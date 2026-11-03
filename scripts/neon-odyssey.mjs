const MODULE_ID = "neon-odyssey";

/* Cryptist Occult Magic: slots by Cryptist level (3 at 7, 4 at 13, 5 at 19). Slot level follows standard Pact Magic. */
const CRYPTIST_SLOTS = [1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5];
const PACT_SLOT_LEVEL = level => level >= 9 ? 5 : Math.ceil(level / 2);

Hooks.once("init", () => {
  const cfg = CONFIG.DND5E;
  cfg.skills.cmp ??= { label: "Computers", ability: "int", fullKey: "computers", icon: "icons/svg/terminal.svg" };
  cfg.skills.tec ??= { label: "Technology", ability: "int", fullKey: "technology", icon: "icons/svg/circuit.svg" };
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
