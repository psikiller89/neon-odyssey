# Neon Odyssey: Classes, Subclasses & Spells (Foundry VTT module)

For Foundry VTT v14 with the dnd5e system 6.0.6 (2024 rules). Content comes from *Neon Odyssey Outrunner's Handbook v0.1.1* and *Overdrive Expansion v0.1.1* (Playtest 1).

## Contents
- **Classes & Subclasses**: 13 classes and 52 subclasses (26 from the Handbook, 26 from Overdrive).
- **Class & Subclass Features**: all class features, subclass features and option lists (Esoteric Secrets, Psi Shaping, Hypertech Schematics, Primal Forms, Primal Aspects).
- **Species**: 21 species with all their traits (Size choice, speeds, Darkvision, skill choices, trait activities and uses). Laika and Saurian lineage tables are included in the Lineage trait.
- **Backgrounds & Origin feats**: the book's custom "Outrunner" background (ASI, skills, Computers/Technology, tool, languages, Origin feat choice) and the 14 Homeworld Origin feats. Neon Odyssey languages are registered.
- **Spells**: 94 new Neon Odyssey spells.
- **Equipment**: 49 weapons, 5 armors, 10 weapon/armor modules, 21 tools, ammunition and 94 pieces of outrunning gear, priced in Galactic Notes ($).
- **Art**: class emblems and subclass portraits taken from the books.
- **Spell Lists**: one class spell list per spellcasting class, registered with dnd5e so the spell browser and preparation filters work.

## Automation
- Class level-up Advancements: Hit Points, saving throw and skill proficiency choices (including the new Computers and Technology skills), feature grants by level, subclass choice at level 3, ASI/Epic Boon, scale values, and option choices (Esoteric Secrets, Hypertech Schematics, Psi Shaping).
- Subclass feature grants by level. "X Spells" features grant always-prepared spells at the correct levels.
- Features that rename 2024 PHB features (for example Surge = Rage, Invigorate = Lay on Hands, Cheap Shot = Sneak Attack) reuse the official dnd5e automation (uses, activities, effects, scale values) with Neon Odyssey text.
- New features and spells get Activities generated from their text: uses and recovery, activation, attack, save (DC and ability), damage, healing and temp HP, and higher-level scaling.
- Weapons: attack activities, Powered attacks (they use one of the 25 charges in the Power Cell, plus a Replace Power Cell action), Reload magazine tracking with a Reload action, Burst and Scatter saves (DC 15), Thrown attacks, mastery and ranges. Neon properties (Powered, Burst, Braced, Close Quarters, Reload, Scatter, Pummel) are registered as weapon properties.
- Tools have check activities with the Utilize DCs. Consumables (Acid Vial, Healing Stim, Toxin, etc.) have save, heal or damage activities and are used up when spent.
- Cryptist Occult Magic uses its own slot table (3 slots at level 7, 4 at 13, 5 at 19), applied by `scripts/neon-odyssey.mjs`.

## Install
Unzip into `Data/modules/neon-odyssey` (or install the zip with a manifest host), then enable it in your world.

## Notes
- Some spells and features reference PHB-only spells. These link to the `dnd-players-handbook` module when the spell isn't in the SRD. Without that module, those grants show as missing.
- Generated automation covers the common cases. Complex features may still need manual adjustment.
- Rebuild the packs from YAML: `npm i && node build.mjs`.

## v0.4.0 additions

- **Starting equipment:** each class's A/B/C starting equipment choice grants the real Neon Odyssey items and Galactic Notes.
- **Bestiary & Summons** (Actor compendium):
  - 8 bestiary creatures (Chatterling, Harmonic Kindred, Jellikin, Mindclinger, Omnibot, Pixpal, Spy Drone, Starry Guide) with book art and tokens.
  - 14 summoned creatures (Autonomous Assistant, the 9 spell spirits, Rivet Turret, Ambush/Battle/Swift Form).
  - The Summon spells, Autonomous Assistant, Riveter's Deploy Turret and Primalist's Primal Channel have Summon activities that place the token.
  - 6 planetary vehicles as dnd5e vehicle actors with crew-station actions.
- **Rules journal:** Computers & Technology skills, Aether Exposure, Grid Spiking, equipment rules, Hypertech spellcasting and vehicle rules.
- **Automation:**
  - Laika and Saurian lineages are chosen when the species is added; their passive benefits apply through Active Effects.
  - Conditions named in a feature, spell or item (Prone, Restrained, Frightened…) are attached to its activity so they can be applied to targets.
  - Cryptist and Esper ask for Intelligence or Charisma when the class is added.
  - Packs (Outrunner's Pack etc.) add their contents to your inventory.

## Install

In Foundry: **Add-on Modules → Install Module**, paste this manifest URL:

```
https://github.com/psikiller89/neon-odyssey/releases/latest/download/module.json
```

## Rebuilding

`tools/` contains the Python generators that read the PDFs and write `packs/_source`; `node build.mjs` compiles the packs.
