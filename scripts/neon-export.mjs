/* Export a character to the official Neon Odyssey form-fillable PDF sheet. */
const NEON_ID = "neon-odyssey";
const SHEET_PDF = "modules/neon-odyssey/assets/neon-odyssey-character-sheet.pdf";
const ABILITY_SUFFIX = { str: "", dex: " 1", con: " 2", int: " 3", wis: " 4", cha: " 5" };
const SKILL_ROWS = [["acr", "Skill 1"], ["ani", "Skill"], ["arc", "Skill 3"], ["ath", "Skill 2"], ["cmp", "Skill 5"], ["dec", "Skill 4"],
  ["his", "Skill 9"], ["ins", "Skill 6"], ["itm", "Skill 10"], ["inv", "Skill 7"], ["med", "Skill 11"], ["nat", "Skill 8"],
  ["prc", "Skill 15"], ["prf", "Skill 12"], ["per", "Skill 16"], ["rel", "Skill 13"], ["slt", "Skill 17"], ["ste", "Skill 14"],
  ["sur", "Skill 19"], ["tec", "Skill 18"]];
const SPELL_ROWS = [1, 2, 3, 4, 5, 7, 6, 8, 9, 13, 11, 15, 10, 14, 12, 16, 17, 21, 19, 23, 18, 22, 20, 24, 25, 29, 27, 31, 26, 30, 28, 32];
const SLOT_BOXES = { 1: [1, 2, 3, 4], 2: [5, 6, 7], 3: [9, 10, 11], 4: [13, 16, 19], 5: [14, 17, 20], 6: [15, 18], 7: [25, 28], 8: [26], 9: [27] };
const BIG_FIELDS = new Set(["Level", "Armor", "Initiative", "Speed", "Speed 1", "HP Temp", "HP Max", "HD Spent", "HD Max",
  "Spell Attack Bonus", "Spell Save DC", "Spellcasting Modifier", "Score STR 6", "Score STR 7", ...Object.values(ABILITY_SUFFIX).map(s => `Mod STR${s}`)]);
const CHAR_MAP = { "−": "-", "‐": "-", "‑": "-", "×": "x", "≥": ">=", "≤": "<=", "→": "->", "½": "1/2", "¼": "1/4", "¾": "3/4", "\u00a0": " " };

const signed = n => (Number(n) >= 0 ? `+${Number(n)}` : `${Number(n)}`);
const stripHTML = html => {
  const div = document.createElement("div");
  div.innerHTML = String(html ?? "").replace(/<\/(p|li|h\d|div)>/gi, "\n").replace(/<br\s*\/?>/gi, "\n");
  return div.textContent.replace(/\n{3,}/g, "\n\n").trim();
};
const label = v => (typeof v === "string" ? v : v?.label ?? "");
function traitLabel(key) {
  try { return dnd5e.documents.Trait.keyLabel(key) || key.split(":").pop(); } catch { return key.split(":").pop(); }
}
function traitList(trait, prefix, cfg) {
  const t = trait ?? {};
  const out = [...(t.value ?? [])].map(k => (cfg ? label(cfg[k]) || k : traitLabel(`${prefix}:${k}`)));
  for ( const c of String(t.custom ?? "").split(";") ) if ( c.trim() ) out.push(c.trim());
  return out;
}
const isCopy = i => !!i.getFlag("dnd5e", "cachedFor");

function actionData(item) {
  const acts = item.system.activities ? [...item.system.activities] : [];
  const act = acts.find(a => a.type === "attack") ?? acts.find(a => a.type === "save") ?? acts.find(a => a.labels?.damage?.length);
  if ( !act ) return null;
  const lb = act.labels ?? {};
  const save = lb.save ? lb.save.replace(/DC\s*(\d+)\s*(\w{3})\w*/i, (m, dc, ab) => `DC ${dc} ${ab.toUpperCase()}`) : "";
  const damage = (lb.damage ?? lb.damages ?? []).map(d => d.label).filter(Boolean).join(", ");
  return { act, bonus: lb.toHit ?? save, damage, range: lb.range ?? item.labels?.range ?? "" };
}

export function neonSheetData(actor) {
  const s = actor.system; const f = {}; const checks = []; const notes = [];
  const classes = actor.itemTypes.class.sort((a, b) => b.system.levels - a.system.levels);
  const subs = actor.itemTypes.subclass;
  const multi = classes.length > 1;
  f["Character Name"] = actor.name;
  f["Player"] = game.users.find(u => !u.isGM && actor.testUserPermission(u, "OWNER"))?.name ?? "";
  f["Class"] = classes.map(c => (multi ? `${c.name} ${c.system.levels}` : c.name)).join(" / ");
  f["Subclass"] = subs.map(c => c.name).join(" / ");
  f["Species"] = actor.itemTypes.race[0]?.name ?? s.details.race?.name ?? "";
  const origin = actor.itemTypes.feat.find(i => /-origin$/.test(i.system.identifier ?? ""));
  f["Homeworld"] = actor.getFlag(NEON_ID, "homeworld") ?? origin?.name.replace(/ Origin$/, "") ?? "";
  f["Level"] = s.details.level ?? "";
  f["XP"] = s.details.xp?.value || "";
  f["Armor"] = s.attributes.ac?.value ?? "";
  f["Initiative"] = signed(s.attributes.init?.total ?? 0);
  f["Speed"] = s.attributes.movement?.walk ?? "";
  f["Size"] = (s.traits.size ?? "").toUpperCase().slice(0, 3);
  if ( s.attributes.inspiration ) checks.push("Heroic Inspiration");

  const hp = s.attributes.hp ?? {};
  f["Speed 1"] = hp.value ?? ""; f["HP Max"] = hp.max ?? ""; f["HP Temp"] = hp.temp || "";
  f["HD Max"] = classes.map(c => `${c.system.levels}${c.system.hd?.denomination ?? ""}`).join(" ");
  f["HD Spent"] = classes.reduce((n, c) => n + (c.system.hd?.spent ?? 0), 0) || "";
  for ( let i = 1; i <= 3; i++ ) if ( (s.attributes.death?.success ?? 0) >= i ) checks.push(`Death Save ${i}`);
  for ( let i = 1; i <= 3; i++ ) if ( (s.attributes.death?.failure ?? 0) >= i ) checks.push(`Death Save ${i + 3}`);
  for ( let i = 1; i <= 6; i++ ) if ( (s.attributes.exhaustion ?? 0) >= i ) checks.push(`Exhaustion ${i}`);
  const res = [
    ...traitList(s.traits.dr, "dr", CONFIG.DND5E.damageTypes),
    ...traitList(s.traits.di, "di", CONFIG.DND5E.damageTypes).map(x => `${x} (immune)`),
    ...traitList(s.traits.dv, "dv", CONFIG.DND5E.damageTypes).map(x => `${x} (vulnerable)`),
    ...traitList(s.traits.ci, "ci", CONFIG.DND5E.conditionTypes).map(x => `${x} (immune)`)
  ];
  f["Resistances"] = res.join(", ");

  for ( const [k, suf] of Object.entries(ABILITY_SUFFIX) ) {
    const a = s.abilities[k]; if ( !a ) continue;
    f[`Score STR${suf}`] = a.value; f[`Mod STR${suf}`] = signed(a.mod); f[`Save STR${suf}`] = signed(a.save?.value ?? a.mod);
    if ( a.proficient >= 1 ) checks.push(`Ability Save${suf}`);
  }
  f["Score STR 6"] = signed(s.attributes.prof ?? 0);
  f["Score STR 7"] = s.skills.prc?.passive ?? "";
  SKILL_ROWS.forEach(([k, field], i) => {
    const sk = s.skills[k]; if ( !sk ) return;
    f[field] = signed(sk.total ?? sk.mod ?? 0);
    if ( sk.value >= 1 ) checks.push(i ? `Skills ${i}` : "Skills");
  });

  // Weapons, cantrips & damage.
  const attackItems = [
    ...actor.itemTypes.weapon.filter(i => i.system.equipped),
    ...actor.itemTypes.spell.filter(i => (i.system.level === 0) && !isCopy(i)),
    ...actor.itemTypes.weapon.filter(i => !i.system.equipped)
  ];
  const attacks = attackItems.map(i => ({ item: i, d: actionData(i) })).filter(x => x.d);
  attacks.forEach(({ item, d }, i) => {
    const sfx = i ? ` ${i}` : "";
    const props = item.type === "weapon" ? [...(item.system.properties ?? [])].map(p => label(CONFIG.DND5E.itemProperties[p])).filter(Boolean) : [];
    const row = [item.name, d.bonus, d.damage, [d.range, ...props].filter(Boolean).join(", ")];
    if ( i < 10 ) [f[`Attack Name${sfx}`], f[`Attack Bonus${sfx}`], f[`Attack Damage${sfx}`], f[`Attack Notes${sfx}`]] = row;
    else notes.push(`Attack: ${row.filter(Boolean).join(" | ")}`);
  });

  // Features, feats, proficiencies.
  const feats = actor.itemTypes.feat;
  const useText = i => {
    const u = i.system.uses;
    return u?.max ? ` (${u.value ?? u.max}/${u.max})` : "";
  };
  f["Features and Traits"] = feats.filter(i => i.system.type?.value !== "feat").map(i => `${i.name}${useText(i)}`);
  const bg = actor.itemTypes.background[0];
  f["Feats and Professions"] = [bg ? `Background: ${bg.name}` : "", ...feats.filter(i => i.system.type?.value === "feat").map(i => `${i.name}${useText(i)}`)].filter(Boolean).join("\n");
  f["Weapon Proficiencies"] = traitList(s.traits.weaponProf, "weapon").join(", ");
  const tools = []; const vehicles = [];
  for ( const [k, t] of Object.entries(s.tools ?? {}) ) {
    if ( !(t.value >= 1) ) continue;
    if ( k in CONFIG.DND5E.vehicleTypes ) vehicles.push(label(CONFIG.DND5E.vehicleTypes[k]) || k);
    else tools.push(traitLabel(`tool:${k}`));
  }
  f["Tool Proficiencies"] = tools.join(", ");
  f["Vehicle Proficiencies"] = vehicles.join(", ");
  const armor = new Set(s.traits.armorProf?.value ?? []);
  ["lgt", "med", "hvy", "shl"].forEach((k, i) => { if ( armor.has(k) ) checks.push(`Armor Proficiency ${i + 1}`); });
  const comms = Object.entries(s.traits.languages?.communication ?? {}).filter(([, c]) => c?.value)
    .map(([k, c]) => `${label(CONFIG.DND5E.communicationTypes?.[k]) || k} ${c.value} ${c.units ?? "ft"}`);
  f["Languages"] = [...traitList(s.traits.languages, "languages"), ...comms].join(", ");

  // Equipment.
  const physical = actor.items.filter(i => ("quantity" in i.system) && !isCopy(i));
  const isMagic = i => !!i.system.attunement || (i.system.rarity && (i.system.rarity !== "")) || i.system.properties?.has?.("mgc");
  f["Equipment"] = physical.filter(i => !isMagic(i)).map(i => `${i.name}${i.system.quantity > 1 ? ` x${i.system.quantity}` : ""}${i.system.equipped ? " (E)" : ""}`).join("\n");
  physical.filter(isMagic).forEach((i, n) => {
    if ( n < 6 ) {
      f[`Magic Item${n ? ` ${n}` : ""}`] = i.name;
      if ( i.system.attuned ) checks.push(`Magic Item Attunement ${n + 1}`);
    } else notes.push(`Magic item: ${i.name}${i.system.attuned ? " (attuned)" : ""}`);
  });
  f["Galactic Notes"] = s.currency?.gn ?? "";

  // Spellcasting.
  const ab = s.attributes.spellcasting;
  if ( ab && s.abilities[ab] ) {
    const idx = { int: 1, wis: 2, cha: 3 }[ab]; if ( idx ) checks.push(`Spellcasting Ability ${idx}`);
    f["Spellcasting Modifier"] = signed(s.abilities[ab].mod);
    f["Spell Save DC"] = s.attributes.spell?.dc ?? "";
    f["Spell Attack Bonus"] = signed(s.attributes.spell?.attack ?? (s.abilities[ab].mod + (s.attributes.prof ?? 0)));
  }
  const slots = {}; const pact = s.spells?.pact;
  for ( let l = 1; l <= 9; l++ ) {
    const sl = s.spells?.[`spell${l}`] ?? {};
    slots[l] = { max: Number(sl.max) || 0, spent: Math.max(0, (Number(sl.max) || 0) - (Number(sl.value) || 0)) };
  }
  if ( pact?.max && pact.level ) {
    slots[pact.level].max += Number(pact.max); slots[pact.level].spent += Math.max(0, pact.max - (pact.value ?? 0));
    notes.unshift(`Pact slots: ${pact.value ?? 0}/${pact.max} at level ${pact.level} (counted in Level ${pact.level} slots).`);
  }
  for ( let l = 1; l <= 9; l++ ) {
    if ( slots[l].max ) f[`Total ${l}`] = slots[l].max;
    SLOT_BOXES[l].slice(0, slots[l].spent).forEach(n => checks.push(`Spell Expended ${n}`));
  }
  const seen = new Set();
  const spells = actor.itemTypes.spell.filter(i => !isCopy(i) && ((i.system.level === 0) || (i.system.prepared >= 1) || (i.system.method && !["spell", "prepared"].includes(i.system.method))))
    .sort((a, b) => (a.system.level - b.system.level) || a.name.localeCompare(b.name))
    .filter(i => !seen.has(i.name) && seen.add(i.name));
  spells.forEach((sp, i) => {
    const props = sp.system.properties ?? new Set();
    const feat = [props.has("concentration") ? "C" : "", props.has("ritual") ? "R" : "", props.has("material") ? `M${sp.system.materials?.cost ? "*" : ""}` : ""].filter(Boolean).join(", ");
    const d = actionData(sp);
    const row = [sp.system.level === 0 ? "C" : sp.system.level, sp.name, sp.labels?.activation ?? "", sp.labels?.range ?? "", feat, sp.labels?.school ?? "",
      d ? [d.bonus, d.damage].filter(Boolean).join("; ") : (sp.labels?.duration ?? ""), sp.system.source?.page ?? ""];
    if ( i < SPELL_ROWS.length ) {
      const n = SPELL_ROWS[i];
      ["Spell Level", "Spell Name", "Spell Casting Time", "Spell Range", "Spell Features", "Spell School", "Spell Notes", "Spell Page"].forEach((c, j) => f[`${c} ${n}`] = row[j]);
    } else notes.push(`Spell: ${row[1]} (${row[0] === "C" ? "cantrip" : `level ${row[0]}`})`);
  });

  const d = s.details;
  const personality = [["Personality", d.trait], ["Ideals", d.ideal], ["Bonds", d.bond], ["Flaws", d.flaw], ["Appearance", d.appearance]]
    .filter(([, v]) => v && stripHTML(v)).map(([k, v]) => `${k}: ${stripHTML(v)}`);
  const bio = stripHTML(d.biography?.value);
  f["Notes"] = [...notes, ...personality, bio ? (bio.length > 2500 ? `${bio.slice(0, 2500)}...` : bio) : ""].filter(Boolean).join("\n");
  return { fields: f, checks };
}

function fitSize(font, text, w, h, multiline, max) {
  for ( let size = max; size >= 4; size -= 0.5 ) {
    if ( !multiline ) { if ( font.widthOfTextAtSize(text, size) <= w - 4 ) return size; continue; }
    let lines = 0;
    for ( const para of text.split("\n") ) {
      let cur = "";
      lines++;
      for ( const word of para.split(" ") ) {
        const next = cur ? `${cur} ${word}` : word;
        if ( font.widthOfTextAtSize(next, size) > w - 4 ) { lines++; cur = word; } else cur = next;
      }
    }
    if ( lines * size * 1.2 <= h - 2 ) return size;
  }
  return 4;
}

export async function neonBuildSheetPdf(actor) {
  const { PDFDocument, StandardFonts, PDFTextField, PDFCheckBox } = await import("../lib/pdf-lib.esm.min.js");
  const bytes = await (await fetch(foundry.utils.getRoute(SHEET_PDF))).arrayBuffer();
  const pdf = await PDFDocument.load(bytes);
  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const charset = new Set(font.getCharacterSet());
  const clean = v => [...String(v ?? "").normalize("NFC")].map(c => CHAR_MAP[c] ?? c)
    .join("").split("").filter(c => (c === "\n") || charset.has(c.codePointAt(0))).join("");
  const form = pdf.getForm();
  for ( const field of form.getFields() ) if ( (field instanceof PDFTextField) && field.isRichFormatted() ) field.disableRichFormatting();
  const { fields, checks } = neonSheetData(actor);
  if ( Array.isArray(fields["Features and Traits"]) ) {
    const list = fields["Features and Traits"]; const field = form.getTextField("Features and Traits");
    const { width, height } = field.acroField.getWidgets()[0].getRectangle();
    const asLines = list.join("\n");
    fields["Features and Traits"] = fitSize(font, clean(asLines), width, height, true, 9) >= 6.5 ? asLines : list.join(" • ");
  }
  for ( const [name, value] of Object.entries(fields) ) {
    const field = form.getFieldMaybe(name);
    if ( !(field instanceof PDFTextField) ) continue;
    const text = clean(value);
    if ( !text ) continue;
    const multiline = field.isMultiline();
    field.setText(multiline ? text : text.replace(/\n/g, " "));
    const { width, height } = field.acroField.getWidgets()[0].getRectangle();
    field.setFontSize(fitSize(font, field.getText(), width, height, multiline, BIG_FIELDS.has(name) ? 16 : 9));
  }
  for ( const name of checks ) {
    const field = form.getFieldMaybe(name);
    if ( field instanceof PDFCheckBox ) field.check();
  }
  form.updateFieldAppearances(font);
  return pdf.save();
}

export async function neonExportSheet(actor) {
  try {
    const bytes = await neonBuildSheetPdf(actor);
    foundry.utils.saveDataToFile(bytes, "application/pdf", `${actor.name.replace(/[\\/:*?"<>|]+/g, "_")} - Neon Odyssey Sheet.pdf`);
  } catch(err) {
    console.error("neon-odyssey | Character sheet export failed", err);
    ui.notifications.error(`Neon Odyssey: couldn't export ${actor.name}'s character sheet. See the console (F12) for details.`);
  }
}

Hooks.on("getHeaderControlsActorSheetV2", (app, controls) => {
  const actor = app.document;
  if ( (actor?.type !== "character") || !actor.testUserPermission(game.user, "OBSERVER") ) return;
  if ( controls.some(c => c.action === "neonExportSheet") ) return;
  controls.push({ action: "neonExportSheet", icon: "fa-solid fa-file-pdf", label: "Export Character Sheet (PDF)", ownership: "OBSERVER", onClick: () => neonExportSheet(actor) });
});

Hooks.once("init", () => {
  const mod = game.modules.get(NEON_ID);
  mod.api = { ...(mod.api ?? {}), exportSheet: neonExportSheet, buildSheetPdf: neonBuildSheetPdf, sheetData: neonSheetData };
});
