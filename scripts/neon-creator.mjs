// Neon Odyssey guided character creator: name, ability scores, species, background (with Homeworld origin feat) and class.
const NEON_CC = "neon-odyssey";
const ABILS = ["str", "dex", "con", "int", "wis", "cha"];
const STD_ARRAY = [15, 14, 13, 12, 10, 8];
const PB_COST = { 8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9 };
const esc = s => foundry.utils.escapeHTML(String(s ?? ""));
const strip = html => String(html ?? "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

async function neonCreatorOptions(includeDnd) {
  const get = async (packId, types, folderTest = null) => {
    const pack = game.packs.get(packId);
    if ( !pack ) return [];
    const idx = await pack.getIndex({ fields: ["system.description.value", "folder"] });
    return idx.filter(e => types.includes(e.type) && (!folderTest || folderTest(pack.folders.get(e.folder))))
      .map(e => ({ uuid: e.uuid ?? `Compendium.${packId}.Item.${e._id}`, name: e.name, img: e.img, desc: strip(foundry.utils.getProperty(e, "system.description.value")).slice(0, 420), source: pack.metadata.label }))
      .sort((a, b) => a.name.localeCompare(b.name));
  };
  const o = {
    species: await get(`${NEON_CC}.origins`, ["race"]),
    backgrounds: await get(`${NEON_CC}.origins`, ["background"]),
    classes: await get(`${NEON_CC}.classes`, ["class"])
  };
  if ( includeDnd ) {
    for ( const id of ["dnd5e.origins24"] ) {
      o.species.push(...await get(id, ["race"]));
      o.backgrounds.push(...await get(id, ["background"]));
    }
    o.classes.push(...await get("dnd5e.classes24", ["class"]));
  }
  return o;
}

async function neonRunAdvancement(actor, itemData) {
  const AM = dnd5e.applications.advancement.AdvancementManager;
  const manager = AM.forNewItem(actor, itemData);
  if ( !manager.steps.length ) return actor.createEmbeddedDocuments("Item", [itemData]);
  return new Promise(resolve => {
    const close = manager.close.bind(manager);
    manager.close = async (...args) => { const r = await close(...args); resolve(); return r; };
    manager.render({ force: true });
  });
}

class NeonCharacterCreator extends foundry.applications.api.ApplicationV2 {
  static DEFAULT_OPTIONS = { id: "neon-character-creator", classes: ["neon-gm-tool", "neon-creator"], window: { title: "Neon Odyssey Character Creator", icon: "fa-solid fa-user-astronaut", resizable: true }, position: { width: 640, height: 760 } };
  state = { step: 0, name: "", method: "standard", scores: { str: 15, dex: 14, con: 13, int: 12, wis: 10, cha: 8 }, species: null, background: null, cls: null, level: 1, dnd: false, opts: null };
  static STEPS = ["Name & Abilities", "Species", "Background & Homeworld", "Class", "Review"];

  async _renderHTML() {
    const s = this.state;
    s.opts ??= await neonCreatorOptions(s.dnd);
    const steps = NeonCharacterCreator.STEPS.map((n, i) => `<span style="padding:2px 6px;border-radius:4px;${i === s.step ? "background:#c026d3;color:#fff" : "opacity:.7"}">${i + 1}. ${n}</span>`).join(" ");
    const body = [() => this._abilities(), () => this._pick("species", s.opts.species, "Your species gives your size, speed and species traits."),
      () => this._pick("background", s.opts.backgrounds, "The Outrunner custom background lets you choose your ability increases, skills, tool, languages and your Homeworld origin feat during the next step."),
      () => this._pick("cls", s.opts.classes, "") + `<div class="form-group"><label>Starting level</label><input type="number" name="level" min="1" max="20" value="${s.level}"></div>`,
      () => this._review()][s.step]();
    const ok = [s.name.trim() && this._valid(), s.species, s.background, s.cls, true][s.step];
    return `<form class="neon-cc" style="display:flex;flex-direction:column;gap:8px;height:100%">
      <div style="display:flex;flex-wrap:wrap;gap:4px;font-size:12px">${steps}</div>
      <div style="flex:1;overflow:auto">${body}</div>
      <label style="font-size:12px"><input type="checkbox" name="dnd" ${s.dnd ? "checked" : ""}> Also show dnd5e (2024) species, backgrounds and classes</label>
      <div style="display:flex;gap:6px">
        <button type="button" data-act="back" ${s.step ? "" : "disabled"}><i class="fa-solid fa-arrow-left"></i> Back</button>
        ${s.step < 4 ? `<button type="button" data-act="next" ${ok ? "" : "disabled"}>Next <i class="fa-solid fa-arrow-right"></i></button>`
          : `<button type="button" data-act="create"><i class="fa-solid fa-user-plus"></i> Create Character</button>`}
      </div></form>`;
  }

  _valid() {
    const v = ABILS.map(a => this.state.scores[a]);
    if ( this.state.method === "standard" ) return [...v].sort((a, b) => b - a).join() === STD_ARRAY.join();
    if ( this.state.method === "pointbuy" ) return v.every(x => x in PB_COST) && v.reduce((t, x) => t + PB_COST[x], 0) <= 27;
    return v.every(x => (x >= 3) && (x <= 20));
  }
  _abilities() {
    const s = this.state;
    const cfg = CONFIG.DND5E.abilities;
    const field = a => {
      const v = s.scores[a];
      if ( s.method === "standard" ) return `<select name="score.${a}">${STD_ARRAY.map(n => `<option ${n === v ? "selected" : ""}>${n}</option>`).join("")}</select>`;
      const [min, max] = s.method === "pointbuy" ? [8, 15] : [3, 20];
      return `<input type="number" name="score.${a}" min="${min}" max="${max}" value="${v}">`;
    };
    const spent = ABILS.reduce((t, a) => t + (PB_COST[s.scores[a]] ?? 99), 0);
    const note = s.method === "standard" ? "Use each of 15, 14, 13, 12, 10 and 8 once." : s.method === "pointbuy" ? `Points spent: ${spent} / 27 (scores 8–15).` : "Enter rolled or chosen scores (3–20).";
    return `<div class="form-group"><label>Character name</label><input type="text" name="name" value="${esc(s.name)}" placeholder="Name"></div>
      <div class="form-group"><label>Ability scores</label><select name="method">
        ${[["standard", "Standard Array"], ["pointbuy", "Point Buy"], ["manual", "Manual / Rolled"]].map(([k, l]) => `<option value="${k}" ${s.method === k ? "selected" : ""}>${l}</option>`).join("")}</select></div>
      <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:6px;text-align:center">
        ${ABILS.map(a => `<label>${esc(cfg[a]?.label ?? a)}<br>${field(a)}</label>`).join("")}</div>
      <p class="hint" style="color:${this._valid() ? "inherit" : "#f87171"}">${note} Your background adds its ability increases in the next steps.</p>`;
  }
  _pick(key, list, hint) {
    const cur = this.state[key];
    return `${hint ? `<p class="hint">${hint}</p>` : ""}<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:6px">
      ${list.map(o => `<a class="neon-cc-opt" data-key="${key}" data-uuid="${esc(o.uuid)}" title="${esc(o.desc)}" style="display:flex;flex-direction:column;align-items:center;padding:4px;border-radius:6px;border:2px solid ${cur?.uuid === o.uuid ? "#c026d3" : "transparent"};background:rgba(0,0,0,.15)">
        <img src="${esc(o.img)}" style="width:64px;height:64px;object-fit:contain;border:none"><span style="text-align:center">${esc(o.name)}</span>${o.source.startsWith("Neon") ? "" : `<small>${esc(o.source)}</small>`}</a>`).join("")}</div>
      ${cur ? `<div style="margin-top:8px;padding:6px;border-left:3px solid #c026d3"><b>${esc(cur.name)}</b><p>${esc(cur.desc)}${cur.desc.length >= 420 ? "…" : ""}</p></div>` : ""}`;
  }
  _review() {
    const s = this.state;
    return `<h3>${esc(s.name)}</h3><p>${ABILS.map(a => `${a.toUpperCase()} ${s.scores[a]}`).join(" · ")}</p>
      <p><b>Species:</b> ${esc(s.species?.name)}<br><b>Background:</b> ${esc(s.background?.name)}<br><b>Class:</b> ${esc(s.cls?.name)}, level ${s.level}</p>
      <p class="hint">Click Create Character. The dnd5e advancement windows then open in order (species, background, class). Make your choices in each one, including your Homeworld origin feat, skills and, from level 3, your subclass.</p>`;
  }

  _replaceHTML(result, content) {
    content.innerHTML = result;
    const form = content.querySelector("form"), s = this.state;
    form.addEventListener("change", ev => {
      const t = ev.target;
      if ( t.name === "dnd" ) { s.dnd = t.checked; s.opts = null; return this.render(); }
      if ( t.name === "name" ) { s.name = t.value; return this.render(); }
      if ( t.name === "level" ) { s.level = Math.clamp(Number(t.value) || 1, 1, 20); return; }
      if ( t.name === "method" ) {
        s.method = t.value;
        if ( s.method === "standard" ) ABILS.forEach((a, i) => s.scores[a] = STD_ARRAY[i]);
        if ( s.method === "pointbuy" ) ABILS.forEach(a => s.scores[a] = 8);
        return this.render();
      }
      if ( t.name?.startsWith("score.") ) {
        const a = t.name.slice(6), v = Number(t.value);
        if ( s.method === "standard" ) { const other = ABILS.find(x => (x !== a) && (s.scores[x] === v)); if ( other ) s.scores[other] = s.scores[a]; }
        s.scores[a] = v; return this.render();
      }
    });
    form.addEventListener("click", async ev => {
      const opt = ev.target.closest(".neon-cc-opt");
      if ( opt ) {
        const list = { species: s.opts.species, background: s.opts.backgrounds, cls: s.opts.classes }[opt.dataset.key];
        s[opt.dataset.key] = list.find(o => o.uuid === opt.dataset.uuid); return this.render();
      }
      const b = ev.target.closest("button[data-act]");
      if ( !b ) return;
      if ( b.dataset.act === "back" ) { s.step--; return this.render(); }
      if ( b.dataset.act === "next" ) { s.step++; return this.render(); }
      if ( b.dataset.act === "create" ) { b.disabled = true; return this._create(); }
    });
  }

  async _create() {
    const s = this.state;
    const species = await fromUuid(s.species.uuid);
    const data = { name: s.name.trim(), type: "character", img: species?.img,
      system: { abilities: Object.fromEntries(ABILS.map(a => [a, { value: s.scores[a] }])) },
      prototypeToken: { name: s.name.trim(), actorLink: true, disposition: CONST.TOKEN_DISPOSITIONS.FRIENDLY, sight: { enabled: true } } };
    const tokenImg = species?.getFlag?.(NEON_CC, "token") ?? species?.system?.token;
    if ( tokenImg ) data.prototypeToken.texture = { src: tokenImg };
    if ( !game.user.isGM ) data.ownership = { [game.user.id]: CONST.DOCUMENT_OWNERSHIP_LEVELS.OWNER };
    const actor = await Actor.implementation.create(data);
    if ( !actor ) return;
    await this.close();
    for ( const [uuid, levels] of [[s.species.uuid], [s.background.uuid], [s.cls.uuid, s.level]] ) {
      const doc = await fromUuid(uuid);
      if ( !doc ) continue;
      const itemData = game.items.fromCompendium(doc);
      if ( levels ) itemData.system.levels = levels;
      await neonRunAdvancement(actor, itemData);
    }
    if ( !game.user.isGM && !game.user.character ) await game.user.update({ character: actor.id });
    actor.sheet.render(true);
    ui.notifications.info(`${actor.name} is ready.`);
    return actor;
  }
}

const neonOpenCreator = () => new NeonCharacterCreator().render({ force: true });
Hooks.on("renderActorDirectory", (app, html) => {
  if ( !game.user.can("ACTOR_CREATE") ) return;
  const root = html instanceof HTMLElement ? html : html[0];
  const actions = root?.querySelector(".header-actions");
  if ( !actions || root.querySelector(".neon-creator-btn") ) return;
  const b = document.createElement("button");
  b.type = "button"; b.className = "neon-creator-btn";
  b.innerHTML = `<i class="fa-solid fa-user-astronaut" inert></i><span>Neon Character Creator</span>`;
  b.addEventListener("click", ev => { ev.preventDefault(); neonOpenCreator(); });
  actions.after(b);
});
Hooks.once("init", () => {
  const mod = game.modules.get(NEON_CC);
  mod.api = { ...(mod.api ?? {}), characterCreator: neonOpenCreator, CharacterCreator: NeonCharacterCreator, runAdvancement: neonRunAdvancement };
});
