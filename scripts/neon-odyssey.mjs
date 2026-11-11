const MODULE_ID = "neon-odyssey";

/* Cryptist Occult Magic: slots by Cryptist level (3 at 7, 4 at 13, 5 at 19). Slot level follows standard Pact Magic. */
const CRYPTIST_SLOTS = [1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5];
const PACT_SLOT_LEVEL = level => level >= 9 ? 5 : Math.ceil(level / 2);

Hooks.once("init", () => {
  const cfg = CONFIG.DND5E;
  cfg.skills.cmp ??= { label: "Computers", ability: "int", fullKey: "computers", icon: "modules/neon-odyssey/icons/neon/i-laptop-code-cyan.webp" };
  cfg.skills.tec ??= { label: "Technology", ability: "int", fullKey: "technology", icon: "modules/neon-odyssey/icons/neon/i-microchip-cyan.webp" };
  CONFIG.DND5E.weaponIds.sniperrifle ??= "Compendium.neon-odyssey.items.Item.WQfmBiZHCdLyIH40";
  const subtypes = cfg.featureTypes?.class?.subtypes;
  if ( subtypes ) Object.assign(subtypes, {
    esotericSecret: "Esoteric Secret",
    psiShaping: "Psi Shaping Option",
    hypertechSchematic: "Hypertech Schematic",
    primalForm: "Primal Form",
    primalAspect: "Primal Aspect"
  });
});

Hooks.on("dnd5e.preparePactSlots", (spells, actor, progression) => {
  if ( !actor?.items ) return;
  const cryptist = actor.items.find(i => (i.type === "class") && (i.system.identifier === "cryptist"));
  if ( !cryptist ) return;
  const level = Math.clamp(progression.pact ?? 0, 0, 20);
  const slot = spells.pact ??= { value: 0 };
  slot.type = "pact";
  slot.label = game.i18n.localize("DND5E.SPELLCASTING.METHODS.Pact.label");
  const override = Number.isNumeric(slot.override) ? Math.max(parseInt(slot.override), 0) : null;
  if ( !level && (override === null) ) return false;
  slot.max = override ?? CRYPTIST_SLOTS[level - 1] ?? 0;
  slot.level = slot.max ? PACT_SLOT_LEVEL(Math.max(level, 1)) : 0;
  slot.value = Math.clamp(slot.value ?? 0, 0, slot.max) || 0;
  return false;
});

Hooks.once("ready", () => console.log(`${MODULE_ID} | Neon Odyssey content ready`));

/* Equipment: Galactic Notes currency and Neon Odyssey weapon properties. */
Hooks.once("init", () => {
  const cfg = CONFIG.DND5E;
  cfg.currencies.gn ??= { label: "Galactic Notes", abbreviation: "$", conversion: 50, icon: "systems/dnd5e/icons/currency/platinum.webp" };
  const props = {
    powered: "Powered", burst: "Burst", braced: "Braced", closeQuarters: "Close Quarters",
    reload: "Reload", scatter: "Scatter", pummel: "Pummel"
  };
  for ( const [key, label] of Object.entries(props) ) {
    cfg.itemProperties[key] ??= { label };
    cfg.validProperties.weapon?.add(key);
  }
});

/* Neon Odyssey languages. */
Hooks.once("init", () => {
  const names = ["Smuggler’s Slang", "Hadalic", "Sideric", "Pixlish", "Dissonant", "Ryliath", "Lyric", "SIGNAL", "Clysmic",
    "Solari", "Promean", "Astronian", "Yaungu", "Boru", "Magmari", "Typhan", "Selash", "Zoic", "Marsoom", "Zeticulan",
    "Oculok", "Navili", "Chroma", "Phytoss", "Shensi", "Sleemese", "Nimboo", "Khora", "Ossik", "Volcar", "Goro", "Yoggoth",
    "Morlith", "Noxilus", "Rosidian", "Kharabis"];
  const children = Object.fromEntries(names.map(n => [n.toLowerCase().replace(/[^a-z0-9]+/g, ""), n]));
  CONFIG.DND5E.languages.neonOdyssey ??= { label: "Neon Odyssey", selectable: false, children };
});

// Cryptist and Esper may use Intelligence or Charisma as their spellcasting ability.
const FLEX_CASTERS = new Set(["cryptist", "esper"]);
Hooks.on("createItem", async (item, options, userId) => {
  if ( (userId !== game.user.id) || (item.type !== "class") || !FLEX_CASTERS.has(item.system.identifier) ) return;
  if ( (item.parent?.type !== "character") || item.getFlag("neon-odyssey", "abilityChosen") ) return;
  const ability = await foundry.applications.api.DialogV2.wait({
    window: { title: `${item.name}: Spellcasting Ability` },
    content: `<p>Choose your ${item.name} spellcasting ability.</p>`,
    buttons: [
      { action: "int", label: CONFIG.DND5E.abilities.int.label },
      { action: "cha", label: CONFIG.DND5E.abilities.cha.label, default: true }
    ],
    rejectClose: false
  }) ?? "cha";
  await item.update({ "system.spellcasting.ability": ability, "flags.neon-odyssey.abilityChosen": true });
});

/* Primeval Cryptist: Shield of the Elements (10 + Con + spellcasting ability, no armor). */
Hooks.once("init", () => {
  CONFIG.DND5E.armorClasses.neonShieldOfElements ??= {
    label: "Shield of the Elements",
    formula: "10 + @abilities.con.mod + @attributes.spell.mod",
    armored: false
  };
});

/* Mutually exclusive effects (e.g. Symmetric Vital/Somber balance): applying one removes the others in its group. */
Hooks.on("createActiveEffect", async (effect, options, userId) => {
  if ( userId !== game.user.id ) return;
  const group = effect.getFlag("neon-odyssey", "exclusive");
  const actor = effect.target ?? (effect.parent instanceof Actor ? effect.parent : null);
  if ( !group || !(actor instanceof Actor) ) return;
  const others = actor.appliedEffects.filter(e => (e.id !== effect.id) && (e.getFlag("neon-odyssey", "exclusive") === group));
  for ( const e of others ) await e.delete();
});

// Galactic Notes are digital credits: they never count toward encumbrance or container weight.
function withoutGalacticNotes(model, fn) {
  const currency = model?.currency;
  const gn = currency?.gn;
  if ( !gn ) return fn();
  currency.gn = 0;
  try { return fn(); } finally { currency.gn = gn; }
}

Hooks.once("init", () => {
  const AF = dnd5e?.dataModels?.actor?.AttributesFields;
  if ( typeof AF?.prepareEncumbrance === "function" ) {
    const original = AF.prepareEncumbrance;
    AF.prepareEncumbrance = function(...args) {
      return withoutGalacticNotes(this, () => original.apply(this, args));
    };
  } else console.warn("neon-odyssey | could not make Galactic Notes weightless for actors");

  const patched = new Set();
  const models = [...Object.values(CONFIG.Item.dataModels ?? {}), ...Object.values(CONFIG.Actor.dataModels ?? {})];
  for ( const model of models ) {
    for ( let proto = model?.prototype; proto && proto !== Object.prototype; proto = Object.getPrototypeOf(proto) ) {
      if ( patched.has(proto) ) continue;
      patched.add(proto);
      const desc = Object.getOwnPropertyDescriptor(proto, "currencyWeight");
      if ( !desc?.get ) continue;
      Object.defineProperty(proto, "currencyWeight", {
        ...desc,
        get() { return withoutGalacticNotes(this, () => desc.get.call(this)); }
      });
    }
  }
});

// Repair item and activity icons that point at dnd5e paths which no longer exist (copies made from older module versions).
const NEON_IMG_FIX = {
  "systems/dnd5e/icons/svg/action/attack.svg": "systems/dnd5e/icons/svg/activity/attack.svg",
  "systems/dnd5e/icons/svg/action/magic.svg": "systems/dnd5e/icons/svg/activity/cast.svg",
  "systems/dnd5e/icons/svg/action/move.svg": "systems/dnd5e/icons/svg/action/dash.svg",
  "systems/dnd5e/icons/svg/action/disengage.svg": "systems/dnd5e/icons/svg/activity/forward.svg",
  "systems/dnd5e/icons/svg/action/restore-use.svg": "systems/dnd5e/icons/svg/activity/heal.svg",
  "systems/dnd5e/icons/svg/action/push.svg": "systems/dnd5e/icons/svg/activity/utility.svg",
  "systems/dnd5e/icons/svg/action/dodge.svg": "systems/dnd5e/icons/svg/activity/utility.svg",
  "icons/magic/unholy/orb-colllecting-energy-green.webp": "icons/magic/unholy/orb-collecting-energy-green.webp",
  "icons/sundries/books/book-embossed-bound-purple.webp": "icons/sundries/books/book-embossed-bound-brown.webp"
};

function neonImageFixes(item) {
  const update = {};
  if ( NEON_IMG_FIX[item.img] ) update.img = NEON_IMG_FIX[item.img];
  for ( const activity of item.system?.activities ?? [] ) {
    if ( NEON_IMG_FIX[activity.img] ) update[`system.activities.${activity.id}.img`] = NEON_IMG_FIX[activity.img];
  }
  return Object.keys(update).length ? { _id: item.id, ...update } : null;
}

Hooks.once("ready", async () => {
  if ( !game.user.isGM ) return;
  let fixed = 0;
  try {
    const worldItems = game.items.map(neonImageFixes).filter(Boolean);
    if ( worldItems.length ) { await Item.updateDocuments(worldItems); fixed += worldItems.length; }
    for ( const actor of game.actors ) {
      const updates = actor.items.map(neonImageFixes).filter(Boolean);
      if ( updates.length ) { await actor.updateEmbeddedDocuments("Item", updates); fixed += updates.length; }
    }
    if ( fixed ) console.log(`neon-odyssey | repaired ${fixed} item icon(s)`);
  } catch (err) {
    console.error("neon-odyssey | icon repair failed", err);
  }
});

/* Resolve "type:identifier" item-uses consumption targets to the actor's real item IDs. */
const NEON_TARGET_REF = /^([a-z]+):([a-z0-9-]+)$/;

function neonTargetUpdates(actor) {
  const updates = [];
  for ( const item of actor.items ) {
    const update = {};
    for ( const activity of item.system.activities ?? [] ) {
      const targets = activity.consumption?.targets ?? [];
      let changed = false;
      const data = targets.map(t => {
        const obj = t.toObject?.() ?? { ...t };
        const m = (obj.type === "itemUses") && NEON_TARGET_REF.exec(obj.target ?? "");
        if ( !m ) return obj;
        const found = actor.items.find(i => (i.type === m[1]) && (i.system.identifier === m[2]));
        if ( !found ) return obj;
        changed = true;
        return { ...obj, target: found.id };
      });
      if ( changed ) update[`system.activities.${activity.id}.consumption.targets`] = data;
    }
    if ( Object.keys(update).length ) updates.push({ _id: item.id, ...update });
  }
  return updates;
}

const neonPendingTargets = new Map();
function neonResolveTargets(actor) {
  if ( !actor || (actor.documentName !== "Actor") || !actor.isOwner ) return;
  clearTimeout(neonPendingTargets.get(actor.uuid));
  neonPendingTargets.set(actor.uuid, setTimeout(async () => {
    neonPendingTargets.delete(actor.uuid);
    const updates = neonTargetUpdates(actor);
    if ( updates.length ) await actor.updateEmbeddedDocuments("Item", updates).catch(err =>
      console.error("neon-odyssey | consumption target repair failed", err));
  }, 300));
}

Hooks.on("createItem", (item, options, userId) => {
  if ( userId === game.user.id ) neonResolveTargets(item.parent);
});
Hooks.on("updateItem", (item, changes, options, userId) => {
  if ( (userId === game.user.id) && foundry.utils.hasProperty(changes, "system.identifier") ) neonResolveTargets(item.parent);
});
Hooks.once("ready", () => {
  if ( !game.user.isGM ) return;
  for ( const actor of game.actors ) neonResolveTargets(actor);
});

/* Surge: one window for the Resistances and every Surge-linked ability the Juggernaut has, then apply them together. */
const SURGE_TYPES = ["bludgeoning", "fire", "lightning", "piercing", "radiant", "slashing"];
const SURGE_LINKS = {
  "call-the-power": [{ name: "Heroic Alter-Ego" }, { name: "Mythic Presence", max: 13 }, { name: "Glorious Presence", min: 14 }],
  "mythic-awakening": [{ name: "Sight Beyond Sight" }],
  "master-of-the-eternal": [{ name: "Eternal Hero" }],
  "rampaging-destruction": [{ name: "Titanic Surge", off: true }]
};
const HEROIC_RESOLVE = { int: "Intelligence", wis: "Wisdom", cha: "Charisma" };
const cap = t => `${t.charAt(0).toUpperCase()}${t.slice(1)}`;

function neonSurgeLinks(actor) {
  const level = actor.classes?.juggernaut?.system.levels ?? 20;
  const links = [];
  for ( const it of actor.items ) {
    for ( const l of SURGE_LINKS[it.system.identifier] ?? [] ) {
      if ( (l.min && (level < l.min)) || (l.max && (level > l.max)) ) continue;
      const effect = it.effects.find(e => e.name === l.name);
      if ( effect ) links.push({ ...l, item: it, effect, key: `link${links.length}` });
    }
  }
  return links;
}

Hooks.on("dnd5e.postUseActivity", async (activity) => {
  const item = activity.item;
  const actor = item?.actor;
  if ( !actor?.isOwner || (item.system.identifier !== "surge") || (activity.type !== "utility") ) return;
  const pickRes = !actor.items.some(i => i.system.identifier === "master-of-the-eternal");
  const awakening = actor.items.find(i => i.system.identifier === "mythic-awakening");
  const links = neonSurgeLinks(actor);
  let content = "";
  if ( pickRes ) content += `<fieldset><legend>Choose 3 Resistances</legend>${SURGE_TYPES.map(t =>
    `<label style="display:block"><input type="checkbox" name="${t}"> ${CONFIG.DND5E.damageTypes[t]?.label ?? t}</label>`).join("")}</fieldset>`;
  if ( awakening ) content += `<fieldset><legend>Heroic Resolve</legend><label>Add your Strength bonus to saves using
    <select name="resolve">${Object.entries(HEROIC_RESOLVE).map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select></label></fieldset>`;
  if ( links.length ) content += `<fieldset><legend>Surge abilities</legend>${links.map(l =>
    `<label style="display:block"><input type="checkbox" name="${l.key}" ${l.off ? "" : "checked"}> ${l.name} <small>(${l.item.name})</small></label>`).join("")}</fieldset>`;
  const chosen = await foundry.applications.api.DialogV2.wait({
    window: { title: "Activate Surge" },
    content,
    buttons: [{ action: "ok", label: "Surge", default: true, callback: (event, button) => {
      const f = button.form.elements;
      return {
        res: pickRes ? SURGE_TYPES.filter(t => f[t]?.checked).slice(0, 3) : [],
        resolve: f.resolve?.value,
        links: links.filter(l => f[l.key]?.checked)
      };
    } }],
    rejectClose: false
  });
  if ( !chosen ) return;
  const toData = (e, src) => {
    const o = e.toObject();
    delete o._id;
    Object.assign(o, { transfer: false, disabled: false, origin: src.uuid });
    foundry.utils.setProperty(o, `flags.${MODULE_ID}.surge`, true);
    return o;
  };
  const names = new Set(["Surge", ...chosen.res.map(t => `Surge Resistance: ${cap(t)}`)]);
  const data = item.effects.filter(e => names.has(e.name)).map(e => toData(e, item));
  for ( const l of chosen.links ) data.push(toData(l.effect, l.item));
  const resolve = awakening?.effects.find(e => e.name === `Heroic Resolve: ${HEROIC_RESOLVE[chosen.resolve]}`);
  if ( resolve ) data.push(toData(resolve, awakening));
  const old = actor.effects.filter(e => e.getFlag(MODULE_ID, "surge")).map(e => e.id);
  if ( old.length ) await actor.deleteEmbeddedDocuments("ActiveEffect", old);
  if ( data.length ) await actor.createEmbeddedDocuments("ActiveEffect", data);
});

/* Auras: Mythic / Glorious Presence and the Enforcer's Zone of Safety give allied tokens in range their bonus. */
const NEON_AURAS = { "Mythic Presence": 10, "Glorious Presence": 30 };
function neonAurasOf(actor) {
  if ( !actor ) return [];
  const out = [];
  const e = actor.effects.find(e => !e.disabled && !e.isSuppressed && NEON_AURAS[e.name] && !e.getFlag(MODULE_ID, "auraFrom"));
  if ( e ) {
    const changes = [{ key: "system.bonuses.abilities.save", type: "add", value: "+1d4", phase: "initial" }];
    if ( e.name === "Glorious Presence" ) {
      const dmg = actor.system.scale?.juggernaut?.["rage-damage"]?.value ?? 0;
      if ( dmg ) for ( const k of ["mwak", "rwak", "msak", "rsak"] ) changes.push({ key: `system.bonuses.${k}.damage`, type: "add", value: `+${dmg}`, phase: "initial" });
    }
    out.push({ kind: "presence", name: e.name, radius: NEON_AURAS[e.name], img: e.img, origin: e.uuid, changes, color: e.name === "Glorious Presence" ? 0xffd23f : 0xff2bd6,
      text: `add 1d4 to saving throws${changes.length > 1 ? " and the Surge Damage bonus to damage rolls" : ""}` });
  }
  const zone = actor.items.find(i => i.system.identifier === "zone-of-safety");
  if ( zone && !actor.statuses?.has("incapacitated") ) {
    const has = id => actor.items.some(i => i.system.identifier === id);
    const bonus = Math.max(1, actor.system.abilities?.cha?.mod ?? 0);
    const changes = [{ key: "system.bonuses.abilities.save", type: "add", value: `+${bonus}`, phase: "initial" }];
    const parts = [`+${bonus} to saving throws`];
    if ( has("fearless-conviction") ) { changes.push({ key: "system.traits.ci.value", type: "add", value: "frightened", phase: "initial" }); parts.push("Immunity to Frightened"); }
    if ( has("harmonic-vigil") ) {
      for ( const t of ["necrotic", "radiant"] ) changes.push({ key: "system.traits.dr.value", type: "add", value: t, phase: "initial" });
      parts.push("Resistance to Necrotic and Radiant");
    }
    out.push({ kind: "zone", name: "Zone of Safety", radius: actor.system.scale?.enforcer?.aura?.value ?? 10, img: zone.img, origin: zone.uuid,
      changes, color: 0x2bf0ff, text: parts.join(", ") });
  }
  return out;
}
function neonTokenGap(a, b, scene) {
  const size = scene.grid.size;
  const gx = Math.max(0, b.x - (a.x + (a.width * size)), a.x - (b.x + (b.width * size)));
  const gy = Math.max(0, b.y - (a.y + (a.height * size)), a.y - (b.y + (b.height * size)));
  return ((Math.max(gx, gy) / size) * scene.grid.distance) + scene.grid.distance;
}
async function neonRefreshAuras(scene) {
  if ( !scene || !game.users.activeGM?.isSelf ) return;
  const sources = scene.tokens.filter(t => t.actor).flatMap(t => neonAurasOf(t.actor).map(a => ({ token: t, ...a })));
  for ( const t of scene.tokens ) {
    const actor = t.actor;
    if ( !actor ) continue;
    const want = {};
    for ( const s of sources ) {
      if ( (s.token === t) || (s.token.actor === actor) || (s.token.disposition !== t.disposition) || (neonTokenGap(s.token, t, scene) > s.radius) ) continue;
      if ( !want[s.kind] || (s.radius > want[s.kind].radius) ) want[s.kind] = s;
    }
    const have = actor.effects.filter(e => e.getFlag(MODULE_ID, "auraFrom"));
    const keep = new Set();
    for ( const e of have ) {
      const w = Object.values(want).find(w => (e.getFlag(MODULE_ID, "auraFrom") === w.token.uuid) && (e.name === `${w.name} (Aura)`)
        && (JSON.stringify(e.system?.changes?.map(c => c.value) ?? []) === JSON.stringify(w.changes.map(c => c.value))));
      if ( w ) keep.add(w);
    }
    const drop = have.filter(e => ![...keep].some(w => (e.getFlag(MODULE_ID, "auraFrom") === w.token.uuid) && (e.name === `${w.name} (Aura)`))).map(e => e.id);
    if ( drop.length ) await actor.deleteEmbeddedDocuments("ActiveEffect", drop.filter(id => actor.effects.has(id))).catch(() => null);
    const add = Object.values(want).filter(w => !keep.has(w)).map(w => ({
      name: `${w.name} (Aura)`, img: w.img, origin: w.origin, type: "base", transfer: false, disabled: false,
      system: { changes: w.changes }, description: `<p>Within ${w.radius} feet of ${w.token.name}: ${w.text}.</p>`,
      flags: { [MODULE_ID]: { auraFrom: w.token.uuid } }
    }));
    if ( add.length ) await actor.createEmbeddedDocuments("ActiveEffect", add).catch(() => null);
  }
}
let neonAuraTimer = null;
let neonAuraScene = null;
let neonAuraBusy = false;
function neonQueueAuras(actor, scene) {
  if ( canvas?.ready ) for ( const t of actor?.getActiveTokens?.() ?? [] ) t.renderFlags?.set({ refreshState: true });
  neonAuraScene = scene ?? game.scenes.viewed ?? game.scenes.active;
  if ( neonAuraTimer ) return;
  neonAuraTimer = setTimeout(async () => {
    neonAuraTimer = null;
    if ( neonAuraBusy ) return neonQueueAuras(null, neonAuraScene);
    neonAuraBusy = true;
    try { await neonRefreshAuras(neonAuraScene); }
    catch(err) { console.error("neon-odyssey | aura refresh failed", err); }
    finally { neonAuraBusy = false; }
  }, 250);
}
Hooks.on("updateToken", (token, changes) => {
  if ( ["x", "y", "width", "height", "disposition"].some(k => k in changes) ) neonQueueAuras(null, token.parent);
});
Hooks.on("createToken", token => neonQueueAuras(null, token.parent));
Hooks.on("deleteToken", token => neonQueueAuras(null, token.parent));
Hooks.on("canvasReady", () => neonQueueAuras());
for ( const h of ["createActiveEffect", "updateActiveEffect", "deleteActiveEffect"] ) Hooks.on(h, effect => {
  if ( effect.getFlag(MODULE_ID, "auraFrom") ) return;
  if ( NEON_AURAS[effect.name] || effect.statuses?.has("incapacitated") ) neonQueueAuras(effect.parent);
});
for ( const h of ["createItem", "deleteItem"] ) Hooks.on(h, item => {
  if ( ["zone-of-safety", "fearless-conviction", "harmonic-vigil"].includes(item.system?.identifier) ) neonQueueAuras(item.parent);
});
Hooks.on("updateActor", (actor, changes) => {
  if ( foundry.utils.hasProperty(changes, "system.abilities.cha") && actor.items.some(i => i.system.identifier === "zone-of-safety") ) neonQueueAuras(actor);
});
Hooks.on("refreshToken", token => {
  const auras = neonAurasOf(token.actor);
  let g = token.neonAura;
  if ( !auras.length ) { if ( g ) g.visible = false; return; }
  if ( !g || g.destroyed ) g = token.neonAura = token.addChildAt(new PIXI.Graphics(), 0);
  g.clear();
  for ( const aura of auras ) {
    const r = (aura.radius / canvas.grid.distance) * canvas.grid.size;
    g.lineStyle(3, aura.color, 0.9).beginFill(aura.color, 0.06).drawRoundedRect(-r, -r, token.w + (2 * r), token.h + (2 * r), r / 2).endFill();
  }
  g.visible = true;
});

/* Cyberguard Full-System Upgrade: add every Tactical Cybernetics implant the Enforcer doesn't already have. */
Hooks.on("createItem", async (item, options, userId) => {
  const actor = item.parent;
  if ( (userId !== game.user.id) || (item.system?.identifier !== "full-system-upgrade") || !actor ) return;
  const pack = game.packs.get(`${MODULE_ID}.features`);
  const index = await pack.getIndex({ fields: ["system.identifier"] });
  const owned = new Set(actor.items.map(i => i.system.identifier));
  const missing = index.filter(e => e.system?.identifier?.startsWith("implant-") && !owned.has(e.system.identifier));
  const docs = await Promise.all(missing.map(e => pack.getDocument(e._id)));
  if ( docs.length ) await actor.createEmbeddedDocuments("Item", docs.map(d => game.items.fromCompendium(d)));
});

/* Neon Odyssey tools from the book. Core keys with a Neon equivalent point to the Neon item so existing grants show the book name. */
Hooks.once("init", () => {
  const tools = CONFIG.DND5E.tools;
  const I = `Compendium.${MODULE_ID}.items.Item.`;
  const NEON_TOOLS = {
    painter: ["dex", "469Ci9cfRjPurGvA"], brewer: ["int", "57DVSNEEAzuy0P30"], cook: ["wis", "ec86miJotQkOIlaj"],
    alchemist: ["int", "yTNGm8Mlp1gckpKP"], mason: ["str", "ir4TscEIA7h7YHBG"], electronics: ["dex", "QtEnNlpK8ltfZ9gd"],
    engineer: ["dex", "33sXsmnMQakxMFCD"], jeweler: ["int", "znvghkskhrqYeiUe"], mechanic: ["str", "ls9En7asIx46b5et"],
    polymer: ["int", "AaNTKKWGQo5EPgXF"], surveying: ["wis", "WmVo3QzG4etjXFNi"], weaver: ["dex", "mhsFOJedTzJLibht"],
    bypass: ["dex", "7uvYP4Hpk5NqzkQB"], forg: ["dex", "8yxOAgALwDE6AMmB"], gameset: ["dex", "OuSBOtZopTjQZpLI"],
    disg: ["cha", "zc9lxJDbkrn3oAq8"], instrument: ["cha", "QvMKgjq1gOIunojJ"], navg: ["wis", "uBf4FF5qHapyAgXz"],
    herb: ["int", "3L3ZSmaDIPpkc9HJ"], spiking: ["int", "Rt7adqDDyIE4taqD"], pois: ["int", "BtfnXgHN6AsXeJVt"]
  };
  for ( const [key, [ability, id]] of Object.entries(NEON_TOOLS) ) tools[key] = { ...(tools[key] ?? {}), ability, id: `${I}${id}` };
});
function neonMalwareStatus() {
  if ( CONFIG.statusEffects.some(s => s.id === "malware") ) return;
  CONFIG.statusEffects.push({ id: "malware", name: "Malware", img: `modules/${MODULE_ID}/icons/neon/s-biohazard-lime.webp`, _id: "neonmalware00000" });
}
Hooks.once("setup", neonMalwareStatus);
Hooks.once("ready", neonMalwareStatus);

/* Virus Malware: -1d6 on the next D20 Test (works for NPCs too), then the status is removed after that roll. */
const neonMalwareActor = subject => subject instanceof Actor ? subject : subject?.actor;
Hooks.on("dnd5e.preRollD20TestV2", config => {
  const actor = neonMalwareActor(config?.subject);
  if ( !actor?.statuses?.has("malware") ) return;
  config.rolls ??= [{}];
  const roll = config.rolls[0] ??= {};
  roll.parts = [...(roll.parts ?? []), "-1d6"];
});
for ( const name of ["AbilityCheck", "SavingThrow", "Skill", "ToolCheck", "Attack", "Concentration"] ) {
  Hooks.on(`dnd5e.roll${name}`, (rolls, data) => {
    const actor = neonMalwareActor(data?.subject);
    if ( !actor?.isOwner ) return;
    const ids = actor.effects.filter(e => e.statuses?.has("malware")).map(e => e.id);
    if ( ids.length ) actor.deleteEmbeddedDocuments("ActiveEffect", ids).catch(() => null);
  });
}

/* Gorgonite Gorgon's Gaze: choose the save DC ability when the trait is added. */
Hooks.on("createItem", async (item, options, userId) => {
  if ( (userId !== game.user.id) || (item.system?.identifier !== "gorgons-gaze") || (item.parent?.type !== "character") ) return;
  if ( item.getFlag(MODULE_ID, "abilityChosen") ) return;
  const A = CONFIG.DND5E.abilities;
  const ability = await foundry.applications.api.DialogV2.wait({
    window: { title: "Gorgon's Gaze: Save DC" },
    content: "<p>Choose the ability used for your Gorgon's Gaze save DC (8 + Proficiency Bonus + modifier).</p>",
    buttons: [
      { action: "int", label: A.int.label },
      { action: "wis", label: A.wis.label },
      { action: "cha", label: A.cha.label, default: true }
    ],
    rejectClose: false
  }) ?? "cha";
  const update = { [`flags.${MODULE_ID}.abilityChosen`]: true };
  for ( const a of item.system.activities ) if ( a.type === "save" ) update[`system.activities.${a.id}.save.dc.calculation`] = ability;
  await item.update(update);
});

/* Gorgonite Toxin Resistant: Advantage on Constitution saves while Poisoned (saves to end it). */
async function neonToxinAdvantage(effect, removed) {
  if ( !effect.statuses?.has("poisoned") ) return;
  const actor = effect.parent instanceof Actor ? effect.parent : effect.parent?.parent;
  const toggle = actor?.items.find(i => i.system.identifier === "toxin-resistant")?.effects.find(e => e.name === "Toxin Resistant: Advantage vs Poisoned");
  if ( !toggle ) return;
  const poisoned = actor.effects.some(e => (!removed || (e.id !== effect.id)) && e.statuses?.has("poisoned"));
  if ( toggle.disabled === poisoned ) await toggle.update({ disabled: !poisoned });
}
Hooks.on("createActiveEffect", (effect, options, userId) => { if ( userId === game.user.id ) neonToxinAdvantage(effect, false); });
Hooks.on("deleteActiveEffect", (effect, options, userId) => { if ( userId === game.user.id ) neonToxinAdvantage(effect, true); });

/* ---------------- Vehicles ---------------- */
const NEON_VEHICLE_CLASSES = {
  lightPlanetary: "Light Planetary", heavyPlanetary: "Heavy Planetary", lightMech: "Light Mech", standardMech: "Standard Mech",
  heavyMech: "Heavy Mech", lightStarfighter: "Light Starfighter", standardStarfighter: "Standard Starfighter",
  heavyStarfighter: "Heavy Starfighter", lightTransport: "Light Transport", heavyTransport: "Heavy Transport", capitalShip: "Capital Ship"
};
Hooks.once("init", () => Object.assign(CONFIG.DND5E.vehicleTypes, NEON_VEHICLE_CLASSES));

/* Crew: the first crew member's PB is added to vehicle weapon attacks; also to saves and initiative if proficient with the vehicle class. */
async function neonVehicleCrew(vehicle) {
  if ( (vehicle?.type !== "vehicle") || !vehicle.isOwner ) return;
  const uuids = vehicle.system.crew?.value ?? [];
  const driver = uuids.length ? await fromUuid(uuids[0]).catch(() => null) : null;
  const pb = driver?.system?.attributes?.prof ?? 0;
  const cls = vehicle.getFlag(MODULE_ID, "vehicleClass");
  const tools = driver?.system?.tools ?? {};
  const proficient = !!driver && Object.entries(tools).some(([k, t]) => (t.value >= 1) && ((k === cls) || (k === vehicle.system.details?.type)));
  const driverPB = proficient ? pb : 0;
  const flags = vehicle.flags?.[MODULE_ID] ?? {};
  if ( (flags.crewPB !== pb) || (flags.driverPB !== driverPB) || (flags.driver !== (driver?.name ?? "")) ) {
    await vehicle.update({ [`flags.${MODULE_ID}.crewPB`]: pb, [`flags.${MODULE_ID}.driverPB`]: driverPB, [`flags.${MODULE_ID}.driver`]: driver?.name ?? "" });
  }
  const changes = driverPB ? [
    ...["str", "dex", "con"].map(a => ({ key: `system.abilities.${a}.bonuses.save`, type: "add", value: String(driverPB), phase: "initial" })),
    { key: "system.attributes.init.bonus", type: "add", value: String(driverPB), phase: "initial" }
  ] : [{ key: "system.attributes.init.bonus", type: "add", value: String(pb), phase: "initial" }];
  const existing = vehicle.effects.find(e => e.getFlag(MODULE_ID, "crewEffect"));
  const name = driver ? `Crew: ${driver.name} (PB +${pb}${driverPB ? ", proficient" : ""})` : "Crew: none";
  if ( existing ) { if ( existing.name !== name ) await existing.update({ name, "system.changes": changes }); }
  else await vehicle.createEmbeddedDocuments("ActiveEffect", [{ name, img: "icons/svg/wing.svg", type: "base", system: { changes }, flags: { [MODULE_ID]: { crewEffect: true } } }]);
}
Hooks.on("updateActor", (actor, changes, options, userId) => {
  if ( (userId === game.user.id) && (actor.type === "vehicle") && foundry.utils.hasProperty(changes, "system.crew") ) neonVehicleCrew(actor);
});
Hooks.once("ready", () => { if ( game.user.isGM ) for ( const a of game.actors.filter(a => a.type === "vehicle") ) neonVehicleCrew(a); });

/* Damage Threshold, Shield Points (= Temp HP, with their own threshold) and Mishaps. */
const NEON_MISHAPS = [
  [1, 1, "Fire", "A fire breaks out in the engine. A creature that starts its turn in or on the vehicle takes 11 (2d10) Fire damage.", "15 (Dex)", []],
  [2, 4, "Frozen Steering", "The vehicle can’t turn. It automatically fails vehicle Dexterity checks and saves until repaired.", "15 (Str)", [["system.abilities.dex.check.roll.mode", "-1"], ["system.abilities.dex.save.roll.mode", "-1"]]],
  [5, 7, "Power Drain", "The vehicle gains 1 Exhaustion level (−2 to its D20 Tests per level; at 6 it breaks down).", "Repair Parts (DC 15 Int (Technology), 1 hour)", "exhaustion"],
  [8, 10, "Weapon Malfunction", "One of the vehicle’s weapons (random) is disabled until repaired.", "20 (Str)", []],
  [11, 13, "Sharp Veer", "The driver must take an action at the start of each of its turns to hold course, or the vehicle swerves 45° and moves ¼ of its last Speed that way.", "15 (Dex)", []],
  [14, 16, "Buckled Frame", "The vehicle’s Damage Threshold is reduced by 10 until repaired.", "15 (Str)", [["system.attributes.hp.dt", "-10"]]],
  [17, 19, "Damaged Drive", "Disadvantage on vehicle Dexterity checks; riders have Disadvantage on ability checks and attack rolls.", "20 (Dex)", [["system.abilities.dex.check.roll.mode", "-1"]]],
  [20, 20, "Roll Over", "The vehicle rolls, is Prone and stops. Riders inside are Prone and take 11 (2d10) Bludgeoning; riders outside make a DC 20 Str save or are thrown 30 ft and Prone.", "—", "prone"]
];
const neonPendingMishap = new WeakMap();
Hooks.on("dnd5e.preApplyDamage", (actor, amount, updates, options) => {
  if ( actor?.type !== "vehicle" ) return;
  const hp = actor.system.attributes.hp;
  if ( (amount > 0) && hp.dt && (amount < hp.dt) ) {
    ui.notifications?.info(`${actor.name}: ${amount} damage doesn’t beat its Damage Threshold (${hp.dt}).`);
    return false;
  }
  const after = updates["system.attributes.hp.value"] ?? hp.value;
  const loss = hp.value - after;
  const half = Math.floor(hp.max / 2);
  if ( (loss > 0) && (after > 0) && ((hp.mt && (loss >= hp.mt)) || ((hp.value > half) && (after <= half))) ) neonPendingMishap.set(actor, true);
});
Hooks.on("dnd5e.applyDamage", async (actor, amount) => {
  if ( !neonPendingMishap.get(actor) ) return;
  neonPendingMishap.delete(actor);
  if ( !game.users.activeGM?.isSelf && !actor.isOwner ) return;
  const roll = await new Roll("1d20").evaluate();
  const [, , name, text, dc, fx] = NEON_MISHAPS.find(([lo, hi]) => (roll.total >= lo) && (roll.total <= hi));
  await roll.toMessage({ speaker: ChatMessage.getSpeaker({ actor }), flavor: `<strong>${actor.name}: Vehicle Mishap — ${name}</strong><br>${text}<br><em>Repair DC: ${dc}</em>` });
  const data = { name: `Mishap: ${name}`, img: "icons/svg/hazard.svg", type: "base", description: `<p>${text}</p><p>Repair DC: ${dc}. Delete this effect when repaired.</p>`, system: { changes: [] }, flags: { [MODULE_ID]: { mishap: name } } };
  if ( Array.isArray(fx) ) data.system.changes = fx.map(([key, value]) => ({ key, value, type: "add", phase: "initial" }));
  else if ( fx === "prone" ) data.statuses = ["prone"];
  else if ( fx === "exhaustion" ) {
    const level = actor.effects.filter(e => e.getFlag(MODULE_ID, "mishap") === "Power Drain").length + 1;
    data.name = `Vehicle Exhaustion ${level}`;
    data.system.changes = ["str", "dex", "con", "int", "wis", "cha"].flatMap(a => ["check", "save"].map(t => ({ key: `system.abilities.${a}.bonuses.${t}`, value: "-2", type: "add", phase: "initial" })));
    if ( level >= 6 ) await actor.update({ "system.attributes.hp.value": 0 });
  }
  await actor.createEmbeddedDocuments("ActiveEffect", [data]);
});
