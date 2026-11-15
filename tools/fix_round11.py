#!/usr/bin/env python3
"""Round 11: Virus Infection Vector as token statuses (host + Infected attacker) with a slot-restore button."""
import os, yaml, copy
OUT = os.path.expanduser('~/work/neon-odyssey/packs/_source')
F = os.path.join(OUT, 'features/gridrunner/virus/infection-vector-3.yml')
ICON = 'modules/neon-odyssey/icons/neon/'
d = yaml.safe_load(open(F)); IID = d['_id']
save = next(a for a in d['system']['activities'].values() if a['type'] == 'save')
mal = yaml.safe_load(open(os.path.join(OUT, 'features/gridrunner/virus/malware-3.yml')))
util = copy.deepcopy(next(iter(mal['system']['activities'].values())))
eff_tpl = mal['effects'][0]
def rider(i): return {'_id': i, 'riders': {'activity': [], 'effect': [], 'item': []}}
def tgt(count, units='ft', value=''): return {'template': {'contiguous': False, 'units': 'ft', 'type': ''},
    'affects': {'choice': False, 'count': count, 'type': 'creature'}, 'override': False, 'prompt': False}
host = copy.deepcopy(util); host.update(_id='IVinfuseHost0001', name='Infuse Host', sort=0)
host['activation'] = {'type': 'action', 'value': None, 'override': False, 'condition': ''}
host['consumption'] = {'scaling': {'allowed': False, 'max': ''}, 'spellSlot': False,
    'targets': [{'type': 'itemUses', 'value': '1', 'target': '', 'scaling': {}}]}
host['duration'] = {'units': 'hour', 'value': '1', 'concentration': False, 'override': False, 'special': 'Or until you use this feature again'}
host['range'] = {'units': 'touch', 'value': '', 'override': False, 'special': 'You or a creature you touch'}
host['target'] = tgt('1'); host['effects'] = [rider('IVhostEffect0001')]
counter = copy.deepcopy(save); counter.update(_id='IVcounterInfect1', name='Counter-Infection', sort=100)
counter['activation'] = {'type': 'reaction', 'value': None, 'override': False, 'condition': 'A creature hits the protected host with an attack roll'}
counter['consumption'] = {'scaling': {'allowed': False, 'max': ''}, 'spellSlot': True, 'targets': []}
counter['range'] = {'units': 'any', 'value': '', 'override': False, 'special': 'The attacker'}
counter['target'] = tgt('1'); counter['effects'] = [dict(rider('IVinfectedEff001'), onSave=False)]
counter['description'] = {'chatFlavor': 'On a failed save the attack misses instead.'}
restore = copy.deepcopy(util); restore.update(_id='IVrestoreSlot001', name='Restore Use (Level 2+ Spell Slot)', sort=200)
restore['activation'] = {'type': 'none', 'value': None, 'override': False, 'condition': ''}
restore['consumption'] = {'scaling': {'allowed': True, 'max': '8'}, 'spellSlot': False, 'targets': [
    {'type': 'spellSlots', 'value': '1', 'target': '2', 'scaling': {'mode': 'level'}},
    {'type': 'itemUses', 'value': '-1', 'target': '', 'scaling': {}}]}
restore['duration'] = {'units': 'inst', 'value': '', 'concentration': False, 'override': False, 'special': ''}
restore['range'] = {'units': 'self', 'value': '', 'override': False, 'special': ''}
restore['target'] = tgt(''); restore['effects'] = []
d['system']['activities'] = {a['_id']: a for a in (host, counter, restore)}
def eff(i, name, img, status, secs, desc):
    e = copy.deepcopy(eff_tpl); e.update(_id=i, name=name, img=ICON + img, statuses=[status], description=desc)
    e['duration'] = {'value': secs, 'units': 'seconds', 'expiry': None, 'expired': False}
    e['_key'] = f'!items.effects!{IID}.{i}'; return e
d['effects'] = [
    eff('IVhostEffect0001', 'Infection Vector', 's-shield-virus-lime.webp', 'infection-vector', 3600,
        '<p>Dormant malware protects this host for 1 hour. When a creature hits the host with an attack roll, the Virus can use Counter-Infection as a Reaction.</p>'),
    eff('IVinfectedEff001', 'Infected', 's-virus-pink.webp', 'infected', 6,
        '<p>The triggering attack misses. Disadvantage on ability checks and attack rolls until the start of your next turn (removed automatically in combat).</p>')]
d['img'] = ICON + 's-shield-virus-lime.webp'
yaml.safe_dump(d, open(F, 'w'), sort_keys=False, allow_unicode=True, width=200)
mf = os.path.join(OUT, 'features/gridrunner/virus/malware-3.yml'); t = open(mf).read()
open(mf, 'w').write(t.replace('  name: Malware\n  img: icons/svg/upgrade.svg', '  name: Malware\n  img: ' + ICON + 's-biohazard-lime.webp'))
print('round11 ok')
