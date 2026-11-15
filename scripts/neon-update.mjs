/* Neon Odyssey: refresh a character's Neon items from the module compendiums, keeping levels, choices and spent uses. */
const NEON_ID = "neon-odyssey";
const NEON_ITEM_PACKS = ["classes", "features", "origins", "spells", "items"];
const UNIQUE_TYPES = new Set(["class", "subclass", "race", "background"]);
const PHYSICAL_KEEP = ["quantity", "equipped", "attuned", "attunement", "container", "identified", "weight"];

async function neonSourceFor(item) {
  const src = item._stats?.compendiumSource ?? item.flags?.dnd5e?.sourceId ?? item.flags?.core?.sourceId;
  if ( src?.startsWith(`Compendium.${NEON_ID}.`) ) return fromUuid(src);
  if ( src || !UNIQUE_TYPES.has(item.type) || !item.system.identifier ) return null;
  for ( const name of NEON_ITEM_PACKS ) {
    const pack = game.packs.get(`${NEON_ID}.${name}`);
    const index = await pack?.getIndex({ fields: ["system.identifier"] });
    const entry = index?.find(e => (e.type === item.type) && (e.system?.identifier === item.system.identifier));
    if ( entry ) return pack.getDocument(entry._id);
  }
  return null;
}

function neonMergeSystem(item, fresh) {
  const sys = fresh.toObject().system;
  const old = item.toObject().system;
  if ( old.uses && sys.uses ) sys.uses.spent = old.uses.spent ?? 0;
  for ( const [id, act] of Object.entries(sys.activities ?? {}) ) {
    const prev = old.activities?.[id];
    if ( prev?.uses && act.uses ) act.uses.spent = prev.uses.spent ?? 0;
  }
  if ( sys.advancement ) {
    const prev = new Map(Object.entries(old.advancement ?? {}).map(([k, a]) => [a._id ?? k, a]));
    for ( const [k, adv] of Object.entries(sys.advancement) ) {
      const p = prev.get(adv._id ?? k);
      if ( p ) adv.value = p.value ?? adv.value;
    }
  }
  if ( item.type === "class" ) {
    sys.levels = old.levels;
    if ( old.hd ) sys.hd = { ...sys.hd, spent: old.hd.spent ?? 0 };
    if ( old.spellcasting?.ability ) sys.spellcasting = { ...sys.spellcasting, ability: old.spellcasting.ability };
  }
  if ( item.type === "spell" ) for ( const k of ["prepared", "method", "sourceClass"] ) if ( k in old ) sys[k] = old[k];
  for ( const k of PHYSICAL_KEEP ) if ( (k in old) && (k in sys) ) sys[k] = old[k];
  return sys;
}

async function neonSyncEffects(item, fresh) {
  const freshEffects = fresh.effects.map(e => e.toObject());
  const freshIds = new Set(freshEffects.map(e => e._id));
  const remove = item.effects.filter(e => !freshIds.has(e.id)).map(e => e.id);
  if ( remove.length ) await item.deleteEmbeddedDocuments("ActiveEffect", remove);
  const update = []; const create = [];
  for ( const e of freshEffects ) {
    const existing = item.effects.get(e._id);
    if ( existing ) update.push({ ...e, disabled: existing.disabled });
    else create.push(e);
  }
  if ( update.length ) await item.updateEmbeddedDocuments("ActiveEffect", update, { recursive: false, diff: false });
  if ( create.length ) await item.createEmbeddedDocuments("ActiveEffect", create, { keepId: true });
}

async function neonGrantMissing(actor, item) {
  const level = item.type === "class" ? item.system.levels : (item.class?.system.levels ?? 0);
  const owned = new Set(actor.items.map(i => i._stats?.compendiumSource ?? i.flags?.dnd5e?.sourceId).filter(Boolean));
  const added = [];
  const advancement = item.toObject().system.advancement ?? {};
  for ( const [key, adv] of Object.entries(advancement) ) {
    adv._id ??= key;
    if ( (adv.type !== "ItemGrant") || ((adv.level ?? 0) > level) ) continue;
    const live = Object.entries(adv.value?.added ?? {}).filter(([id]) => actor.items.has(id));
    const already = new Set(live.map(([, uuid]) => uuid));
    for ( const { uuid, optional } of adv.configuration?.items ?? [] ) {
      if ( optional || owned.has(uuid) || already.has(uuid) ) continue;
      const doc = await fromUuid(uuid);
      if ( !doc ) continue;
      const data = doc.toObject();
      foundry.utils.setProperty(data, "_stats.compendiumSource", uuid);
      foundry.utils.setProperty(data, "flags.dnd5e.sourceId", uuid);
      foundry.utils.setProperty(data, "flags.dnd5e.advancementOrigin", `${item.id}.${adv._id}`);
      if ( data.type === "spell" ) {
        const cls = item.type === "class" ? item.system.identifier : item.system.classIdentifier;
        Object.assign(data.system, { sourceClass: cls ?? data.system.sourceClass, method: "spell", prepared: 2 });
      }
      const [created] = await actor.createEmbeddedDocuments("Item", [data]);
      if ( !created ) continue;
      adv.value = adv.value ?? {}; adv.value.added = { ...Object.fromEntries(live), [created.id]: uuid };
      live.push([created.id, uuid]);
      owned.add(uuid); added.push(created.name);
    }
  }
  if ( added.length ) await item.update({ "system.advancement": advancement });
  return added;
}

export async function neonUpdateActor(actor, { notify = true } = {}) {
  const refreshed = []; const added = [];
  const items = actor.items.filter(i => !i.flags?.dnd5e?.cachedFor);
  for ( const item of items ) {
    const fresh = await neonSourceFor(item);
    if ( !fresh || (fresh.type !== item.type) ) continue;
    const flags = foundry.utils.mergeObject(fresh.toObject().flags ?? {}, item.toObject().flags ?? {}, { inplace: false });
    await item.update({ name: fresh.name, img: fresh.img, system: neonMergeSystem(item, fresh), flags }, { recursive: false, diff: false });
    await neonSyncEffects(item, fresh);
    refreshed.push(item.name);
  }
  for ( const item of actor.items.filter(i => ["class", "subclass"].includes(i.type)) ) added.push(...await neonGrantMissing(actor, item));
  if ( notify ) ui.notifications.info(`Neon Odyssey: updated ${refreshed.length} item(s) on ${actor.name}${added.length ? `, added ${added.join(", ")}` : ""}.`);
  return { refreshed, added };
}

async function neonConfirmUpdate(actor) {
  const ok = await foundry.applications.api.DialogV2.confirm({
    window: { title: "Update from Compendium" },
    content: `<p>Refresh <strong>${foundry.utils.escapeHTML(actor.name)}</strong>'s Neon Odyssey classes, subclasses, features, species, spells and gear from the latest module version?</p>
      <p>Levels, choices and spent uses are kept, and missing features for the current level are added. Edits you made to those items' text or activities are replaced.</p>`,
    rejectClose: false
  });
  if ( ok ) return neonUpdateActor(actor);
}

Hooks.on("getHeaderControlsActorSheetV2", (app, controls) => {
  const actor = app.document;
  if ( !["character", "npc"].includes(actor?.type) || !actor.isOwner ) return;
  if ( controls.some(c => c.action === "neonUpdateFromCompendium") ) return;
  controls.push({ action: "neonUpdateFromCompendium", icon: "fa-solid fa-arrows-rotate", label: "Update from Compendium", ownership: "OWNER", onClick: () => neonConfirmUpdate(actor) });
});

Hooks.once("init", () => {
  const mod = game.modules.get(NEON_ID);
  mod.api = { ...(mod.api ?? {}), updateActor: neonUpdateActor };
});
