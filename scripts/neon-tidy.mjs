const NEON_ID = "neon-odyssey";
const useTheme = () => game.settings.get(NEON_ID, "tidyTheme");

Hooks.once("init", () => {
  game.settings.register(NEON_ID, "tidyTheme", {
    name: "Neon Odyssey Theme for Tidy 5e",
    hint: "When Tidy 5e Sheets is active, give all its sheets the Neon Odyssey look. The \"Neon Odyssey (Tidy 5e)\" sheets always have it.",
    scope: "world",
    config: true,
    type: Boolean,
    default: true,
    requiresReload: true
  });
});

const NEON_TIDY_TABS = {
  attributes: "Outrunner",
  inventory: "Gear",
  spellbook: "Spells",
  features: "Abilities",
  effects: "Status",
  biography: "Dossier"
};

function renameTidyTabs(element) {
  for ( const [id, label] of Object.entries(NEON_TIDY_TABS) ) {
    for ( const tab of element.querySelectorAll(`.tab-option[data-tab-id="${id}"]`) ) {
      const title = tab.querySelector(".tab-title");
      if ( title && title.textContent !== label ) title.textContent = label;
      if ( tab.getAttribute("title") !== label ) tab.setAttribute("title", label);
    }
  }
}

const NEON_TIDY_NPC_TABS = { inventory: "Gear", effects: "Status", biography: "Dossier" };

/* Selectable "Neon Odyssey (Tidy 5e)" sheets: Tidy 5e's sheets, always with the Neon look. */
function neonRegisterTidySheets() {
  if ( !game.modules.get("tidy5e-sheet")?.active || neonRegisterTidySheets.done ) return;
  for ( const [type, label] of [["character", "Neon Odyssey Sheet (Tidy 5e)"], ["npc", "Neon Odyssey NPC Sheet (Tidy 5e)"]] ) {
    const entry = Object.entries(CONFIG.Actor.sheetClasses[type] ?? {}).find(([k]) => /^dnd5e\.Tidy5e(Character|Npc)Sheet/.test(k));
    const Base = entry?.[1]?.cls;
    if ( !Base ) continue;
    neonRegisterTidySheets.done = true;
    const Sheet = class extends Base {
      static DEFAULT_OPTIONS = { classes: ["neon-tidy", "neon-tidy-sheet"] };
    };
    Object.defineProperty(Sheet, "name", { value: type === "npc" ? "NeonTidyNpcSheet" : "NeonTidyCharacterSheet" });
    foundry.applications.apps.DocumentSheetConfig.registerSheet(Actor, NEON_ID, Sheet, { types: [type], label, makeDefault: false });
  }
}
Hooks.once("setup", neonRegisterTidySheets);
Hooks.once("tidy5e-sheet.ready", () => neonRegisterTidySheets());
Hooks.once("ready", neonRegisterTidySheets);

Hooks.on("renderActorSheetV2", (app, element) => {
  if ( !element?.classList?.contains("tidy5e-sheet") ) return;
  if ( !useTheme() && !element.classList.contains("neon-tidy-sheet") ) return;
  element.classList.add("neon-tidy");
  if ( element.classList.contains("npc") ) {
    for ( const [id, label] of Object.entries(NEON_TIDY_NPC_TABS) ) for ( const t of element.querySelectorAll(`.tab-option[data-tab-id="${id}"] .tab-title`) ) t.textContent = label;
  }
  if ( !element.classList.contains("character") ) return;
  renameTidyTabs(element);
  if ( element._neonTabObserver ) return;
  element._neonTabObserver = new MutationObserver(() => renameTidyTabs(element));
  element._neonTabObserver.observe(element, { childList: true, subtree: true, characterData: true });
});

Hooks.once("tidy5e-sheet.ready", api => {
  try {
    api.registerCharacterContent(new api.models.HtmlContent({
      html: data => {
        const gn = Number(data?.actor?.system?.currency?.gn ?? 0);
        return `<span class="neon-tidy-credits" data-tooltip="Galactic Notes"><b>$</b> ${gn.toLocaleString()} <small>GN</small></span>`;
      },
      injectParams: { selector: '[data-tidy-sheet-part="name-header-row"]', position: "beforeend" },
      enabled: () => useTheme()
    }));
  } catch (err) {
    console.error(`${NEON_ID} | Tidy 5e integration failed`, err);
  }
});
