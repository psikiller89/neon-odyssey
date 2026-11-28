// Neon Odyssey GM tools: Encounter Builder, Loot Generator and Shop Generator.
const NEON_GM = "neon-odyssey";
const CR_XP = { 0: 10, 0.125: 25, 0.25: 50, 0.5: 100, 1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800, 6: 2300, 7: 2900, 8: 3900,
  9: 5000, 10: 5900, 11: 7200, 12: 8400, 13: 10000, 14: 11500, 15: 13000, 16: 15000, 17: 18000, 18: 20000, 19: 22000,
  20: 25000, 21: 33000, 22: 41000, 23: 50000, 24: 62000, 25: 75000, 26: 90000, 27: 105000, 28: 120000, 29: 135000, 30: 155000 };
// 2024 Dungeon Master's Guide XP budget per character: [Low, Moderate, High]
const XP_BUDGET = [null, [50, 75, 100], [100, 150, 200], [150, 225, 400], [250, 375, 500], [500, 750, 1100], [600, 1000, 1400],
  [750, 1300, 1700], [1000, 1700, 2100], [1300, 2000, 2600], [1600, 2300, 3100], [1900, 2900, 4100], [2200, 3700, 4700],
  [2600, 4200, 5400], [2900, 4900, 6200], [3300, 5400, 7800], [3800, 6100, 9800], [4500, 7200, 11700], [5000, 8700, 14200],
  [5500, 10700, 17200], [6400, 13200, 22000]];
const DIFFS = ["Low", "Moderate", "High"];
const esc = s => foundry.utils.escapeHTML(String(s ?? ""));
const crXP = cr => CR_XP[cr] ?? CR_XP[Math.min(30, Math.round(cr))] ?? 0;
const crLabel = cr => ({ 0.125: "1/8", 0.25: "1/4", 0.5: "1/2" })[cr] ?? String(cr);
const gn = n => `${Number(n).toLocaleString()} GN`;
const pick = arr => arr[Math.floor(Math.random() * arr.length)];

function neonParty() {
  let chars = game.users.filter(u => !u.isGM && u.character).map(u => u.character);
  if ( !chars.length ) chars = game.actors.filter(a => a.type === "character" && a.hasPlayerOwner);
  const lv = chars.map(a => a.system.details?.level || 1);
  return { size: chars.length || 4, level: lv.length ? Math.round(lv.reduce((a, b) => a + b, 0) / lv.length) : 1 };
}

async function neonMonsterIndex(packIds) {
  const out = [];
  for ( const id of packIds ) {
    const pack = game.packs.get(id);
    if ( !pack ) continue;
    const index = await pack.getIndex({ fields: ["system.details.cr", "system.details.type.value", "type", "img", "folder"] });
    const skip = new Set(pack.folders.filter(f => /summon|vehicle/i.test(f.name)).map(f => f.id));
    for ( const e of index ) {
      if ( e.type !== "npc" || skip.has(e.folder) ) continue;
      const cr = Number(foundry.utils.getProperty(e, "system.details.cr"));
      if ( !Number.isFinite(cr) ) continue;
      out.push({ uuid: e.uuid ?? `Compendium.${id}.Actor.${e._id}`, name: e.name, img: e.img, cr, xp: crXP(cr),
        ctype: foundry.utils.getProperty(e, "system.details.type.value") || "", source: pack.metadata.label });
    }
  }
  return out;
}

function neonMonsterPacks() {
  return game.packs.filter(p => p.documentName === "Actor" && p.index.some?.(e => e.type === "npc") !== false)
    .filter(p => !/hero|starter/i.test(p.metadata.label))
    .map(p => ({ id: p.collection, label: p.metadata.label,
      on: p.collection === `${NEON_GM}.bestiary` || ["dnd5e.monsters", "dnd5e.actors24"].includes(p.collection) }));
}

export function neonGenerateEncounter(pool, { size, level, difficulty, maxCount = 6, maxCR }) {
  const budget = size * (XP_BUDGET[Math.clamp(level, 1, 20)]?.[difficulty] ?? 0);
  maxCR ??= level + [0, 2, 3][difficulty];
  const cands = pool.filter(m => m.cr <= maxCR && m.xp <= budget);
  const list = [];
  let spent = 0, count = 0;
  for ( let guard = 0; guard < 50 && count < maxCount; guard++ ) {
    const left = budget - spent;
    const floor = count ? 0 : left * 0.15;
    const ok = cands.filter(m => m.xp <= left && m.xp >= floor);
    if ( !ok.length ) break;
    const m = pick(ok);
    const n = Math.max(1, Math.min(maxCount - count, Math.floor(left / m.xp), 1 + Math.floor(Math.random() * 4)));
    const row = list.find(r => r.uuid === m.uuid);
    if ( row ) row.count += n; else list.push({ ...m, count: n });
    spent += n * m.xp; count += n;
    if ( spent >= budget * 0.9 ) break;
  }
  return { budget, list };
}

async function neonPlaceEncounter(list, { hidden = true, combat = true } = {}) {
  if ( !canvas.scene ) return ui.notifications.warn("Open a scene first.");
  let folder = game.folders.find(f => f.type === "Actor" && f.name === "Neon Encounters");
  folder ??= await Folder.create({ name: "Neon Encounters", type: "Actor", color: "#c026d3" });
  const grid = canvas.grid.size;
  const { x: cx, y: cy } = canvas.stage.pivot;
  const docs = [];
  let i = 0;
  for ( const row of list ) {
    let actor = game.actors.find(a => a._stats?.compendiumSource === row.uuid);
    if ( !actor ) {
      const src = await fromUuid(row.uuid);
      if ( !src ) continue;
      actor = await Actor.implementation.create({ ...game.actors.fromCompendium(src), folder: folder.id });
    }
    for ( let n = 0; n < row.count; n++, i++ ) {
      const w = actor.prototypeToken.width || 1;
      const col = i % 4, line = Math.floor(i / 4);
      const td = await actor.getTokenDocument({ x: cx + (col - 2) * grid * Math.max(w, 1.5), y: cy + line * grid * Math.max(w, 1.5), hidden });
      docs.push(td.toObject());
    }
  }
  const tokens = await canvas.scene.createEmbeddedDocuments("Token", docs);
  if ( combat && tokens.length ) {
    const c = game.combats.find(c => c.scene?.id === canvas.scene.id) ?? await Combat.implementation.create({ scene: canvas.scene.id, active: true });
    await c.createEmbeddedDocuments("Combatant", tokens.map(t => ({ tokenId: t.id, sceneId: canvas.scene.id, actorId: t.actorId, hidden: t.hidden })));
  }
  ui.notifications.info(`Placed ${tokens.length} creatures on ${canvas.scene.name}.`);
  return tokens;
}

class NeonEncounterBuilder extends foundry.applications.api.ApplicationV2 {
  static DEFAULT_OPTIONS = { id: "neon-encounter-builder", classes: ["neon-gm-tool"], window: { title: "Neon Encounter Builder", icon: "fa-solid fa-skull", resizable: true }, position: { width: 620, height: 720 } };
  state = { ...neonParty(), difficulty: 1, maxCount: 6, ctype: "", packs: neonMonsterPacks(), list: [], budget: 0, pool: null, hidden: true, combat: true };

  async _prepPool() {
    this.state.pool = await neonMonsterIndex(this.state.packs.filter(p => p.on).map(p => p.id));
  }
  get pool() { return (this.state.pool ?? []).filter(m => !this.state.ctype || m.ctype === this.state.ctype); }
  _budget() { const s = this.state; return s.size * (XP_BUDGET[Math.clamp(s.level, 1, 20)]?.[s.difficulty] ?? 0); }

  async _renderHTML() {
    if ( !this.state.pool ) await this._prepPool();
    const s = this.state, budget = this._budget();
    const total = s.list.reduce((t, r) => t + r.xp * r.count, 0);
    const color = total > budget * 1.1 ? "#f87171" : total >= budget * 0.75 ? "#4ade80" : "#facc15";
    const types = Object.entries(CONFIG.DND5E.creatureTypes).map(([k, v]) => `<option value="${k}" ${s.ctype === k ? "selected" : ""}>${esc(v.label ?? v)}</option>`).join("");
    const names = [...new Set(this.pool.map(m => m.name))].sort().map(n => `<option value="${esc(n)}">`).join("");
    const rows = s.list.map((r, i) => `<tr><td><img src="${esc(r.img)}" width="28" height="28" style="border:none"></td>
      <td><a class="neon-open" data-uuid="${esc(r.uuid)}">${esc(r.name)}</a><br><small>${esc(r.source)}</small></td><td>${crLabel(r.cr)}</td><td>${r.xp.toLocaleString()}</td>
      <td style="white-space:nowrap"><button type="button" data-act="dec" data-i="${i}">−</button> ${r.count} <button type="button" data-act="inc" data-i="${i}">+</button></td>
      <td><button type="button" data-act="del" data-i="${i}"><i class="fa-solid fa-trash"></i></button></td></tr>`).join("");
    return `<form class="neon-eb" style="display:flex;flex-direction:column;gap:6px">
      <div class="form-group"><label>Party size</label><input type="number" name="size" min="1" max="12" value="${s.size}">
        <label>Average level</label><input type="number" name="level" min="1" max="20" value="${s.level}"></div>
      <div class="form-group"><label>Difficulty</label><select name="difficulty">${DIFFS.map((d, i) => `<option value="${i}" ${i === s.difficulty ? "selected" : ""}>${d}</option>`).join("")}</select>
        <label>Max creatures</label><input type="number" name="maxCount" min="1" max="20" value="${s.maxCount}"></div>
      <div class="form-group"><label>Creature type</label><select name="ctype"><option value="">Any</option>${types}</select></div>
      <fieldset><legend>Monster sources</legend>${s.packs.map((p, i) => `<label style="display:inline-block;margin-right:10px"><input type="checkbox" data-pack="${i}" ${p.on ? "checked" : ""}> ${esc(p.label)}</label>`).join("")}
        <p class="hint">${this.pool.length} monsters available.</p></fieldset>
      <div style="display:flex;gap:6px"><button type="button" data-act="gen"><i class="fa-solid fa-dice"></i> Generate</button>
        <input list="neon-eb-names" name="addName" placeholder="Add a monster by name"><datalist id="neon-eb-names">${names}</datalist>
        <button type="button" data-act="add"><i class="fa-solid fa-plus"></i> Add</button></div>
      <p><b>XP:</b> <span style="color:${color}">${total.toLocaleString()}</span> / ${budget.toLocaleString()} (${DIFFS[s.difficulty]} budget)</p>
      <table><thead><tr><th></th><th>Monster</th><th>CR</th><th>XP</th><th>Count</th><th></th></tr></thead><tbody>${rows || `<tr><td colspan="6">Click Generate or add monsters.</td></tr>`}</tbody></table>
      <div style="display:flex;gap:10px;align-items:center"><label><input type="checkbox" name="hidden" ${s.hidden ? "checked" : ""}> Hidden tokens</label>
        <label><input type="checkbox" name="combat" ${s.combat ? "checked" : ""}> Add to combat</label>
        <button type="button" data-act="place" ${s.list.length ? "" : "disabled"}><i class="fa-solid fa-map-location-dot"></i> Place on Scene</button></div>
    </form>`;
  }

  _replaceHTML(result, content) {
    content.innerHTML = result;
    const form = content.querySelector("form");
    form.addEventListener("change", async ev => {
      const t = ev.target;
      if ( t.dataset.pack !== undefined ) { this.state.packs[t.dataset.pack].on = t.checked; this.state.pool = null; return this.render(); }
      if ( t.name === "addName" ) return;
      if ( ["hidden", "combat"].includes(t.name) ) { this.state[t.name] = t.checked; return; }
      if ( t.name ) this.state[t.name] = t.type === "number" || t.name === "difficulty" ? Number(t.value) : t.value;
      this.render();
    });
    form.addEventListener("click", async ev => {
      const open = ev.target.closest(".neon-open");
      if ( open ) return (await fromUuid(open.dataset.uuid))?.sheet.render(true);
      const b = ev.target.closest("button[data-act]");
      if ( !b ) return;
      const s = this.state, i = Number(b.dataset.i);
      switch ( b.dataset.act ) {
        case "gen": Object.assign(s, neonGenerateEncounter(this.pool, s)); break;
        case "inc": s.list[i].count++; break;
        case "dec": if ( --s.list[i].count < 1 ) s.list.splice(i, 1); break;
        case "del": s.list.splice(i, 1); break;
        case "add": {
          const name = form.querySelector("[name=addName]").value.trim();
          const m = this.pool.find(m => m.name === name);
          if ( !m ) return ui.notifications.warn(`No monster named "${name}" in the chosen sources.`);
          const row = s.list.find(r => r.uuid === m.uuid);
          if ( row ) row.count++; else s.list.push({ ...m, count: 1 });
          break;
        }
        case "place": await neonPlaceEncounter(s.list, s); return;
      }
      this.render();
    });
  }
}

async function neonItemIndex() {
  const pack = game.packs.get(`${NEON_GM}.items`);
  const idx = await pack.getIndex({ fields: ["system.price", "folder", "type"] });
  const fold = id => pack.folders.get(id);
  const topName = id => { let f = fold(id); while ( f?.folder ) f = f.folder; return f?.name ?? ""; };
  return idx.map(e => ({ uuid: e.uuid ?? `Compendium.${pack.collection}.Item.${e._id}`, name: e.name, img: e.img, type: e.type,
    price: Number(foundry.utils.getProperty(e, "system.price.value")) || 0, cat: topName(e.folder) }))
    .filter(e => e.price > 0 && !/pack contents/i.test(e.cat));
}

const LOOT_TIERS = [["Cheap", 0, 100], ["Standard", 100, 1000], ["Valuable", 1000, 5000], ["Premium", 5000, Infinity]];
const CREDITS = [["CR 0–4", "3d6 * 50", [0, 1]], ["CR 5–10", "2d8 * 500", [1, 2]], ["CR 11–16", "2d10 * 5000", [2, 3]], ["CR 17+", "2d8 * 50000", [3, 3]]];

export async function neonRollLoot({ tier = 0, creatures = 1, items = 2, actor = null, whisper = true } = {}) {
  const [label, formula, [lo, hi]] = CREDITS[tier];
  let credits = 0;
  for ( let i = 0; i < creatures; i++ ) credits += (await new Roll(formula).evaluate()).total;
  const all = await neonItemIndex();
  const got = [];
  for ( let i = 0; i < items; i++ ) {
    const [, min, max] = LOOT_TIERS[Math.random() < 0.7 ? lo : hi];
    const pool = all.filter(e => e.price >= min && e.price < max);
    if ( pool.length ) got.push(pick(pool));
  }
  const target = actor ? game.actors.get(actor) : null;
  if ( target ) {
    const docs = [];
    for ( const g of got ) docs.push(game.items.fromCompendium(await fromUuid(g.uuid)));
    if ( docs.length ) await target.createEmbeddedDocuments("Item", docs);
    await target.update({ "system.currency.gn": (target.system.currency?.gn ?? 0) + credits });
  }
  const content = `<div class="neon-loot"><h3><i class="fa-solid fa-sack-dollar"></i> Loot (${label}, ${creatures} creature${creatures > 1 ? "s" : ""})</h3>
    <p><b>${gn(credits)}</b></p><ul>${got.map(g => `<li>@UUID[${g.uuid}]{${esc(g.name)}} <small>(${gn(g.price)})</small></li>`).join("") || "<li>No items</li>"}</ul>
    ${target ? `<p>Given to <b>${esc(target.name)}</b>.</p>` : ""}</div>`;
  await ChatMessage.implementation.create({ content, speaker: { alias: "Neon Loot" }, whisper: whisper ? ChatMessage.getWhisperRecipients("GM").map(u => u.id) : [] });
  return { credits, items: got };
}

const SHOP_TYPES = {
  general: ["General Store", e => e.cat === "Outrunning Gear" && e.type !== "consumable"],
  weapons: ["Weapon Shop", e => ["Weapons", "Ammunition"].includes(e.cat)],
  armor: ["Armor & Modules", e => ["Armor", "Weapon & Armor Modules"].includes(e.cat)],
  tools: ["Tools & Instruments", e => e.cat === "Tools"],
  consumables: ["Pharmacy & Explosives", e => e.type === "consumable"],
  black: ["Black Market", e => e.price >= 1000]
};

export async function neonGenerateShop({ type = "general", stock = 10, markup = 0, name = "" } = {}) {
  const [label, pred] = SHOP_TYPES[type];
  const pool = (await neonItemIndex()).filter(pred);
  const chosen = [];
  for ( const e of foundry.utils.deepClone(pool).sort(() => Math.random() - 0.5) ) {
    if ( chosen.length >= stock ) break;
    chosen.push({ ...e, qty: e.type === "consumable" ? 1 + Math.floor(Math.random() * 6) : 1 + Math.floor(Math.random() * 2) });
  }
  chosen.sort((a, b) => a.name.localeCompare(b.name));
  const mult = 1 + markup / 100;
  const html = `<p><i>${esc(label)}${markup ? `, prices ${markup > 0 ? "+" : ""}${markup}%` : ""}.</i> Drag an item onto a character sheet to buy it.</p>
    <table><thead><tr><th>Item</th><th>Price</th><th>Stock</th></tr></thead><tbody>
    ${chosen.map(e => `<tr><td>@UUID[${e.uuid}]{${esc(e.name)}}</td><td>${gn(Math.round(e.price * mult))}</td><td>${e.qty}</td></tr>`).join("")}</tbody></table>`;
  let folder = game.folders.find(f => f.type === "JournalEntry" && f.name === "Neon Shops");
  folder ??= await Folder.create({ name: "Neon Shops", type: "JournalEntry", color: "#c026d3" });
  const entry = await JournalEntry.implementation.create({ name: name || label, folder: folder.id,
    pages: [{ name: name || label, type: "text", text: { content: html } }] });
  entry.sheet.render(true);
  return entry;
}

async function neonLootDialog() {
  const pcs = game.actors.filter(a => a.type === "character").map(a => `<option value="${a.id}">${esc(a.name)}</option>`).join("");
  const res = await foundry.applications.api.DialogV2.prompt({
    window: { title: "Neon Loot Generator", icon: "fa-solid fa-sack-dollar" },
    content: `<div class="form-group"><label>Challenge Rating</label><select name="tier">${CREDITS.map((c, i) => `<option value="${i}">${c[0]}</option>`).join("")}</select></div>
      <div class="form-group"><label>Creatures</label><input type="number" name="creatures" value="1" min="1" max="20"></div>
      <div class="form-group"><label>Items</label><input type="number" name="items" value="2" min="0" max="10"></div>
      <div class="form-group"><label>Give to</label><select name="actor"><option value="">Nobody (chat only)</option>${pcs}</select></div>
      <div class="form-group"><label>GM only</label><input type="checkbox" name="whisper" checked></div>`,
    ok: { label: "Roll Loot", callback: (ev, btn) => new foundry.applications.ux.FormDataExtended(btn.form).object }
  }).catch(() => null);
  if ( res ) return neonRollLoot({ ...res, tier: Number(res.tier), creatures: Number(res.creatures), items: Number(res.items), actor: res.actor || null });
}

async function neonShopDialog() {
  const res = await foundry.applications.api.DialogV2.prompt({
    window: { title: "Neon Shop Generator", icon: "fa-solid fa-store" },
    content: `<div class="form-group"><label>Shop</label><select name="type">${Object.entries(SHOP_TYPES).map(([k, v]) => `<option value="${k}">${v[0]}</option>`).join("")}</select></div>
      <div class="form-group"><label>Name</label><input type="text" name="name" placeholder="Optional"></div>
      <div class="form-group"><label>Items in stock</label><input type="number" name="stock" value="10" min="1" max="60"></div>
      <div class="form-group"><label>Price change %</label><input type="number" name="markup" value="0" min="-90" max="500"></div>`,
    ok: { label: "Create Shop", callback: (ev, btn) => new foundry.applications.ux.FormDataExtended(btn.form).object }
  }).catch(() => null);
  if ( res ) return neonGenerateShop({ ...res, stock: Number(res.stock), markup: Number(res.markup) });
}

const neonOpenEncounter = () => new NeonEncounterBuilder().render(true);
Hooks.on("getSceneControlButtons", controls => {
  if ( !game.user.isGM ) return;
  const tools = controls.tokens?.tools;
  if ( !tools ) return;
  [["neonEncounter", "Neon Encounter Builder", "fa-solid fa-skull", neonOpenEncounter],
   ["neonLoot", "Neon Loot Generator", "fa-solid fa-sack-dollar", neonLootDialog],
   ["neonShop", "Neon Shop Generator", "fa-solid fa-store", neonShopDialog]].forEach(([name, title, icon, fn], i) => {
    tools[name] = { name, title, icon, order: 100 + i, button: true, visible: true, onChange: () => fn() };
  });
});

Hooks.once("init", () => {
  const mod = game.modules.get(NEON_GM);
  mod.api = { ...(mod.api ?? {}), encounterBuilder: neonOpenEncounter, generateEncounter: neonGenerateEncounter, placeEncounter: neonPlaceEncounter,
    monsterIndex: neonMonsterIndex, rollLoot: neonRollLoot, lootDialog: neonLootDialog, generateShop: neonGenerateShop, shopDialog: neonShopDialog,
    EncounterBuilder: NeonEncounterBuilder };
});
