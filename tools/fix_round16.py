#!/usr/bin/env python3
"""Round 16: area templates for features, species traits, gear, spells and monster actions whose text describes an area."""
import os,re
exec(''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fix_round7.py')).readlines()[:81]))

R='radius'
# path, item name prefix (None = the file's own item), activity name ('*' = every activity), type, size, extra
FIX=[
 ('origins/species-traits/raizo/unleash-the-storm.yml',None,'*',R,10,{}),
 ('origins/species-traits/solari/lightbringers-glare.yml',None,'*',R,15,{}),
 ('origins/species-traits/zeticulan/repulsion-field.yml',None,'*',R,15,{}),
 ('features/disciple/anomaly/impossible-no-more-17.yml',None,'Impossible No More',R,10,{}),
 ('features/disciple/godhand/stellar-flash-11.yml',None,'*',R,30,{'stationary':True}),
 ('features/icon/remix/upbeat-aura-3.yml',None,'Start Upbeat Aura',R,30,{}),
 ('features/machinist/gravgunner/gravitic-flux-9.yml',None,'*','sphere',20,{'range':150}),
 ('features/primalist/hivemind/cacophonous-swarm-3.yml',None,'Manifest Swarm',R,10,{}),
 ('features/primalist/hivemind/heart-of-the-swarm-10.yml',None,'*','sphere',10,{'range':120}),
 ('features/primalist/splicer/chimeric-splicing-3.yml',None,'Noxious',R,5,{}),
 ('items/gear/flamethrower.yml',None,'*','cone',15,{}),
 ('items/gear/fuel-oil.yml',None,'*','square',5,{'range':5}),
 ('items/gear/grav-spikes.yml',None,'*','square',5,{'range':5}),
 ('items/pack-contents/outrunner-s-pack--grav-spikes.yml',None,'*','square',5,{'range':5}),
 ('items/gear/steel-bearings.yml',None,'*','square',10,{'range':10}),
 ('items/pack-contents/intruder-s-pack--steel-bearings.yml',None,'*','square',10,{'range':10}),
 ('items/gear/signal-jammer.yml',None,'*',R,100,{}),
]
B='bestiary/cosmic-codex/'
for f,n,t,s,x in [
 ('battle-bot-devastator','Antipersonnel','sphere',20,{'range':150}),
 ('battle-bot-heavy','Suppressing Fire','cube',10,{'range':80}),
 ('boombot','Explosive End',R,10,{}),
 ('calamity-spawn','Whispering Aura',R,10,{}),
 ('calamity-spawn','Wails of the Consumed',R,120,{}),
 ('calamity-spawn','Lashing Burst',R,30,{}),
 ('calamity-spawn','Warp Space','sphere',15,{'range':60}),
 ('chem-sludge','Noxious Fumes',R,30,{}),
 ('chem-sludge','Corrosive Spew','cone',30,{}),
 ('demolitions-expert','Throw Grenade','sphere',10,{'range':'auto'}),
 ('drift-gaunt-cadet','Unmask',R,20,{}),
 ('drift-gaunt-commander','Personal Warp Generator',R,20,{}),
 ('drift-gaunt-commander','Death','cone',30,{}),
 ('drift-gaunt-lieutenant','Jetpack',R,20,{}),
 ('drift-gaunt-lieutenant','Unmask',R,10,{}),
 ('grid-spiker','Overload','sphere',20,{'range':60}),
 ('hive-ravager','Acid Spew','cone',30,{}),
 ('hollow-hunger','Quell Warmth','cone',20,{}),
 ('marine-commander','Photon Grenade','sphere',20,{'range':60}),
 ('marine-sergeant','Grenade','sphere',20,{'range':60}),
 ('space-pirate-captain','Shredder Grenade','sphere',20,{'range':60}),
 ('space-pirate-reaver','Scatter Shot','cone',15,{}),
 ('time-dolphin','Echolocation Burst','cone',30,{}),
 ('time-dolphin','Song of Time',R,20,{}),
 ('void-manta','Voidshadow','cone',60,{}),
 ('vort-elite','Terrifying Presence',R,30,{}),
 ('vort-elite','Acid Spray','line',30,{'width':5}),
 ('weird-scientist','Multi-Function Gizmo','sphere',20,{'range':60}),
]: FIX.append((B+f+'.yml',n,'*',t,s,x))
FIX.append((B+'security-bot.yml','Riot Gun','Save',R,10,{'stationary':True}))
for f,n,s in [('chatterling','Discordant Shriek',30),('harmonic-kindred','Harmonic Aura',5),('mindclinger','Mind Shield',5),
              ('mindclinger','Psychic Burst',5),('spy-drone','Self-Destruct',5),('starry-guide','Radiant Burst',5)]:
    FIX.append((f'bestiary/creatures/{f}.yml',n,'*',R,s,{}))

def apply(it,actname,typ,size,x):
    desc=re.sub('<[^>]+>',' ',it['system']['description']['value'])
    n=0
    for a in it['system']['activities'].values():
        if actname!='*' and a.get('name')!=actname: continue
        a['target']=area(typ,size)
        if x.get('width'): a['target']['template']['width']=str(x['width'])
        if x.get('stationary'): a['target']['template']['stationary']=True
        rng=x.get('range')
        if rng=='auto': rng=int(re.search(r'within (\d+) feet',desc).group(1))
        if rng: a['range']=ft(rng)
        if 'consumption' in a and it['type']!='spell': a['consumption']['spellSlot']=False
        n+=1
    assert n, (it['name'],actname)

done=0
for p,name,actname,typ,size,x in FIX:
    d=L(p)
    its=[d] if name is None else [i for i in d.get('items',[]) if i['name'].startswith(name)]
    assert len(its)==1,(p,name,len(its))
    apply(its[0],actname,typ,size,x); D(p,d); done+=1

p='spells/level-2/starshine.yml'; d=L(p)
d['system']['target']['template'].update({'type':R,'size':'10','units':'ft'})
D(p,d); done+=1
print('fixed',done)
