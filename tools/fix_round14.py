#!/usr/bin/env python3
"""Round 14: Xenomon Hit Dice, starfighter shield auto-refill text, Arbiter balance choice."""
import os
exec(''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fix_round7.py')).readlines()[:81]))

p='features/primalist/xenotrainer/xenomon-partner-3.yml'; d=L(p)
for a in d['system']['activities'].values():
    if a['type']=='summon': a['bonuses']['hd']='@classes.primalist.levels'
D(p,d)

for v in ['interceptor','superiority-fighter']:
    p=f'bestiary/vehicles/{v}.yml'; d=L(p)
    for it in d['items']:
        if it['system'].get('identifier')!='shields': continue
        it['system']['description']['value']=('<p>Shield Points (30) are tracked as Temporary Hit Points and absorb damage first. They have their own Damage Threshold. '
            'After 1 minute (10 rounds) of game time without taking damage they return to maximum automatically. Use Restore Shield Points to refill them by hand.</p>')
    D(p,d)

p='features/enforcer/arbiter/aspect-of-balance-3.yml'; d=L(p)
acts=list(d['system']['activities'].items())
acts=[(i,a) for i,a in acts if not a['name'].startswith('Balance:')]
for side in ['Somber','Vital']:
    acts.insert(0 if side=='Somber' else 1, act(d,'balance'+side,'utility',f'Balance: {side}','special','When you finish a Long Rest'))
setacts(d,acts)
desc=d['system']['description']['value']
note='<p><em>Foundry: click Balance: Somber or Balance: Vital after a Long Rest. Only that aspect’s Arbiter Spells stay prepared; Imbue buttons also shift your balance.</em></p>'
if 'Foundry: click Balance' not in desc: d['system']['description']['value']=desc+note
D(p,d)
print('round14 ok')
