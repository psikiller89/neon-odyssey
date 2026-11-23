#!/usr/bin/env python3
"""Round 15: Nilari Breath Weapon cone/line templates and level scaling."""
import os
exec(''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fix_round7.py')).readlines()[:81]))

p='origins/species-traits/nilari/breath-weapon.yml'; d=L(p)
aid,base=[(i,a) for i,a in d['system']['activities'].items() if a['type']=='save'][0]
base['consumption']['spellSlot']=False
base['activation']['condition']='Replaces one attack when you take the Attack action'
part=base['damage']['parts'][0]
part.update({'number':None,'denomination':None,'custom':{'enabled':True,'formula':'(floor((@details.level + 1) / 6) + 1)d10'}})
cone=copy.deepcopy(base); cone.update({'name':'Breath Weapon (15-ft Cone)','sort':0,'target':area('cone',15)})
line=copy.deepcopy(base); line.update({'_id':mkid('r15:nilari-breath-line'),'name':'Breath Weapon (30-ft Line)','sort':1,'target':area('line',30)})
line['target']['template']['width']='5'
setacts(d,[(aid,cone),(line['_id'],line)])
D(p,d)
print('ok')

p='origins/species-traits/yoggoth/hypnagogic-droning.yml'; d=L(p)
for a in d['system']['activities'].values():
    if a['type']=='save': a['target']=area('radius',20)
D(p,d)

p='features/gridrunner/arc-mage/ultimate-flare-14.yml'; d=L(p)
for a in d['system']['activities'].values():
    if a['type']=='save': a['target']=area('cube',30); a['range']=ft(150)
D(p,d)
print('ok2')

p='origins/species-traits/nilari/wyrmhole-slip.yml'; d=L(p)
for a in d['system']['activities'].values():
    a['consumption']['spellSlot']=False
    a['range']=ft(30)
    a['target']=area('radius',10); a['target']['template']['stationary']=True
    a['target']['affects']={'choice':True,'count':'','type':'enemy'}
    a['description']['chatFlavor']='Difficult Terrain for enemies until the end of the turn (place it on your starting or destination space).'
D(p,d)
print('ok3')
