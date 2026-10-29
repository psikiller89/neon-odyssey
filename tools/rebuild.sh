#!/bin/bash
set -e
cd ~/work/build
for s in gen_spells gen_items pack_contents gen_classes fix_refs fix_machinist fix_invention fix_ac gen_origins add_lineages gen_bestiary gen_summons gen_codex link_summons gen_vehicles gen_rules fix_audit fix_uses fix_reports fix_subclass3 add_conditions; do
  echo "== $s"; python3 $s.py 2>&1 | grep -v "layout\|Consider" | tail -3
done
python3 ~/work/neon-odyssey/tools/neon_icons.py
cd ~/work/neon-odyssey && export PATH=~/work/node-v20.18.0-linux-x64/bin:$PATH && node build.mjs
