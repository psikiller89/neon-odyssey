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

Hooks.on("renderActorSheetV2", (app, element) => {
  if (!element?.classList?.contains("tidy5e-sheet") || !useTheme()) return;
  element.classList.add("neon-tidy");
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
