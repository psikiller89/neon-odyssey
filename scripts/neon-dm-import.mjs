const NEON_ID = "neon-odyssey";
const FLAG = "dmId";
const TYPE_FOLDERS = {
  planet: "Planets", location: "Locations", faction: "Factions", npc: "NPCs",
  tech: "Tech & Items", lore: "Lore", note: "Notes"
};
const PIN_ICON = "icons/svg/circle.svg";

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const cap = s => String(s ?? "").replace(/^./, c => c.toUpperCase());

/* ---------- markdown (same dialect as the DM app) ---------- */
function inline(s, link) {
  return s.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, t, label) => link(t.trim(), label))
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>").replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>");
}
function md(src, link) {
  const lines = esc(src || "").split(/\r?\n/);
  let out = "", list = false, para = [];
  const flush = () => { if ( para.length ) { out += `<p>${para.join("<br>")}</p>`; para = []; } };
  const closeList = () => { if ( list ) { out += "</ul>"; list = false; } };
  for ( const l of lines ) {
    let m;
    if ( !l.trim() ) { flush(); closeList(); continue; }
    if ( (m = l.match(/^(#{1,3})\s+(.*)/)) ) { flush(); closeList(); const n = m[1].length + 1; out += `<h${n}>${inline(m[2], link)}</h${n}>`; continue; }
    if ( (m = l.match(/^\s*[-*]\s+(.*)/)) ) { flush(); if ( !list ) { out += "<ul>"; list = true; } out += `<li>${inline(m[1], link)}</li>`; continue; }
    if ( /^---+\s*$/.test(l) ) { flush(); closeList(); out += "<hr>"; continue; }
    closeList(); para.push(inline(l, link));
  }
  flush(); closeList();
  return out;
}

/* ---------- generated map backgrounds (ported from the DM app) ---------- */
function rng(seedStr) {
  let h = 1779033703;
  for ( const c of seedStr ) h = Math.imul(h ^ c.charCodeAt(0), 3432918353), h = (h << 13) | (h >>> 19);
  return () => { h = Math.imul(h ^ (h >>> 16), 2246822507); h = Math.imul(h ^ (h >>> 13), 3266489909); return ((h ^= h >>> 16) >>> 0) / 4294967296; };
}
async function genImage(key) {
  const [, kind, seedStr] = key.split(":");
  const r = rng(seedStr || "x");
  const pick = a => a[Math.floor(r() * a.length)];
  const W = 2400, H = 1600, c = document.createElement("canvas");
  c.width = W; c.height = H;
  const g = c.getContext("2d");
  if ( kind === "city" ) {
    g.fillStyle = "#0b0418"; g.fillRect(0, 0, W, H);
    const blocks = [];
    for ( let x = 40; x < W; x += 120 + Math.floor(r() * 60) ) for ( let y = 40; y < H; y += 100 + Math.floor(r() * 60) ) blocks.push([x, y]);
    for ( const [x, y] of blocks ) {
      const w = 70 + (r() * 50), h = 50 + (r() * 50);
      g.fillStyle = `hsl(${260 + (r() * 40)},45%,${10 + (r() * 8)}%)`; g.fillRect(x, y, w, h);
      if ( r() < .3 ) { g.strokeStyle = pick(["#ff2e97", "#2de2ff", "#ffd31a"]); g.globalAlpha = .6; g.lineWidth = 2; g.strokeRect(x + 4, y + 4, w - 8, h - 8); g.globalAlpha = 1; }
    }
    for ( let i = 0; i < 6; i++ ) {
      const pts = i < 3
        ? (y => [0, y, W / 3, y + ((r() - .5) * 600), W * 2 / 3, y + ((r() - .5) * 600), W, r() * H])(r() * H)
        : (x => [x, 0, x + ((r() - .5) * 600), H / 3, x + ((r() - .5) * 600), H * 2 / 3, r() * W, H])(r() * W);
      const col = i % 2 ? "45,226,255" : "255,46,151";
      for ( const [w, a] of [[26, .08], [16, .14], [6, .55]] ) {
        g.strokeStyle = `rgba(${col},${a})`; g.lineWidth = w; g.beginPath();
        g.moveTo(pts[0], pts[1]); g.bezierCurveTo(...pts.slice(2)); g.stroke();
      }
    }
    g.fillStyle = "#1a5cff33"; g.beginPath(); g.ellipse(W * r(), H, W * .4, H * .25, 0, 0, Math.PI * 2); g.fill();
  } else {
    const bg = g.createRadialGradient(W / 2, H / 2, 50, W / 2, H / 2, W * .7);
    bg.addColorStop(0, "#1c0b3a"); bg.addColorStop(1, "#05020c");
    g.fillStyle = bg; g.fillRect(0, 0, W, H);
    for ( let i = 0; i < 9; i++ ) {
      const x = r() * W, y = r() * H, rad = 200 + (r() * 600), col = pick(["255,46,151", "45,226,255", "180,140,255", "255,122,47"]);
      const n = g.createRadialGradient(x, y, 0, x, y, rad);
      n.addColorStop(0, `rgba(${col},.22)`); n.addColorStop(1, `rgba(${col},0)`); g.fillStyle = n; g.fillRect(0, 0, W, H);
    }
    for ( let i = 0; i < 2600; i++ ) {
      const s = r() < .97 ? r() * 1.6 : 2 + (r() * 2.5);
      g.fillStyle = `rgba(255,255,255,${.3 + (r() * .7)})`; g.beginPath(); g.arc(r() * W, r() * H, s, 0, Math.PI * 2); g.fill();
    }
    g.strokeStyle = "#2de2ff14"; g.lineWidth = 1;
    for ( let x = 0; x < W; x += 200 ) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
    for ( let y = 0; y < H; y += 200 ) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
  }
  return new Promise(res => c.toBlob(res, "image/jpeg", .9));
}

/* ---------- helpers ---------- */
const slug = s => String(s ?? "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "campaign";
const FP = () => foundry.applications.apps.FilePicker.implementation;

async function ensureDir(path) {
  let cur = "";
  for ( const part of path.split("/") ) {
    cur = cur ? `${cur}/${part}` : part;
    const exists = await FP().browse("data", cur).then(r => r?.target === cur, () => false);
    if ( !exists ) await FP().createDirectory("data", cur, {});
  }
}

async function upload(dir, name, blob) {
  const res = await FP().upload("data", dir, new File([blob], name, { type: blob.type }), {}, { notify: false });
  if ( !res?.path ) throw new Error(`Upload of ${name} failed`);
  return res.path;
}

function b64Blob(b64, name) {
  const ext = name.split(".").pop().toLowerCase();
  const type = { jpg: "image/jpeg", jpeg: "image/jpeg", png: "image/png", webp: "image/webp", gif: "image/gif", svg: "image/svg+xml" }[ext] ?? "application/octet-stream";
  const bin = atob(b64), arr = new Uint8Array(bin.length);
  for ( let i = 0; i < bin.length; i++ ) arr[i] = bin.charCodeAt(i);
  return new Blob([arr], { type });
}

function imageSize(src) {
  return new Promise(res => {
    const img = new Image();
    img.onload = () => res({ width: img.naturalWidth, height: img.naturalHeight });
    img.onerror = () => res({ width: 2400, height: 1600 });
    img.src = foundry.utils.getRoute(src);
  });
}

async function folder(type, name, parent = null) {
  const f = game.folders.find(x => (x.type === type) && (x.name === name) && ((x.folder?.id ?? null) === (parent?.id ?? null)));
  return f ?? Folder.implementation.create({ type, name, folder: parent?.id ?? null, color: "#ff2e97" });
}

const byFlag = (collection, id) => collection.find(d => d.getFlag(NEON_ID, FLAG) === id);

async function upsert(cls, collection, dmId, data) {
  const existing = byFlag(collection, dmId);
  foundry.utils.setProperty(data, `flags.${NEON_ID}.${FLAG}`, dmId);
  if ( existing ) { await existing.update(data); return [existing, false]; }
  return [await cls.create(data), true];
}

async function upsertPage(entry, name, html, sort = 0, key = name) {
  const page = entry.pages.find(p => p.getFlag(NEON_ID, FLAG) === key);
  const data = { name, type: "text", sort, text: { content: html, format: CONST.JOURNAL_ENTRY_PAGE_FORMATS.HTML },
    flags: { [NEON_ID]: { [FLAG]: key } } };
  if ( page ) return page.update(data);
  return entry.createEmbeddedDocuments("JournalEntryPage", [data]);
}

async function speciesItem(name) {
  if ( !name ) return null;
  const pack = game.packs.get(`${NEON_ID}.origins`);
  if ( !pack ) return null;
  const idx = await pack.getIndex({ fields: ["type"] });
  const hit = idx.find(i => (i.type === "race") && (i.name.toLowerCase() === name.toLowerCase()));
  return hit ? pack.getDocument(hit._id) : null;
}

/* ---------- import ---------- */
export async function neonImportDmCampaign(data, { notify = true } = {}) {
  if ( !game.user.isGM ) throw new Error("Only a GM can import a campaign.");
  if ( !Array.isArray(data?.entries) ) throw new Error("This isn't a Neon Odyssey DM campaign export.");
  const campaign = data.campaign?.name || "Neon Odyssey Campaign";
  const dir = `worlds/${game.world.id}/neon-odyssey-dm/${slug(campaign)}`;
  const images = data.__images ?? {};
  const uploaded = {};
  const stats = { journals: 0, actors: 0, scenes: 0, sessions: 0, created: 0, updated: 0 };
  const count = created => created ? stats.created++ : stats.updated++;

  const progress = notify ? ui.notifications.info(`Importing "${campaign}" from Neon Odyssey DM...`, { progress: true }) : null;
  const step = (pct, message) => progress?.update?.({ pct, message });

  const needDir = Object.keys(images).length || (data.maps ?? []).some(m => m.image?.startsWith("gen:"));
  if ( needDir ) await ensureDir(dir);
  const imgPath = async name => {
    if ( !name ) return null;
    if ( uploaded[name] ) return uploaded[name];
    if ( name.startsWith("art/") ) return null;
    if ( name.startsWith("gen:") ) {
      const file = `${name.replace(/[^\w-]+/g, "-")}.jpg`;
      return (uploaded[name] = await upload(dir, file, await genImage(name)));
    }
    if ( !images[name] || !/^[\w.-]+$/.test(name) ) return null;
    return (uploaded[name] = await upload(dir, name, b64Blob(images[name], name)));
  };

  // Folders
  const jRoot = await folder("JournalEntry", campaign);
  const jFolders = {};
  for ( const [type, label] of Object.entries(TYPE_FOLDERS) ) {
    if ( data.entries.some(e => (TYPE_FOLDERS[e.type] ? e.type : "note") === type) ) jFolders[type] = await folder("JournalEntry", label, jRoot);
  }

  // Pass 1: journal entries (so links can resolve)
  const journals = new Map();
  let i = 0;
  for ( const e of data.entries ) {
    step(0.05 + (0.35 * (i++ / data.entries.length)), `Wiki: ${e.title}`);
    const type = TYPE_FOLDERS[e.type] ? e.type : "note";
    const [doc, created] = await upsert(JournalEntry.implementation, game.journal, e.id,
      { name: e.title || "Untitled", folder: jFolders[type].id });
    journals.set(e.id, doc); count(created); stats.journals++;
  }
  const byTitle = new Map(data.entries.map(e => [String(e.title).trim().toLowerCase(), journals.get(e.id)]));
  const link = (t, label) => {
    const txt = document.createElement("textarea"); txt.innerHTML = t;
    const raw = txt.value.trim();
    const doc = byTitle.get(raw.toLowerCase());
    return doc ? `@UUID[${doc.uuid}]{${label || raw}}` : `<em>${label || t}</em>`;
  };

  // NPC actors
  const npcs = data.entries.filter(e => e.type === "npc");
  const aFolder = npcs.length ? await folder("Actor", `${campaign} NPCs`) : null;
  const actors = new Map();
  for ( const e of npcs ) {
    step(0.4 + (0.2 * (actors.size / npcs.length)), `NPC: ${e.title}`);
    const speciesName = (e.body.match(/^\*\*[^*]*\*\*\s*·\s*([^·\n]+)/)?.[1] ?? "").trim();
    const species = await speciesItem(speciesName);
    const art = (await imgPath(e.img)) ?? species?.img?.replace(/\.webp$/, "-art.webp") ?? null;
    const token = species?.img ?? art;
    const existing = byFlag(game.actors, e.id);
    const actorData = {
      name: e.title || "NPC", folder: aFolder.id,
      system: { details: { biography: { value: md(e.body, link) } } }
    };
    if ( art ) Object.assign(actorData, { img: art, prototypeToken: { name: e.title, texture: { src: token } } });
    if ( !existing ) {
      actorData.type = "npc";
      actorData.system.details.type = { value: "humanoid", subtype: speciesName };
      actorData.prototypeToken ??= {};
      Object.assign(actorData.prototypeToken, { name: e.title, displayName: CONST.TOKEN_DISPLAY_MODES.HOVER, disposition: CONST.TOKEN_DISPOSITIONS.NEUTRAL });
    }
    const [actor, created] = await upsert(Actor.implementation, game.actors, e.id, actorData);
    if ( created && species ) {
      const item = game.items.fromCompendium(species);
      await actor.createEmbeddedDocuments("Item", [item]);
      if ( !actor.system.details.type?.subtype ) await actor.update({ "system.details.type.subtype": speciesName });
    }
    actors.set(e.id, actor); count(created); stats.actors++;
  }

  // Pass 2: journal page content
  i = 0;
  const pinsFor = id => (data.maps ?? []).filter(m => m.pins.some(p => p.entryId === id)).map(m => m.name);
  for ( const e of data.entries ) {
    step(0.6 + (0.15 * (i++ / data.entries.length)), `Wiki: ${e.title}`);
    const doc = journals.get(e.id);
    const actor = actors.get(e.id);
    const img = await imgPath(e.img) ?? (e.img?.startsWith("art/") ? actor?.img : null);
    let html = "";
    if ( img ) html += `<p><img src="${esc(img)}" style="max-width:100%;max-height:420px"></p>`;
    if ( actor ) html += `<p><strong>Actor:</strong> @UUID[${actor.uuid}]{${esc(actor.name)}}</p>`;
    html += md(e.body, link);
    const tags = (e.tags ?? []).filter(Boolean);
    if ( tags.length ) html += `<p><em>Tags: ${tags.map(esc).join(", ")}</em></p>`;
    const backlinks = data.entries.filter(o => (o.id !== e.id) && new RegExp(`\\[\\[\\s*${String(e.title).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*(\\]\\]|\\|)`, "i").test(o.body || ""));
    if ( backlinks.length ) html += `<hr><p><strong>Linked from:</strong> ${backlinks.map(o => `@UUID[${journals.get(o.id).uuid}]{${esc(o.title)}}`).join(", ")}</p>`;
    const maps = pinsFor(e.id);
    if ( maps.length ) html += `<p><strong>On maps:</strong> ${maps.map(esc).join(", ")}</p>`;
    await upsertPage(doc, e.title || "Entry", html, 0, "main");
  }

  // Maps -> scenes
  const maps = data.maps ?? [];
  const sFolder = maps.length ? await folder("Scene", campaign) : null;
  i = 0;
  for ( const m of maps ) {
    step(0.75 + (0.15 * (i++ / maps.length)), `Map: ${m.name}`);
    const src = await imgPath(m.image);
    const { width, height } = src ? await imageSize(src) : { width: 2400, height: 1600 };
    const notes = m.pins.map(p => {
      const entry = p.entryId ? journals.get(p.entryId) : null;
      return {
        x: Math.round(p.x * width), y: Math.round(p.y * height),
        entryId: entry?.id ?? null, text: p.label || entry?.name || "",
        texture: { src: PIN_ICON, tint: p.color || "#ff2e97" }, iconSize: 48, fontSize: 28,
        textColor: p.color || "#ffffff", global: true,
        flags: { [NEON_ID]: { [FLAG]: p.id, notes: p.notes ?? "" } }
      };
    });
    const existing = byFlag(game.scenes, m.id);
    const sceneData = {
      name: m.name || "Map", folder: sFolder.id, width, height, padding: 0,
      backgroundColor: "#05020c", grid: { type: CONST.GRID_TYPES.GRIDLESS },
      tokenVision: false, fog: { exploration: false }
    };
    if ( existing ) {
      await existing.update({ name: sceneData.name, width, height });
      const level = existing.levels.contents[0];
      if ( src && level ) await level.update({ "background.src": src });
      const old = existing.notes.filter(n => n.getFlag(NEON_ID, FLAG));
      if ( old.length ) await existing.deleteEmbeddedDocuments("Note", old.map(n => n.id));
      if ( notes.length ) await existing.createEmbeddedDocuments("Note", notes);
      count(false);
    } else {
      sceneData.levels = [{ name: m.name || "Map", background: { src: src ?? null, color: "#05020c" } }];
      sceneData.notes = notes;
      foundry.utils.setProperty(sceneData, `flags.${NEON_ID}.${FLAG}`, m.id);
      const scene = await Scene.implementation.create(sceneData);
      try {
        const thumb = src ? await Promise.race([scene.createThumbnail(), new Promise(r => setTimeout(r, 15000))]) : null;
        if ( thumb?.thumb ) await scene.update({ thumb: thumb.thumb });
      } catch(err) { console.warn("neon-odyssey | scene thumbnail", err); }
      count(true);
    }
    stats.scenes++;
  }

  // Sessions -> one journal, one page per session
  const sessions = (data.sessions ?? []).slice().sort((a, b) => (a.number ?? 0) - (b.number ?? 0));
  if ( sessions.length ) {
    step(0.92, "Sessions");
    const [sj, created] = await upsert(JournalEntry.implementation, game.journal, `sessions:${slug(campaign)}`,
      { name: `${campaign}: Sessions`, folder: jRoot.id });
    count(created);
    for ( const s of sessions ) {
      const sec = (title, body) => body ? `<h2>${title}</h2>${body}` : "";
      const linked = (s.links ?? []).map(id => journals.get(id)).filter(Boolean);
      const log = (s.log ?? []).map(l => `<li><strong>${new Date(l.t).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</strong> ${inline(esc(l.text), link)}</li>`).join("");
      const html = `<p><strong>Session ${s.number ?? ""}</strong> · ${esc(s.date ?? "")} · ${esc(cap(s.status ?? ""))}</p>`
        + sec("Goals", md(s.goals, link))
        + sec("Scenes", (s.scenes ?? []).length ? `<ul>${s.scenes.map(sc => `<li>${sc.done ? "&#9745;" : "&#9744;"} ${inline(esc(sc.text), link)}</li>`).join("")}</ul>` : "")
        + sec("Linked Entries", linked.length ? `<p>${linked.map(d => `@UUID[${d.uuid}]{${esc(d.name)}}`).join(", ")}</p>` : "")
        + sec("Prep Notes", md(s.prep, link))
        + sec("Play Log", log ? `<ul>${log}</ul>` : "")
        + sec("Recap", md(s.summary, link))
        + sec("Loot", md(s.loot, link))
        + sec("Threads for Next Time", md(s.threads, link));
      await upsertPage(sj, s.title || `Session ${s.number}`, html, (s.number ?? 0) * 100, s.id);
      stats.sessions++;
    }
  }

  step(1, "Done");
  const msg = `Imported "${campaign}": ${stats.journals} wiki entries, ${stats.actors} NPCs, ${stats.scenes} maps, ${stats.sessions} sessions (${stats.created} new, ${stats.updated} updated).`;
  if ( notify ) ui.notifications.info(msg);
  return stats;
}

export function neonPickDmCampaign() {
  const input = document.createElement("input");
  input.type = "file";
  input.accept = ".json,application/json";
  input.onchange = async () => {
    const file = input.files?.[0];
    if ( !file ) return;
    try {
      const data = JSON.parse(await file.text());
      await neonImportDmCampaign(data);
    } catch(err) {
      console.error("neon-odyssey | Neon Odyssey DM import failed", err);
      ui.notifications.error(`Neon Odyssey DM import failed: ${err.message}`);
    }
  };
  input.click();
}

Hooks.on("renderJournalDirectory", (app, html) => {
  if ( !game.user.isGM ) return;
  const root = html instanceof HTMLElement ? html : html[0];
  const actions = root?.querySelector(".header-actions");
  if ( !actions || actions.querySelector(".neon-dm-import") ) return;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "neon-dm-import";
  btn.innerHTML = `<i class="fa-solid fa-satellite-dish" inert></i><span>Import from Neon Odyssey DM</span>`;
  btn.addEventListener("click", ev => { ev.preventDefault(); neonPickDmCampaign(); });
  actions.after(btn);
});

Hooks.once("init", () => {
  const mod = game.modules.get(NEON_ID);
  mod.api = { ...(mod.api ?? {}), importDmCampaign: neonImportDmCampaign, pickDmCampaign: neonPickDmCampaign };
});
