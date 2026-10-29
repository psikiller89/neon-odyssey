/* Neon Odyssey character sheet: a themed variant of the dnd5e character sheet, selectable per character. */
const NEON_ID = "neon-odyssey";
const NEON_TABS = { details: "Outrunner", inventory: "Gear", features: "Abilities", spells: "Spells", effects: "Status", biography: "Dossier" };

Hooks.once("init", () => {
  game.settings.register(NEON_ID, "defaultSheet", {
    name: "Neon Odyssey Sheet by Default",
    hint: "Use the Neon Odyssey character sheet for characters that haven't picked a sheet. Each character can still change sheet from its sheet configuration.",
    scope: "world", config: true, type: Boolean, default: false, requiresReload: true
  });
  const Base = dnd5e.applications.actor.CharacterActorSheet;

  class NeonOdysseySheet extends Base {
    static DEFAULT_OPTIONS = { classes: ["neon-odyssey-sheet"], position: { width: 860, height: 1000 } };
    static TABS = Base.TABS.map(t => ({ ...t, label: NEON_TABS[t.tab] ?? t.label }));

    _onRender(context, options) {
      super._onRender(context, options);
      try { this.#decorate(); } catch(err) { console.error(`${NEON_ID} | sheet decoration failed`, err); }
    }

    #decorate() {
      const el = this.element;
      const actor = this.actor;
      const header = el.querySelector(".sheet-header");
      if ( header && !header.querySelector(".neon-brand") ) {
        header.insertAdjacentHTML("afterbegin", `<div class="neon-brand"><span>Neon Odyssey</span><em>Outrunner Dossier</em></div>`);
      }
      for ( const span of el.querySelectorAll(".sidebar .meter-group .label span, .sidebar .meter-group > .label") ) {
        if ( span.textContent.trim() === game.i18n.localize("DND5E.HitDice") ) span.textContent = "Hit Point Dice";
      }
      for ( const key of ["cmp", "tec"] ) el.querySelectorAll(`.skills [data-key="${key}"]`).forEach(li => li.classList.add("neon-tech"));

      const sidebar = el.querySelector(".sidebar .card");
      if ( sidebar && !el.querySelector(".neon-credits") ) {
        const gn = actor.system.currency?.gn ?? 0;
        const editable = this.isEditable ? "" : "disabled";
        sidebar.insertAdjacentHTML("afterend", `
          <section class="neon-credits">
            <div class="neon-panel-title">Galactic Notes</div>
            <label class="credits"><span class="sym">$</span>
              <input type="text" class="uninput always-interactive" data-neon-currency="gn" value="${gn}" inputmode="numeric" ${editable}>
            </label>
            <div class="neon-panel-title">Grid Spiking</div>
            <div class="neon-quick">
              <button type="button" class="always-interactive" data-neon-skill="cmp"><i class="fas fa-terminal"></i> Computers</button>
              <button type="button" class="always-interactive" data-neon-skill="tec"><i class="fas fa-microchip"></i> Technology</button>
            </div>
          </section>`);
        el.querySelector("[data-neon-currency]")?.addEventListener("change", ev => {
          ev.stopPropagation();
          const raw = ev.currentTarget.value.trim();
          const cur = actor.system.currency?.gn ?? 0;
          const value = /^[+-]/.test(raw) ? cur + (Number(raw) || 0) : Number(raw);
          actor.update({ "system.currency.gn": Math.max(0, Number.isFinite(value) ? Math.floor(value) : cur) });
        });
        el.querySelectorAll("[data-neon-skill]").forEach(b => b.addEventListener("click", ev => {
          actor.rollSkill({ skill: ev.currentTarget.dataset.neonSkill, event: ev });
        }));
      }
    }
  }

  foundry.applications.apps.DocumentSheetConfig.registerSheet(Actor, NEON_ID, NeonOdysseySheet, {
    types: ["character"], label: "Neon Odyssey Sheet", makeDefault: game.settings.get(NEON_ID, "defaultSheet")
  });
});
