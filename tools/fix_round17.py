#!/usr/bin/env python3
"""Round 17: remaining area templates (Explosives, Death Burst, Abyssal Breach, Rivet Turret upgrades)."""
import os,re
exec(''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fix_round7.py')).readlines()[:81]))
DC15={'calculation':'','formula':'15'}

def sphere(n,stationary=False):
    t=area('sphere',n); t['template']['stationary']=stationary; return t

# Explosives: one button per charge/grenade type
p='items/gear/explosives.yml'; d=L(p)
emp=[e['_id'] for e in d.get('effects',[])]
A=[]
def boom(tag,name,rng,size,abil,parts,flavor='',effects=(),typ='save',on='half'):
    i,a=act(d,tag,typ,name,'action',cons=iu(),rng=ft(rng),target=sphere(size,True),effects=effects,flavor=flavor)
    if typ=='save': svdc(a,abil,DC15); dmg(a,parts,on)
    A.append((i,a))
boom('x-small','Small Breaching Charge',5,20,'con',[dpart(4,10,['thunder'])],'The surface the charge is attached to takes 8d10 Force damage.')
boom('x-large','Large Breaching Charge',5,50,'con',[dpart(10,10,['thunder'])],'The surface the charge is attached to takes 20d10 Force damage.')
boom('x-emp','EMP Grenade',60,20,'con',[],'Failed save: powered devices carried stop working for 1 minute; a Construct is Incapacitated. Repeat the save at the end of each turn.',emp,on='none')
boom('x-flash','Flashbang Grenade',60,20,'con',[],'Failed save: Blinded and Deafened. Repeat the save at the end of each turn; succeeds automatically after 1 minute.',on='none')
boom('x-frag','Frag Grenade',60,20,'dex',[dpart(4,6,['piercing'])])
boom('x-inc','Incendiary Grenade',60,20,'dex',[dpart(4,6,['fire'])],'Failed save: the creature starts burning. Flammable objects in the area start burning.')
boom('x-smoke','Smoke Grenade',60,20,None,None,'The Sphere is Heavily Obscured for 1 minute. A strong wind disperses the smoke.',typ='utility')
boom('x-plasma','Plasma Grenade',60,20,'dex',[dpart(5,6,['lightning'])],'Failed save: the creature can\'t take Reactions until the start of its next turn.')
setacts(d,A); D(p,d)

# Lesser Discordant Spirit: Death Burst
p='bestiary/summons/lesser-discordant-spirit.yml'; d=L(p)
it=[i for i in d['items'] if i['name']=='Death Burst'][0]
i,a=act(it,'deathburst','save','Death Burst','special','When the spirit dies',target=area('radius',10),flavor='Add the spell\'s level to the damage. Acid (Instinct), Necrotic (Entropy), Lightning (Progress) or Thunder (Thrill).')
svdc(a,'con',SPDC); dmg(a,[dpart(2,6,['acid','necrotic','lightning','thunder'])],'none')
it['system']['activities']={i:a}; D(p,d)

# Abyssal Breach grows to a 20-foot Sphere at Voidcaller 6 (Yawning Breach)
p='features/oracle/voidcaller/abyssal-breach-3.yml'; d=L(p)
for a in d['system']['activities'].values():
    if a.get('name')=='Open Abyssal Breach': a['target']['template']['size']=f'10 + 10 * min(1, floor({OL} / 6))'
D(p,d)

# Rivet Turret: Enhanced Emplacements versions
p='bestiary/summons/rivet-turret.yml'; d=L(p)
for it in d['items']:
    acts=it['system']['activities']
    if it['name']=='Flash Charge':
        base=next(iter(acts.values()))
        i,a=act(it,'ee-flash','save','Flash Charge (Enhanced Emplacements)',rng=copy.deepcopy(base['range']),target=sphere(10))
        a['save']=copy.deepcopy(base['save']); a['effects']=copy.deepcopy(base.get('effects',[])); a['damage']=copy.deepcopy(base.get('damage',{'onSave':'none','parts':[]}))
        acts[i]=a
    if it['name']=='Plasma Arc':
        base=next(iter(acts.values()))
        i,a=act(it,'ee-arc','save','Plasma Arc (Enhanced Emplacements)',target=line(60,5))
        a['save']=copy.deepcopy(base['save']); a['damage']=copy.deepcopy(base['damage']); a['damage']['parts'][0]['number']=3
        acts[i]=a
D(p,d)
print('ok')
