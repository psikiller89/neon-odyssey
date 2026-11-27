// Neon Odyssey starship combat: Helm (hex movement, facing, maneuvers and stunts) and Focus/Reset Shields.
const NEON_SHIP = "neon-odyssey";
const HEX_FT = 500;

const neonShipHexes = actor => { const m = actor?.system.attributes.movement; return Math.floor((Number(m?.speeds?.fly ?? m?.fly) || 0) / HEX_FT); };
const neonIsShip = actor => (actor?.type === "vehicle") && (neonShipHexes(actor) > 0);
const normDeg = a => ((a % 360) + 360) % 360;
const degDiff = (a, b) => Math.abs(((a - b + 540) % 360) - 180);
const unsetFlag = k => foundry.data.operators?.ForcedDeletion
  ? { [`flags.${NEON_SHIP}.${k}`]: new foundry.data.operators.ForcedDeletion() } : { [`flags.${NEON_SHIP}.-=${k}`]: null };

/* ---------- Shields station: Focus Shields / Reset Shields ---------- */
async function neonFocusShields(actor) {
  const max = Number(actor.getFlag(NEON_SHIP, "shieldMax")) || 0;
  if ( !max ) return ui.notifications.warn(`${actor.name} has no shields.`);
  if ( actor.getFlag(NEON_SHIP, "shieldFocus") ) return ui.notifications.warn(`${actor.name}'s shields are already focused. Reset them first.`);
  const arc = await foundry.applications.api.DialogV2.wait({
    window: { title: `${actor.name}: Focus Shields` }, content: "<p>Focus the shields on which fire arc?</p>",
    buttons: ["Front", "Left", "Right", "Rear"].map(a => ({ action: a, label: a }))
  }).catch(() => null);
  if ( !arc ) return;
  const temp = Number(actor.system.attributes.hp.temp) || 0;
  await actor.update({ "system.attributes.hp.temp": temp * 2, [`flags.${NEON_SHIP}.shieldMax`]: max * 2,
    [`flags.${NEON_SHIP}.shieldBase`]: max, [`flags.${NEON_SHIP}.shieldFocus`]: arc });
  ChatMessage.implementation.create({ speaker: ChatMessage.getSpeaker({ actor }), content: `<p><strong>${actor.name}</strong> focuses its shields on the <strong>${arc}</strong> arc: ${temp * 2}/${max * 2} Shield Points. Damage from the other three arcs goes straight to Hit Points (remove the Temp HP by hand for those hits).</p>` });
}
async function neonResetShields(actor) {
  if ( !actor.getFlag(NEON_SHIP, "shieldFocus") ) return ui.notifications.info(`${actor.name}'s shields already cover all arcs.`);
  const base = Number(actor.getFlag(NEON_SHIP, "shieldBase")) || Math.floor((Number(actor.getFlag(NEON_SHIP, "shieldMax")) || 0) / 2);
  const temp = Math.floor((Number(actor.system.attributes.hp.temp) || 0) / 2);
  await actor.update({ "system.attributes.hp.temp": Math.min(temp, base), [`flags.${NEON_SHIP}.shieldMax`]: base, ...unsetFlag("shieldFocus"), ...unsetFlag("shieldBase") });
  ChatMessage.implementation.create({ speaker: ChatMessage.getSpeaker({ actor }), content: `<p><strong>${actor.name}</strong> resets its shields to cover all arcs: ${Math.min(temp, base)}/${base} Shield Points.</p>` });
}
Hooks.on("dnd5e.postUseActivity", activity => {
  const mode = activity?.flags?.[NEON_SHIP]?.shields;
  const actor = activity?.actor;
  if ( !mode || !actor?.isOwner ) return;
  if ( mode === "focus" ) neonFocusShields(actor); else if ( mode === "reset" ) neonResetShields(actor);
});

/* ---------- Helm ---------- */
function neonHelmDirs(tokenDoc) {
  const grid = canvas.grid;
  const center = tokenDoc.object?.center ?? { x: tokenDoc.x + (tokenDoc.width * grid.sizeX) / 2, y: tokenDoc.y + (tokenDoc.height * grid.sizeY) / 2 };
  const off = grid.getOffset(center);
  const c = grid.getCenterPoint(off);
  const dirs = grid.getAdjacentOffsets(off).map(o => {
    const p = grid.getCenterPoint(o);
    return { dx: p.x - c.x, dy: p.y - c.y, ang: normDeg(Math.toDegrees(Math.atan2(p.y - c.y, p.x - c.x))) };
  }).sort((a, b) => a.ang - b.ang);
  const facing = normDeg((tokenDoc.rotation ?? 0) - 90);
  let idx = 0;
  dirs.forEach((d, i) => { if ( degDiff(d.ang, facing) < degDiff(dirs[idx].ang, facing) ) idx = i; });
  return { dirs, idx, at: k => dirs[((idx + k) % dirs.length + dirs.length) % dirs.length] };
}
const neonHelmState = t => foundry.utils.mergeObject({ moved: 0, last: 0, forward: 0, slipReady: true, dash: false, stunt: false, freeTurns: 0, pivot: false, reverse: false, log: [] }, t.getFlag(NEON_SHIP, "helm") ?? {}, { inplace: false });

class NeonHelm extends foundry.applications.api.ApplicationV2 {
  constructor(tokenDoc, options = {}) {
    super({ id: `neon-helm-${tokenDoc.id}`, ...options });
    this.token = tokenDoc;
    this._hook = Hooks.on("updateToken", doc => { if ( doc === this.token ) this.render(); });
  }
  static DEFAULT_OPTIONS = { classes: ["neon-gm-tool", "neon-helm"], window: { title: "Helm", icon: "fa-solid fa-dharmachakra" }, position: { width: 380, height: "auto" } };
  get title() { return `Helm: ${this.token.name}`; }
  get actor() { return this.token.actor; }
  get state() { return neonHelmState(this.token); }
  get speed() {
    const ex = this.actor.system.attributes.exhaustion ?? 0;
    return Math.max(0, neonShipHexes(this.actor) - ex) * (this.state.dash ? 2 : 1);
  }
  async _close(options) { Hooks.off("updateToken", this._hook); return super._close?.(options); }
  async close(options) { Hooks.off("updateToken", this._hook); return super.close(options); }

  async _renderHTML() {
    const s = this.state, speed = this.speed, left = speed - s.moved;
    const { at } = neonHelmDirs(this.token);
    const facing = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"][Math.round(normDeg(at(0).ang) / 45) % 8];
    const shield = this.actor.getFlag(NEON_SHIP, "shieldFocus");
    const btn = (act, label, title, dis = false) => `<button type="button" data-act="${act}" title="${title}" ${dis ? "disabled" : ""}>${label}</button>`;
    const noFwd = s.reverse || s.pivot;
    return `<div class="neon-helm-body" style="display:flex;flex-direction:column;gap:6px">
      <p style="margin:0"><b>Speed</b> ${speed} hexes${s.dash ? " (Dash)" : ""} · <b>Used</b> ${s.moved} · <b>Left</b> ${left}<br>
      <b>Facing</b> ${facing} · <b>Last turn</b> ${s.last} hexes${shield ? ` · <b>Shields</b> ${shield}` : ""}${s.freeTurns ? ` · <b>Free turns</b> ${s.freeTurns}` : ""}</p>
      <fieldset><legend>Simple Maneuvers</legend><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px">
        ${btn("slipL", "↖ Side Slip", "Move diagonally forward-left 1 hex (2 hexes of movement). Needs 1 hex forward first.", noFwd || left < 2 || !s.slipReady || !s.forward)}
        ${btn("fwd", "▲ Forward", "Move forward 1 hex.", noFwd || left < 1)}
        ${btn("slipR", "Side Slip ↗", "Move diagonally forward-right 1 hex (2 hexes of movement). Needs 1 hex forward first.", noFwd || left < 2 || !s.slipReady || !s.forward)}
        ${btn("turnL", "⟲ Turn Left", "Turn 60° (1 hex of movement, after moving at least 1 hex forward).", !(s.pivot || s.freeTurns || (s.forward && left >= 1)))}
        ${btn("momentum", `⏩ Keep Course (${s.last})`, "Continue the same number of hexes as last turn.", noFwd || !s.last || s.moved || left < s.last)}
        ${btn("turnR", "Turn Right ⟳", "Turn 60° (1 hex of movement, after moving at least 1 hex forward).", !(s.pivot || s.freeTurns || (s.forward && left >= 1)))}
        ${btn("reverse", "▼ Reverse", "Move 1 hex backward. Costs all movement.", s.moved > 0)}
        ${btn("pivot", "◎ Pivot", "Spend all movement to face any direction.", s.moved > 0)}
        ${btn("loop", "∞ Loop", "12 hexes: end 1 hex behind your start, same facing.", noFwd || left < 12)}
      </div></fieldset>
      <fieldset><legend>Stunts (vehicle Dexterity check, one per move)</legend><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px">
        ${btn("tightTurn", "Tight Turn", "Free turn in place: DC 10 for 60°, 15 for 120°, 20 for 180°.", s.stunt)}
        ${btn("wingover", "Wingover (DC 20)", "End 1 hex behind, facing the opposite way, free.", s.stunt)}
        ${btn("hardLoop", "Hard Loop (DC 25)", "End 1 hex behind, same facing, free.", s.stunt)}
        ${btn("pursuit", "Pursuit", "Vehicle Dexterity check; the target makes a vehicle Dexterity save against your total.", s.stunt)}
        ${btn("skim", "Skimming Run", "DC 10 Gargantuan, 20 Huge, 25 Large target. Fail by more than 5: crash.", s.stunt)}
        ${btn("landing", "Fast Landing (DC 15)", "Land or dock above 1 hex Speed. Fail by more than 5: crash.", s.stunt)}
      </div></fieldset>
      <div style="display:flex;gap:4px">${btn("dash", s.dash ? "Dash ✓" : "Dash", "The pilot's action: double Speed this turn.", s.dash)}${btn("undo", "Undo", "Undo the last helm move.", !s.log.length)}${btn("newTurn", "New Turn", "Start a new turn (done automatically in combat).")}</div>
      <p class="hint" style="margin:0">1 hex = 500 ft in atmosphere, 1,500 ft in space. Starship rules are from the Neon Odyssey Pre-Launch playtest.</p>
    </div>`;
  }

  _replaceHTML(result, content) {
    content.innerHTML = result;
    content.querySelectorAll("button[data-act]").forEach(b => b.addEventListener("click", ev => { ev.preventDefault(); this._act(b.dataset.act); }));
  }

  async _save(s, update = {}, entry = null) {
    if ( entry ) s.log = [...s.log.slice(-19), { x: this.token.x, y: this.token.y, rotation: this.token.rotation, prev: foundry.utils.deepClone({ ...s, log: [] }) }];
    await this.token.update({ ...update, [`flags.${NEON_SHIP}.helm`]: s });
  }
  async _move(s, dir, { cost = 1, face = null, forward = false } = {}) {
    const upd = { x: this.token.x + Math.round(dir.dx), y: this.token.y + Math.round(dir.dy) };
    if ( face ) upd.rotation = normDeg(face.ang + 90);
    const snap = foundry.utils.deepClone(s);
    s.moved += cost;
    if ( forward ) { s.forward += 1; s.slipReady = true; }
    await this._save(s, upd, snap);
  }
  async _check(dc, label) {
    const rolls = await this.actor.rollAbilityCheck({ ability: "dex", target: dc }, {}, { data: { flavor: `${this.token.name}: ${label}${dc ? ` (DC ${dc})` : ""}` } });
    return rolls?.[0]?.total ?? null;
  }
  async _act(act) {
    const s = this.state, h = neonHelmDirs(this.token), snap = () => foundry.utils.deepClone(s);
    switch ( act ) {
      case "fwd": return this._move(s, h.at(0), { forward: true, face: h.at(0) });
      case "momentum": {
        const n = Math.min(s.last, this.speed - s.moved); if ( n < 1 ) return;
        const d = h.at(0);
        await this._move(s, { dx: d.dx * n, dy: d.dy * n }, { cost: n, face: d, forward: true });
        const t = this.state; t.forward = s.forward - 1 + n; return this._save(t);
      }
      case "slipL": case "slipR": {
        const k = act === "slipL" ? -1 : 1;
        const n = h.dirs.length === 6 ? k : k;
        await this._move(s, h.at(n), { cost: 2 });
        const t = this.state; t.slipReady = false; t.forward = 0; return this._save(t);
      }
      case "turnL": case "turnR": {
        const step = h.dirs.length === 8 ? 2 : 1;
        const face = h.at(act === "turnL" ? -step : step);
        const old = snap();
        if ( s.pivot ) {} else if ( s.freeTurns ) s.freeTurns--; else s.moved += 1;
        return this._save(s, { rotation: normDeg(face.ang + 90) }, old);
      }
      case "reverse": { const old = snap(); s.reverse = true; s.moved = this.speed; return this._save(s, { x: this.token.x - Math.round(h.at(0).dx), y: this.token.y - Math.round(h.at(0).dy) }, old); }
      case "pivot": { const old = snap(); s.pivot = true; s.moved = this.speed; return this._save(s, {}, old); }
      case "loop": { const back = h.at(h.dirs.length / 2); return this._move(s, back, { cost: 12 }); }
      case "dash": { const old = snap(); s.dash = true; return this._save(s, {}, old); }
      case "newTurn": return this._save({ ...neonHelmState({ getFlag: () => null }), last: s.moved });
      case "undo": {
        const e = s.log.at(-1); if ( !e ) return;
        return this.token.update({ x: e.x, y: e.y, rotation: e.rotation, [`flags.${NEON_SHIP}.helm`]: { ...e.prev, log: s.log.slice(0, -1) } });
      }
      case "tightTurn": {
        const tot = await this._check(null, "Tight Turn"); if ( tot === null ) return;
        const faces = tot >= 20 ? 3 : tot >= 15 ? 2 : tot >= 10 ? 1 : 0;
        const old = snap(); s.stunt = true; s.freeTurns += faces * (h.dirs.length === 8 ? 1 : 1);
        await this._save(s, {}, old);
        return this._chat(`Tight Turn: ${tot} — ${faces ? `can turn up to ${faces * 60}° in place for free` : "failed, no free turn"}.`);
      }
      case "wingover": case "hardLoop": {
        const dc = act === "wingover" ? 20 : 25;
        const tot = await this._check(dc, act === "wingover" ? "Wingover" : "Hard Loop"); if ( tot === null ) return;
        const old = snap(); s.stunt = true;
        if ( tot < dc ) { await this._save(s, {}, old); return this._chat(`${act === "wingover" ? "Wingover" : "Hard Loop"} failed (${tot}).`); }
        const back = h.at(h.dirs.length / 2);
        const upd = { x: this.token.x + Math.round(back.dx), y: this.token.y + Math.round(back.dy) };
        if ( act === "wingover" ) upd.rotation = normDeg(back.ang + 90);
        return this._save(s, upd, old);
      }
      case "pursuit": case "skim": case "landing": {
        let dc = act === "landing" ? 15 : null, label = { pursuit: "Pursuit", skim: "Skimming Run", landing: "Fast Landing" }[act];
        if ( act === "skim" ) {
          dc = await foundry.applications.api.DialogV2.wait({ window: { title: "Skimming Run" }, content: "<p>Target size (starship scale)?</p>",
            buttons: [["Gargantuan", 10], ["Huge", 20], ["Large", 25]].map(([l, v]) => ({ action: String(v), label: `${l} (DC ${v})` })) }).catch(() => null);
          if ( !dc ) return; dc = Number(dc);
        }
        const tot = await this._check(dc, label); if ( tot === null ) return;
        const old = snap(); s.stunt = true; await this._save(s, {}, old);
        if ( act === "pursuit" ) return this._chat(`Pursuit: the target makes a DC ${tot} vehicle Dexterity saving throw. On a failure, ${this.token.name} is in pursuit: it moves with the target and can use a Reaction to fire one front weapon at it.`);
        if ( tot < dc - 5 ) return this._chat(`${label} failed by more than 5 (${tot}): ${this.token.name} crashes!`);
        if ( act === "skim" && tot >= dc ) return this._chat(`Skimming Run (${tot}): until the end of ${this.token.name}'s next turn it is off sensors and the target's weapons can't target it.`);
      }
    }
  }
  _chat(text) { return ChatMessage.implementation.create({ speaker: ChatMessage.getSpeaker({ token: this.token }), content: `<p>${text}</p>` }); }
}

const neonOpenHelm = tokenDoc => {
  if ( !tokenDoc ) return ui.notifications.warn("Select a starship token first.");
  if ( !neonIsShip(tokenDoc.actor) ) return ui.notifications.warn(`${tokenDoc.name} doesn't move in hexes.`);
  const existing = foundry.applications.instances.get(`neon-helm-${tokenDoc.id}`);
  return existing ? existing.render({ force: true }) : new NeonHelm(tokenDoc).render({ force: true });
};

Hooks.on("renderTokenHUD", (hud, html) => {
  const doc = hud.document ?? hud.object?.document;
  if ( !neonIsShip(doc?.actor) || !doc.isOwner ) return;
  const root = html instanceof HTMLElement ? html : html[0];
  const col = root.querySelector(".col.left");
  if ( !col || col.querySelector(".neon-helm-hud") ) return;
  const b = document.createElement("button");
  b.type = "button"; b.className = "control-icon neon-helm-hud"; b.dataset.tooltip = "Helm";
  b.innerHTML = `<i class="fa-solid fa-dharmachakra" inert></i>`;
  b.addEventListener("click", ev => { ev.preventDefault(); neonOpenHelm(doc); });
  col.append(b);
});

/* New turn in combat: momentum is the hexes moved last turn. */
Hooks.on("combatTurnChange", async (combat, prior, current) => {
  if ( !game.users.activeGM?.isSelf ) return;
  const t = combat.combatants.get(current?.combatantId)?.token;
  if ( !t || !neonIsShip(t.actor) ) return;
  const s = neonHelmState(t);
  await t.update({ [`flags.${NEON_SHIP}.helm`]: { ...neonHelmState({ getFlag: () => null }), last: s.moved } });
  if ( s.moved && !s.reverse && !s.pivot ) ChatMessage.implementation.create({ speaker: ChatMessage.getSpeaker({ token: t }), whisper: ChatMessage.getWhisperRecipients("GM").map(u => u.id), content: `<p><strong>${t.name}</strong> keeps moving ${s.moved} hexes forward unless its pilot changes course (Helm → Keep Course).</p>` });
});

Hooks.once("init", () => {
  const mod = game.modules.get(NEON_SHIP);
  mod.api = { ...(mod.api ?? {}), openHelm: neonOpenHelm, Helm: NeonHelm, focusShields: neonFocusShields, resetShields: neonResetShields };
});
