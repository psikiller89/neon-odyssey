#!/usr/bin/env python3
"""Round 10: modern Musician's Instruments (book variants) and Icon tool choice."""
import os, yaml
OUT = os.path.expanduser('~/work/neon-odyssey/packs/_source')
T = os.path.join(OUT, 'items/tools')
UT = '<p><strong>Utilize:</strong> Play a known tune (DC 10), or improvise a song (DC 15)</p>'
FOCUS = '<p>This is a Musician’s Instrument: an Icon can use it as a Spellcasting Focus.</p>'
INST = [  # key, id, name, price $, weight lb, flavour
    ('brass', 'neonInstBrass001', 'Brass Wind (Trumpet, Saxophone)', 1500, 2, 'Valved horns and saxophones with built-in pickups for stage amps.'),
    ('drumpad', 'neonInstDrumPad1', 'Drum Pad', 300, 1, 'A single electronic drum pad loaded with sampled kits.'),
    ('drumkit', 'neonInstDrumKit1', 'Electronic Drum Kit', 1500, 50, 'A full set of mesh-head drums and cymbal pads.'),
    ('keytar', 'neonInstKeytar01', 'Keytar', 1500, 5, 'Portable keys worn on a strap.'),
    ('synth', 'neonInstSynth001', 'Synthesizer', 3000, 300, 'Standing keys rig with modular synth racks.'),
    ('mic', 'neonInstMicro001', 'Microphone', 250, 1, 'A vocal mic with autotune and effects processing.'),
    ('woodwind', 'neonInstWoodWnd1', 'Wood Wind (Flute, Clarinet)', 100, 1, 'Flutes, clarinets and wind controllers.'),
    ('eviolin', 'neonInstEViolin1', 'Electric Violin', 1500, 1, 'A small stringed instrument with a solid body.'),
    ('eguitar', 'neonInstEGuitar1', 'Electric Guitar', 2000, 5, 'A medium stringed instrument.'),
    ('ebass', 'neonInstEBass001', 'Electric Upright Bass', 3000, 80, 'A large stringed instrument.'),
]
base = yaml.safe_load(open(os.path.join(T, 'musicians-instrument.yml')))
for key, _id, name, price, wt, flav in INST:
    d = yaml.safe_load(yaml.safe_dump(base))
    d['_id'] = _id; d['name'] = name
    s = d['system']; s['price']['value'] = price; s['weight']['value'] = wt
    s['type'] = {'value': 'music', 'baseItem': key}
    s['description']['value'] = f'<p>{flav}</p><p><strong>Ability:</strong> Charisma</p><p><strong>Weight:</strong> {wt} lb.</p>{UT}{FOCUS}'
    d['_key'] = f'!items!{_id}'
    slug = name.lower().split(' (')[0].replace(' ', '-')
    yaml.safe_dump(d, open(os.path.join(T, f'instrument-{slug}.yml'), 'w'), sort_keys=False, allow_unicode=True, width=200)
# generic entry becomes a reference to the variants
f = os.path.join(T, 'musicians-instrument.yml'); d = yaml.safe_load(open(f))
lst = ''.join(f'<li>@UUID[Compendium.neon-odyssey.items.Item.{i}]{{{n}}} (${p:,}, {w} lb.)</li>' for _, i, n, p, w, _f in INST)
d['system']['description']['value'] = f'<p><strong>Ability:</strong> Charisma</p><p><strong>Weight:</strong> Varies</p>{UT}<p>Pick a specific instrument:</p><ul>{lst}</ul>'
yaml.safe_dump(d, open(f, 'w'), sort_keys=False, allow_unicode=True, width=200)
# Icon: Artist's Supplies or 3 Musician's Instruments
f = os.path.join(OUT, 'classes/icon/icon.yml'); t = open(f).read()
if 'neonIconTools001' not in t:
    blk = """    neonIconTools001:
      _id: neonIconTools001
      type: Trait
      configuration:
        mode: default
        allowReplacements: false
        grants: []
        choices:
        - count: 3
          pool:
          - tool:art:painter
          - tool:music:*
      value:
        chosen: []
      level: 1
      title: Tool Proficiencies
      hint: Pick Artist’s Supplies, or 3 Musician’s Instruments.
      classRestriction: primary
"""
    t = t.replace('    iFuxb8gJBCVtfegb:\n', blk + '    iFuxb8gJBCVtfegb:\n', 1); open(f, 'w').write(t)
print('round10 ok')
