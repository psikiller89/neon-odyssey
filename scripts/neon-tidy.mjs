const NEON_ID = "neon-odyssey";
const useTheme = () => game.settings.get(NEON_ID, "tidyTheme");

Hooks.once("init", () => {
  game.settings.register(NEON_ID, "tidyTheme", {
    name: "Neon Odyssey Theme for Tidy 5e",
    hint: "When Tidy 5e Sheets is active, give its character sheets the Neon Odyssey look and show only Galactic Notes ($).",
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

Hooks.on("renderActorSheetV2", (app, element) => {
  if (!element?.classList?.contains("tidy5e-sheet") || !useTheme()) return;
  element.classList.add("neon-tidy");
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
