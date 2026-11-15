#!/usr/bin/env python3
"""Round 12: Icon class + Headbanger/Holostar/Remix/Souljammer automation per book."""
import os
exec(''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fix_round7.py')).readlines()[:81]))
spc_cfg=copy.deepcopy(next(iter(L('features/enforcer/arbiter/arbiter-spells-3.yml')['system']['advancement'].values()))['configuration']['spell'])
F='features/icon/'; II='feat:iconic-inspiration'; DIE='@scale.icon.inspiration'
def ii(n=1): return [{'type':'itemUses','value':str(n),'target':II,'scaling':{}}]
def selfuse(n=1): return [{'type':'itemUses','value':str(n),'target':'','scaling':{}}]
def slot(lvl): return [{'type':'spellSlots','value':'1','target':str(lvl),'scaling':{'mode':'level'}}]
def restore_slot(d,tag,lvl):
    i,a=act(d,tag,'utility',f'Restore Use (Level {lvl}+ Spell Slot)','none',cons=slot(lvl)+selfuse(-1))
    a['consumption']['scaling']={'allowed':True,'max':'9'}; return i,a
def restore_ii(d,tag,label='Restore Use (Iconic Inspiration)'):
    return act(d,tag,'utility',label,'none',cons=ii()+selfuse(-1))
def rid(e): return {'_id':e['_id'],'riders':{'activity':[],'effect':[],'item':[]}}
def selfeff(a,e): a['effects']=[rid(e)]
def tgt(a,kind='creature',count='1',r=60):
    a['target']=one(kind,count); a['range']=ft(r)
def save_mode(ab): return chg(f'system.abilities.{ab}.save.roll.mode','1','add')
def rollact(d,tag,name,formula,activation,cond='',cons=None,label=None):
    i,a=act(d,tag,'utility',name,activation,cond,cons); a['roll']=roll(formula,label or name); return i,a
def ITEM(p): return L(F+p)
def SAVE(p,d): D(F+p,d)
def ICON(n): return f'modules/neon-odyssey/icons/neon/{n}.webp'

# ---------- class features ----------
p='class-features/iconic-inspiration-1.yml'; d=ITEM(p)
for e in d.get('effects',[]):
    if e['name']=='Inspired': e['duration']={'value':3600,'units':'seconds','expiry':None,'expired':False}; e['description']='<p>Holds an Iconic Inspiration die for 1 hour: once, after failing a D20 Test, roll it and add it to the d20.</p>'
a=first(d); a['range']=ft(60); a['target']=one()
i,r=rollact(d,'iidie','Roll Iconic Inspiration Die',DIE,'special','When you fail a D20 Test while holding the die')
d['system']['activities'][i]=r; SAVE(p,d)

p='class-features/extended-set-5.yml'; d=ITEM(p)
i,a=act(d,'xset','utility','Regain Iconic Inspiration (Spell Slot)','none',cons=slot(1)+ii(-1)); a['consumption']['scaling']={'allowed':True,'max':'9'}
setacts(d,[(i,a)]); SAVE(p,d)

p='class-features/cosmic-countermelody-7.yml'; d=ITEM(p)
a=first(d); a['name']='Countermelody'; a['activation']['condition']='You or a creature within 30 ft fails a save against Charmed or Frightened'
a['range']=ft(30); a['target']=one(); SAVE(p,d)

p='class-features/endless-encore-18.yml'; d=ITEM(p)
d['system']['description']['value']+='<p><em>Automated: when you roll Initiative, your Iconic Inspiration uses are topped up to 2.</em></p>'; SAVE(p,d)

p='class-features/song-of-the-cosmos-20.yml'; d=ITEM(p)
gi,g=grant('icon-song',20,'Song of the Cosmos',[P24+'phbsplPowerWordH',P24+'phbsplPowerWordK'])
g['configuration']['spell']=copy.deepcopy(spc_cfg)
d['system']['advancement']={gi:g}; SAVE(p,d)

# ---------- Headbanger ----------
p='headbanger/metal-mayhem-3.yml'; d=ITEM(p); d['img']=ICON('i-guitar-violet') if os.path.exists(os.path.expanduser('~/work/neon-odyssey/icons/neon/i-guitar-violet.webp')) else d['img']
e=eff(d,'Metal Mayhem',[],'mm',duration=mins(1),desc='<p>Rocking fury: Advantage on saves to avoid or end Charmed/Frightened. Once per turn on a hit, Steel Slam.</p>')
pr=eff(d,'Prone (Steel Slam)',[],'mmprone',statuses=['prone'])
d['effects']=[e,pr]
i1,a1=act(d,'mmgo','heal','Enter Metal Mayhem','none','When you expend a use of Iconic Inspiration')
a1['healing']=heal('@scale.icon.inspiration.faces','temphp'); selfeff(a1,e)
i2,a2=act(d,'mmslam','save','Steel Slam','special','Once on each of your turns when you hit a creature (while in Metal Mayhem)')
svdc(a2,'str',SPDC); tgt(a2,r=5); a2['effects']=[rid(pr)]
d['system']['activities']={i1:a1,i2:a2}; SAVE(p,d)

p='headbanger/shredder-3.yml'; d=ITEM(p)
t1=trait('shred-armor',0,'Studs and Leather',grants=['armor:med','armor:shl'])
t2=trait('shred-skill',0,'Studs and Leather: Skill',choices=[{'count':1,'pool':['skills:ath','skills:itm']}])
t3=trait('shred-weap',0,'Axe-Slinger: Martial Weapon',choices=[{'count':1,'pool':['weapon:mar:*']}])
d['system']['advancement']={k:v for k,v in (t1,t2,t3)}; SAVE(p,d)

p='headbanger/thunderstruck-3.yml'; d=ITEM(p)
i,a=act(d,'thund','damage','Thunderstruck','special','When a creature with your Iconic Inspiration die makes a damage roll (pushes 10 ft)')
dmg(a,[dpart(None,None,['thunder'],DIE)]); tgt(a,r=5); setacts(d,[(i,a)]); SAVE(p,d)

p='headbanger/facemelter-6.yml'; d=ITEM(p)
a=first(d); a['name']='Mosh Pit (15 ft Difficult Terrain)'; a['activation']={'type':'special','value':None,'override':False,'condition':'While Metal Mayhem is active'}
a['target']=area('radius',15); SAVE(p,d)

p='headbanger/iron-anthem-14.yml'; d=ITEM(p)
e=eff(d,'Iron Anthem',[chg('system.traits.dr.value','thunder','add'),save_mode('str'),save_mode('dex')],'ia',duration=mins(1),
      desc='<p>Thunder Resistance, Advantage on Str/Dex saves. Power Chord reaction; Screaming Defiance (drop to 1 HP instead of 0, once per Long Rest).</p>')
d['effects']=[e]
i1,a1=act(d,'iago','utility','Invoke Iron Anthem','none','When you activate Metal Mayhem',cons=selfuse())
a1['target']=one('ally','max(1,@abilities.cha.mod)'); a1['target']['affects']['choice']=True; a1['range']=ft(30); a1['effects']=[rid(e)]
a1['duration']={'units':'minute','value':'1','concentration':False,'override':False,'special':''}
i2,a2=act(d,'iapc','damage','Power Chord','reaction','An affected creature is hit by an attack roll')
dmg(a2,[dpart(None,None,['thunder'],'@abilities.cha.mod')]); tgt(a2,r=5)
i3,a3=restore_slot(d,'iarest',7)
d['system']['activities']={i1:a1,i2:a2,i3:a3}; SAVE(p,d)

# ---------- Holostar ----------
p='holostar/prismatic-hologram-3.yml'; d=ITEM(p)
d['effects']=[]
i1,a1=act(d,'phgo','utility','Create Hologram','bonus',cons=selfuse()); a1['range']=ft(30)
a1['duration']={'units':'minute','value':'1','concentration':False,'override':False,'special':''}
i2,a2=rollact(d,'phharm','Harmonize','1d4','reaction','A creature within 30 ft of the hologram succeeds or fails a D20 Test (add or subtract)')
i3,a3=act(d,'phmove','utility','Moonwalk (move 30 ft)','bonus'); a3['range']=ft(120)
d['system']['activities']={i1:a1,i2:a2,i3:a3}; SAVE(p,d)

p='holostar/glitz-and-glamour-3.yml'; d=ITEM(p)
a=first(d); a['name']='Lightshow (Silent Image, no Concentration, 10 min)'; a['activation']['type']='special'
a['consumption']['targets']=selfuse()
i,r=restore_ii(d,'ggrest'); d['system']['activities'][i]=r; SAVE(p,d)

p='holostar/dazzling-display-6.yml'; d=ITEM(p)
a=first(d); a['name']='Switch Places with Hologram'; a['range']=ft(60)
gi,g=grant('holo-dazzle',6,'Dazzling Display',[P24+'phbsplHypnoticPa']); g['configuration']['spell']=copy.deepcopy(spc_cfg)
d['system']['advancement']={gi:g}; SAVE(p,d)

p='holostar/holo-headliner-14.yml'; d=ITEM(p)
a=first(d); a['name']='Hologram Grants a Die'; a['activation']['type']='special'; a['activation']['condition']='When you grant an Iconic Inspiration die'
a['consumption']['targets']=selfuse(); a['range']=ft(60); a['target']=one(); SAVE(p,d)

# ---------- Remix ----------
p='remix/upbeat-aura-3.yml'; d=ITEM(p)
e=eff(d,'Upbeat Aura',[save_mode('dex')],'ua',duration=mins(1),desc='<p>30 ft Emanation (60 ft with Pump It Up). Flow State, Glide Roll (you and allies: Advantage on Dex saves), Tempo Tag.</p>')
tag=eff(d,'Tempo Tagged',[chg('system.attributes.movement.walk','-20','add')],'uatag',duration=turn(),desc='<p>Speed −20 ft. Ends early if it takes damage (it takes Psychic damage equal to one roll of the Iconic Inspiration die).</p>')
d['effects']=[e,tag]
i1,a1=act(d,'uago','utility','Start Upbeat Aura','action',cons=ii()); a1['effects']=[rid(e)]
a1['duration']={'units':'minute','value':'1','concentration':False,'override':False,'special':''}
i2,a2=act(d,'uatag','utility','Tempo Tag','special','Once per turn when you move within 5 ft of an enemy'); tgt(a2,'enemy',r=5); a2['effects']=[rid(tag)]
i3,a3=act(d,'uaburst','damage','Tempo Tag Burst','special','The tagged target takes damage'); tgt(a3,'enemy',r=60)
dmg(a3,[dpart(None,None,['psychic'],DIE)])
d['system']['activities']={i1:a1,i2:a2,i3:a3}; SAVE(p,d)

p='remix/feel-the-rhythm-3.yml'; d=ITEM(p)
e=eff(d,'Feel the Rhythm',[chg('system.attributes.movement.walk','10','add')],'ftr',duration={'value':3600,'units':'seconds','expiry':None,'expired':False},
      desc='<p>Speed +10 ft; Opportunity Attacks against you have Disadvantage. Remove when the Iconic Inspiration die is used.</p>')
d['effects']=[e]; i,a=act(d,'ftr','utility','Feel the Rhythm','special','When you grant an Iconic Inspiration die'); tgt(a); a['effects']=[rid(e)]
setacts(d,[(i,a)]); SAVE(p,d)

p='remix/pump-it-up-6.yml'; d=ITEM(p)
i1,a1=rollact(d,'puscr','Record Scratch','-'+DIE,'reaction','A creature tagged by your Upbeat Aura makes an attack roll')
i2,a2=act(d,'pudash','utility','Double Time (Dash)','bonus','While Upbeat Aura is active')
d['system']['activities']={i1:a1,i2:a2}; SAVE(p,d)

p='remix/remix-reality-14.yml'; d=ITEM(p)
st=[x for x in d['effects'] if x['name']=='Stunned']
slow=eff(d,'Off Beat',[chg('system.attributes.movement.walk','0.5','multiply')],'rrslow',duration=rnd(1),desc='<p>Speed halved; Disadvantage on its next attack roll.</p>')
for x in st: x['duration']=rnd(1)
d['effects']=st+[slow]
a=first(d); a['name']='Drop the Beat'; svdc(a,'con',SPDC); tgt(a,'enemy','2',60)
a['effects']=[rid(x) for x in st]+[{'_id':slow['_id'],'onSave':True,'riders':{'activity':[],'effect':[],'item':[]}}]
for x in st: a['effects'][0]['onSave']=False
a['consumption']['targets']=selfuse()
i,r=restore_slot(d,'rrrest',5); d['system']['activities'][i]=r; SAVE(p,d)

# ---------- Souljammer ----------
p='souljammer/smooth-jazz-3.yml'; d=ITEM(p)
a=first(d); a['type']='heal'; a['name']='Smooth Jazz'; a['activation']={'type':'special','value':None,'override':False,'condition':'Right after you cast a level 1+ Abjuration or Enchantment spell'}
a['consumption']['targets']=selfuse()+ii(); a['healing']=heal('2'+DIE.replace('@','@')+'.die' if False else '2@scale.icon.inspiration.die','temphp')
a['target']=one('ally','max(1,@abilities.cha.mod)'); a['target']['affects']['choice']=True; a['range']=ft(60)
a['description']['chatFlavor']='Charmed and Frightened end on each target.'
i,r=restore_ii(d,'sjrest'); d['system']['activities'][i]=r; SAVE(p,d)

p='souljammer/soul-jamming-3.yml'; d=ITEM(p)
i,a=rollact(d,'sjam','Soul Jamming','-'+DIE,'reaction','A creature within 60 ft succeeds on an ability check or saving throw',cons=ii())
tgt(a); setacts(d,[(i,a)]); SAVE(p,d)

p='souljammer/syncopated-swing-6.yml'; d=ITEM(p)
c1=cast(d,'ssbane','Cast Bane (free)',P24+'phbsplBane000000',1,cons=selfuse())
c2=cast(d,'ssbless','Cast Bless (free)',P24+'phbsplBless00000',1,cons=selfuse())
r=restore_slot(d,'ssrest',3); setacts(d,[c1,c2,r]); SAVE(p,d)

p='souljammer/rhapsody-in-blues-14.yml'; d=ITEM(p)
imm=eff(d,'Soothed Soul',[chg('system.traits.ci.value','charmed','add'),chg('system.traits.ci.value','frightened','add')],'rbimm',transfer=True,desc='<p>Immunity to Charmed and Frightened.</p>')
bop=eff(d,'Transcendent Bebop',[],'rbbop',duration=mins(1),desc='<p>Heroic Inspiration granted. A creature that damages this target takes Psychic damage equal to one roll of the Iconic Inspiration die (once per turn).</p>')
d['effects']=[imm,bop]
i1,a1=act(d,'rbbop','utility','Transcendent Bebop','bonus',cons=ii()); a1['target']=one('creature','max(1,@abilities.cha.mod)'); a1['target']['affects']['choice']=True
a1['range']=ft(60); a1['effects']=[rid(bop)]
i2,a2=act(d,'rbdmg','damage','Bebop Backlash','special','A creature damages a Transcendent Bebop target (once per turn)'); tgt(a2,'enemy',r=60)
dmg(a2,[dpart(None,None,['psychic'],DIE)])
d['system']['activities']={i1:a1,i2:a2}; SAVE(p,d)
d=L('classes/icon/icon.yml')
for a in d['system']['advancement'].values():
    if a['type']=='Trait' and a.get('level')==9 and not a.get('title'): a['title']='Expertise'
D('classes/icon/icon.yml',d)
print('round12 ok')
