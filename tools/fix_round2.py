import sys,os,copy,yaml; sys.path.insert(0,'.')
from common import OUT,stats
from autoact import mkid
def L(p): return yaml.safe_load(open(os.path.join(OUT,p)))
def D(p,d): yaml.safe_dump(d,open(os.path.join(OUT,p),'w'),sort_keys=False,allow_unicode=True,width=200)
def chg(k,v,t,pr=None): return {'key':k,'value':str(v),'priority':pr,'type':t,'phase':'initial','_id':mkid(f'r1:{k}:{v}')}
def eff(d,name,changes,tag,transfer=False,disabled=False,statuses=(),desc='',duration=None):
    eid=mkid(d['_id']+':r1:'+tag)
    return {'_id':eid,'name':name,'img':d.get('img'),'type':'base','system':{'changes':changes},'disabled':disabled,'transfer':transfer,
      'duration':duration or {'value':None,'units':'seconds','expiry':None,'expired':False},'description':desc,'tint':'#ffffff','statuses':list(statuses),'sort':0,'flags':{},
      'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"}
VIS={'level':{'min':None,'max':None},'identifier':'','requireAttunement':False,'requireIdentification':False,'requireMagic':False}
def act(d,tag,typ,name,activation='action',cond='',cons=None,rng=None,target=None,effects=(),flavor='',minlvl=None,cls=None,**extra):
    i=mkid(d['_id']+':r1act:'+tag)
    a={'_id':i,'type':typ,'name':name,'img':'','sort':0,'activation':{'type':activation,'value':None,'override':False,'condition':cond},
       'consumption':{'scaling':{'allowed':False,'max':''},'spellSlot':False,'targets':cons or []},'description':{'chatFlavor':flavor},
       'duration':{'units':'inst','concentration':False,'override':False,'value':'','special':''},
       'effects':[{'_id':e,'riders':{'activity':[],'effect':[],'item':[]}} for e in effects],
       'range':rng or {'units':'self','override':False,'special':''},
       'target':target or {'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'','type':'self'},'override':False,'prompt':False},
       'uses':{'spent':0,'recovery':[],'max':''},'flags':{},'visibility':copy.deepcopy(VIS),'behaviors':[]}
    if minlvl: a['visibility']['identifier']=cls; a['visibility']['level']['min']=minlvl
    a.update(extra); return i,a
def uses(n,tgt=''): return [{'type':'itemUses','value':str(n),'target':tgt,'scaling':{}}]
def dpart(n,f,types,custom=None,bonus=''):
    return {'number':n,'denomination':f,'bonus':bonus,'types':list(types),'custom':{'enabled':bool(custom),'formula':custom or ''},'scaling':{'mode':'','number':None,'formula':''}}
def ft(n): return {'value':str(n),'units':'ft','special':'','override':False}
def one(kind='creature',count='1'): return {'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':count,'type':kind},'override':False,'prompt':False}
def area(typ,size): return {'template':{'contiguous':False,'units':'ft','type':typ,'size':str(size),'width':'','count':'','stationary':False},'affects':{'choice':True,'count':'','type':'creature'},'override':False,'prompt':True}
def roll(f,name): return {'formula':f,'name':name,'prompt':False,'visible':True}
def heal(f,t='healing'): return dpart(None,None,[t],f)
def setacts(d,pairs): d['system']['activities']={i:a for i,a in pairs}
def rec(*p): return [{'period':x,'type':'recoverAll'} for x in p]
def setuses(d,mx,*p): d['system']['uses']={'max':str(mx),'spent':0,'recovery':rec(*p)}
def rnd(n=1): return {'units':'rounds','value':str(n),'expiry':None,'expired':False}
def turn(): return {'units':'turns','value':'1','expiry':'turnEnd','expired':False}
def mins(n): return {'value':n*60,'units':'seconds','expiry':None,'expired':False}
SPDC={'calculation':'spellcasting','formula':''}
P24='Compendium.dnd5e.spells24.Item.'; PNO='Compendium.neon-odyssey.spells.Item.'
def cast(d,tag,name,uuid,lvl,activation='action',cond='',cons=None):
    i,a=act(d,tag,'cast',name,activation,cond,cons)
    a['spell']={'uuid':uuid,'challenge':{'override':False},'properties':['vocal','somatic'],'spellbook':False,'ability':'','level':lvl}
    a['target']['prompt']=True; return i,a
def svdc(a,abil,dc): a['save']={'ability':[abil],'dc':dc}
def dmg(a,parts,on=None):
    a['damage']={'critical':{'allow':False,'bonus':''},'parts':parts}
    if on: a['damage']['onSave']=on
def line(l,w): return {'template':{'contiguous':False,'units':'ft','type':'line','size':str(l),'width':str(w),'count':'','stationary':False},'affects':{'choice':True,'count':'','type':'creature'},'override':False,'prompt':True}
def maxlvl(a,cls,n): a['visibility']['identifier']=cls; a['visibility']['level']['max']=n
def noacteff(d,names):
    keep=[e for e in d.get('effects',[]) if e['name'] not in names]; ids={e['_id'] for e in keep}; d['effects']=keep
    for a in d['system'].get('activities',{}).values(): a['effects']=[x for x in a.get('effects',[]) if x['_id'] in ids]
def MIN(lvl): return {'units':'minute','value':str(lvl),'concentration':False,'override':False,'special':''}
JL='@classes.juggernaut.levels'; SG='@scale.juggernaut.rage-damage'; STRDC={'calculation':'str','formula':''}
OL='@classes.oracle.levels'; CC='feat:cosmic-conduit'; SU='feat:surge'
import re
RID=lambda e:{'_id':e['_id'],'riders':{'activity':[],'effect':[],'item':[]}}
F='features/'
J=F+'juggernaut/'
# ---- Surge: choose 3 resistances, drop artifact
p=J+'class-features/surge-1.yml'; d=L(p); noacteff(d,{'Incapacitated'})
m=next(e for e in d['effects'] if e['name']=='Surge'); m['system']['changes']=[c for c in m['system']['changes'] if c['key']!='system.traits.dr.value']
res=[eff(d,f'Surge Resistance: {t.title()}',[chg('system.traits.dr.value',t,'add')],'sres'+t,desc='<p>Apply three of these when you activate Surge.</p>') for t in ['bludgeoning','fire','lightning','piercing','radiant','slashing']]
d['effects']+=res
a=next(iter(d['system']['activities'].values())); a['effects']+=[RID(e) for e in res]; D(p,d)
p=J+'class-features/surging-core-15.yml'; d=L(p); noacteff(d,{'Incapacitated','Unconscious'}); D(p,d)
p=J+'class-features/augmented-intuition-3.yml'; d=L(p)
d['system']['description']['value']=re.sub(r'\+2 Hardened Form.*?(?=In addition)','</p><p>',d['system']['description']['value'],flags=re.S); D(p,d)
# ---- Kinetic Impact: Neon option names
p=J+'class-features/kinetic-impact-9.yml'; d=L(p)
ex=next(a for a in d['system']['activities'].values() if a['type']=='damage'); ex['name']='Kinetic Impact: Extra Damage'
ex['damage']['parts'][0]['custom']={'enabled':True,'formula':f'(1 + min(1, floor({JL} / 17)) + min(1, floor({JL} / 20)))d10'}
dm=eff(d,'Disrupt Momentum',[chg('system.attributes.movement.bonus',15,'subtract')],'disrupt',duration=rnd(1),desc='<p>Speed reduced by 15 feet until the start of your next turn.</p>')
dz=eff(d,'Dazing Impact',[],'dazing',duration=rnd(1),desc='<p>Disadvantage on the next saving throw; can\u2019t make Opportunity Attacks until the start of your next turn.</p>')
fr=eff(d,'Fracture Defenses',[],'fracture',duration=rnd(1),desc='<p>The next attack roll by another creature against this target before the start of your next turn gains +5.</p>')
d['effects']=[dm,dz,fr]
setacts(d,[(ex['_id'],ex),
  act(d,'disrupt','utility','Disrupt Momentum','special','A Kinetic Impact hit',target=one(),effects=[dm['_id']]),
  act(d,'repel','utility','Repelling Force','special','A Kinetic Impact hit',target=one(),flavor='Push the target 15 feet straight away; you can move up to half your Speed toward it without provoking Opportunity Attacks.'),
  act(d,'dazing','utility','Dazing Impact','special','A Kinetic Impact hit',target=one(),effects=[dz['_id']],minlvl=13,cls='juggernaut'),
  act(d,'fracture','utility','Fracture Defenses','special','A Kinetic Impact hit',target=one(),effects=[fr['_id']],minlvl=13,cls='juggernaut')]); D(p,d)
# ---- Eternal
p=J+'eternal/call-the-power-3.yml'; d=L(p)
alter=eff(d,'Heroic Alter-Ego',[chg('system.abilities.cha.check.roll.mode',1,'add')],'alter',duration=mins(10),desc='<p>Advantage on Charisma checks; DC 20 Investigation to recognize you. Mythic Presence: allies in a 10-ft Emanation add 1d4 to saving throws.</p>')
d['effects']=[alter]
i1,a1=act(d,'beam','save','Energy Beam','special','Replace one attack on your turn',target=line(30,5)); svdc(a1,'dex',STRDC); dmg(a1,[dpart(None,None,['force'],f'1d6 + @abilities.str.mod + {SG}')],'none'); maxlvl(a1,'juggernaut',9)
i2,a2=act(d,'beam10','save','Energy Beam (Eternal Flare)','special','Replace one attack on your turn',target=line(60,10),minlvl=10,cls='juggernaut'); svdc(a2,'dex',STRDC); dmg(a2,[dpart(None,None,['force'],f'3d6 + @abilities.str.mod + {SG}')],'half')
setacts(d,[(i1,a1),(i2,a2),act(d,'alter','utility','Heroic Alter-Ego','special','When you activate your Surge',effects=[alter['_id']],duration=MIN(10))]); D(p,d)
p=J+'eternal/mythic-awakening-6.yml'; d=L(p)
bs=eff(d,'Sight Beyond Sight',[chg('system.attributes.senses.ranges.blindsight',10,'add')],'blind',duration=mins(10))
hr=[eff(d,f'Heroic Resolve: {n}',[chg(f'system.abilities.{k}.bonuses.save','@abilities.str.mod','add')],'hr'+k,duration=mins(10)) for k,n in [('int','Intelligence'),('wis','Wisdom'),('cha','Charisma')]]
d['effects']=[bs]+hr
setacts(d,[act(d,'awaken','utility','Mythic Awakening','special','When you activate your Surge (apply Sight Beyond Sight and one Heroic Resolve)',effects=[bs['_id']]+[e['_id'] for e in hr],duration=MIN(10))]); D(p,d)
p=J+'eternal/master-of-the-eternal-14.yml'; d=L(p)
eh=eff(d,'Eternal Hero',[chg('system.traits.dr.value',t,'add') for t in ['bludgeoning','fire','lightning','piercing','radiant','slashing']],'hero',duration=mins(10),desc='<p>Resistance to all Surge damage types.</p>')
d['effects']=[eh]
setacts(d,[act(d,'relic','utility','Bonded Relic','bonus','Or when you activate your Surge',flavor='Teleport your Vessel of Power to you, or reconstitute it.'),
  act(d,'hero','utility','Eternal Hero','special','When you activate your Surge',effects=[eh['_id']],duration=MIN(10))]); D(p,d)
# ---- Mutant
p=J+'mutant/mutagenic-flesh-3.yml'; d=L(p)
se=eff(d,'Aberrant Senses',[chg('system.attributes.senses.ranges.blindsight',10,'add'),chg('system.attributes.senses.ranges.darkvision',30,'add')],'senses',transfer=True)
d['effects']=[se]
i1,a1=act(d,'caustic','damage','Caustic Secretions','reaction','A creature within 5 ft damages you',rng=ft(5),target=one()); dmg(a1,[dpart(None,None,['acid'],'@abilities.str.mod')])
i2,a2=act(d,'append','attack','Sprouted Appendage','bonus',rng=ft(5),target=one())
a2['attack']={'ability':'str','bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':'melee','classification':'unarmed'}}
a2['damage']={'critical':{'bonus':''},'includeBase':False,'parts':[dpart(1,6,['acid','bludgeoning','slashing'],bonus='@mod')]}
setacts(d,[(i1,a1),(i2,a2),act(d,'shriek','utility','Shrieking Mouths','special','When you hit a creature',target=one(),flavor='Until the start of your next turn you have Advantage on Opportunity Attacks against it, and it has Disadvantage on attacks against targets other than you.')]); D(p,d)
p=J+'mutant/adaptive-mutation-6.yml'; d=L(p)
d['effects']=[eff(d,f'Adaptive Mutation: {n}',ch,'am'+n,transfer=True,disabled=True,desc='<p>Turn on the mutation you chose.</p>') for n,ch in [
  ('Amphibious',[chg('system.attributes.movement.swim','@attributes.movement.walk','upgrade')]),('Subterranean',[chg('system.attributes.movement.burrow','@attributes.movement.walk','upgrade')]),
  ('Clinging',[chg('system.attributes.movement.climb','@attributes.movement.walk','upgrade')]),('Amorphous',[])]]; D(p,d)
# ---- Rampager
p=J+'rampager/earthshaking-leap-10.yml'; d=L(p)
a=next(iter(d['system']['activities'].values())); a['name']='Earthshaking Leap'; a['target']=area('radius',10); dmg(a,[dpart(None,None,['force'],f'({SG})d10')],'half'); D(p,d)
p=J+'rampager/monstrous-charge-6.yml'; d=L(p); noacteff(d,{'Restrained'}); next(iter(d['system']['activities'].values()))['name']='Toss Aside'; D(p,d)
p=J+'rampager/rampaging-destruction-3.yml'; d=L(p)
ti=eff(d,'Titanic Surge',[chg('system.traits.size','lg','override',20)],'titan',duration=mins(10))
d['effects']=[ti]
old=next(iter(d['system']['activities'].values())); old['name']='Titanic Surge: Improvised Weapon'; old['activation']={'type':'special','value':None,'override':False,'condition':'Hit with a held object or grappled creature'}
i1,a1=act(d,'smash','damage','Smash Apart','special','First Strength hit on a turn you use Unstable Assault',target=one()); dmg(a1,[dpart(None,None,['force'],f'({SG})d4')])
setacts(d,[(i1,a1),act(d,'titan','utility','Titanic Surge (Large)','special','When you activate your Surge',effects=[ti['_id']],duration=MIN(10)),(old['_id'],old)]); D(p,d)
p=J+'rampager/roaring-devastation-14.yml'; d=L(p)
a=next(iter(d['system']['activities'].values())); a['target']=area('radius',20)
d['system']['activities'].update(dict([act(d,'restore','utility','Restore (expend a Surge)','special','After your Surge ends',[{'type':'itemUses','value':'-1','target':'','scaling':{}},{'type':'itemUses','value':'1','target':SU,'scaling':{}}])])); D(p,d)
# ---- Scrapper
p=J+'scrapper/scrap-modder-3.yml'; d=L(p)
i1,a1=act(d,'buss','save','Junkerbuss','special','Replace one attack of the Attack action',uses(1),target=area('cone',30),flavor='Failed targets begin burning.'); svdc(a1,'dex',STRDC); dmg(a1,[dpart(None,None,['fire'],f'({SG})d8')],'half')
i2,a2=act(d,'burst','damage','Scrapburst','special','Once per turn, hit with a Melee weapon',uses(1),target=one(),flavor='You can also apply Push or Topple.')
dmg(a2,[dpart(None,None,['thunder'],f'(1 + min(1, floor({JL} / 9)) + min(1, floor({JL} / 16)))d8')])
setacts(d,[(i1,a1),(i2,a2)]); D(p,d)
p=J+'scrapper/rusty-spikes-10.yml'; d=L(p)
i1,a1=act(d,'reduce','utility','Rusty Spikes: Reduce Damage','reaction','A creature hits you with an attack roll',roll=roll('2d6','Damage reduced'))
i2,a2=act(d,'spike','damage','Rusty Spikes: Melee Attacker','special','Triggering attack was melee (same amount as reduced)',target=one()); dmg(a2,[dpart(2,6,['piercing'])])
setacts(d,[(i1,a1),(i2,a2)]); D(p,d)
p=J+'scrapper/fury-of-the-road-14.yml'; d=L(p)
i0,a0=act(d,'bike','utility','Create Cruising Bike','bonus','Or when you activate your Surge',uses(1),flavor='Drag the Cruising Bike vehicle from the Bestiary within 10 ft of you.')
i1,a1=act(d,'ram','damage','Ride-By Slash','special','Move within 5 ft of a creature while riding (once per creature per turn)',target=one()); dmg(a1,[dpart(3,6,['slashing'])])
i2,a2=act(d,'boom','save','Detonate Bike','action',target=area('sphere',30)); svdc(a2,'dex',STRDC); dmg(a2,[dpart(5,6,['fire']),dpart(5,6,['piercing'])],'half')
setacts(d,[(i0,a0),(i1,a1),(i2,a2),act(d,'restore','utility','Restore (expend a Surge)','special',cons=[{'type':'itemUses','value':'-1','target':'','scaling':{}},{'type':'itemUses','value':'1','target':SU,'scaling':{}}])]); D(p,d)
p=J+'scrapper/junkyard-ingenuity-6.yml'; d=L(p)
a=next(iter(d['system']['activities'].values())); a['name']='Dragline'; a['range']=ft('@attributes.movement.walk'); a['target']=one()
d['system']['activities'].update(dict([act(d,'bounce','utility','Boombounce','bonus','As part of activating or maintaining Surge',flavor='Jump as with a running start, distance doubled; up to Str mod allies within 10 ft jump with you.')])); D(p,d)
print('round2 juggernaut ok')
import glob as _g
def d5id(name):
    for f in _g.glob(os.path.expanduser('~/work/dnd5e/packs/_source/spells24/**/*.yml'),recursive=True):
        y=yaml.safe_load(open(f))
        if y.get('name')==name: return P24+y['_id']
M=F+'machinist/'
p=M+'botnik/buddy-bot-3.yml'; d=L(p); noacteff(d,{'Incapacitated'}); next(iter(d['system']['activities'].values()))['name']='Command Buddy Bot'; D(p,d)
p=M+'riveter/sentinel-mode-5.yml'; d=L(p); noacteff(d,{'Invisible'}); next(iter(d['system']['activities'].values()))['name']='Sentry Gun'; D(p,d)
p=M+'riveter/enhanced-emplacements-9.yml'; d=L(p); d['system']['activities']={}; D(p,d)
p=M+'gravgunner/grav-gun-3.yml'; d=L(p)
i,a=act(d,'shot','attack','Grav Gun','action',rng={'value':'100','long':'400','units':'ft','special':'','override':True},target=one())
a['attack']={'ability':'int','bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':'ranged','classification':'weapon'}}
a['damage']={'critical':{'bonus':''},'includeBase':False,'parts':[dpart(1,12,['force'],bonus='@mod')]}
setacts(d,[(i,a)]); D(p,d)
p=M+'gravgunner/singularity-cannon-3.yml'; d=L(p); pr=next(e for e in d['effects'] if e['name']=='Prone')
t=re.sub('<[^>]+>',' ',d['system']['description']['value']); vm=t[t.find('Vector Manipulator'):][:600]
vab=next((k for k,n in [('str','Strength'),('dex','Dexterity'),('con','Constitution')] if n+' saving' in vm),'str')
i1,a1=act(d,'beam','save','Disruptor Beam','bonus',cons=uses(1),target=line(30,5)); svdc(a1,'dex',dict(SPDC)); dmg(a1,[dpart(2,8,['force'])],'half')
i2,a2=act(d,'barrage','save','Suppression Barrage','bonus',cons=uses(1),target=area('cone',30),effects=[pr['_id']]); svdc(a2,'dex',dict(SPDC)); dmg(a2,[dpart(1,8,['force'])],'half')
i3,a3=act(d,'vector','save','Vector Manipulator','bonus',cons=uses(1),target=area('cone',30),flavor=re.sub(r'\s+',' ',vm)[:400]); svdc(a3,vab,dict(SPDC))
i4,a4=act(d,'field','heal','Graviton Forcefield','bonus',cons=uses(1),rng=ft(30),target=one(),minlvl=5,cls='machinist'); a4['healing']=heal('2d8 + @abilities.int.mod','temphp')
d['effects']=[pr]; setacts(d,[(i1,a1),(i2,a2),(i3,a3),(i4,a4)]); D(p,d)
p=M+'gravgunner/control-gravity-15.yml'; d=L(p); setuses(d,1,'lr')
rg=d5id('Reverse Gravity'); cfly=eff(d,'Control Gravity: Fly in the Cube',[chg('system.attributes.movement.fly','@attributes.movement.walk','upgrade')],'cfly',duration=mins(1),desc='<p>Fly Speed equal to your Speed while inside the 100-foot Cube.</p>')
d['effects']=[cfly]; ia,aa=act(d,'cfly','utility','Fly in the Cube','special','While inside your Reverse Gravity Cube',effects=[cfly['_id']])
ib,ab=act(d,'pull','utility','Change Gravity Direction','bonus',flavor='Gravity now pulls toward a chosen face of the Cube; no falling damage.')
setacts(d,[cast(d,'rev','Reverse Gravity (free, 100-ft Cube)',rg,7,cons=uses(1)),(ia,aa),(ib,ab)]); D(p,d)
p=M+'riveter/riveter-spells-3.yml'; d=L(p); adv=d['system']['advancement']
for a in (adv.values() if isinstance(adv,dict) else adv):
    if a['level']==5 and len(a['configuration']['items'])==1: a['configuration']['items'].append({'uuid':P24+'phbsplWeb0000000','optional':False,'sort':0})
    if a['level']==13 and len(a['configuration']['items'])==1: a['configuration']['items'].append({'uuid':PNO+'nw8WLScRIXy19tAp','optional':False,'sort':0})
D(p,d)
print('round2 machinist ok', rg, vab)
O=F+'oracle/'
# ---- Cosmic Conduit: Neon names
p=O+'class-features/cosmic-conduit-2.yml'; d=L(p)
inc=next((e['_id'] for e in d['effects'] if e['name']=='Incapacitated'),None)
for e in d['effects']:
    if e['name']=='Turned': e['name']='Rebuked'
for a in d['system']['activities'].values():
    if a['name']=='Turn Undead': a['name']='Rebuke Anathema'
    if a['name']=='Sear Undead': a['name']='Rebuke Anathema (Doom Anathema)'
    if a['name']=='Cosmic Pulse: Save': a['effects']=[x for x in a['effects'] if x['_id']!=inc]
D(p,d)
# ---- Destined Path / Ominous Horizon: Neon option features (replace dnd5e Cleric items)
tpl=L(O+'class-features/doom-anathema-5.yml')
def newfeat(slug,name,desc,lvl):
    y=copy.deepcopy(tpl); y['_id']=mkid('r2feat:'+slug); y['name']=name; y['system']['identifier']=slug
    y['system']['description']['value']=f'<p>{desc}</p>'; y['system']['activities']={}; y['system']['advancement']={}; y['effects']=[]
    if '_key' in y: y['_key']=f"!items!{y['_id']}"
    y['system']['requirements']=f'Oracle {lvl}'; y['system']['prerequisites']={'level':None,'items':[],'repeatable':False}; y['system']['type']={'value':'class','subtype':''}; return y
seer=newfeat('seer','Destined Path: Seer','You know one extra cantrip from the Oracle spell list (add it from the Spells compendium). You add your Wisdom modifier (minimum of +1) to Intelligence (Arcana or Religion) checks.',1)
seer['effects']=[eff(seer,'Seer',[chg('system.skills.arc.bonuses.check','max(1, @abilities.wis.mod)','add'),chg('system.skills.rel.bonuses.check','max(1, @abilities.wis.mod)','add')],'seer',transfer=True)]
sent=newfeat('sentinel','Destined Path: Sentinel','Trained for battle, you gain proficiency with Martial weapons and training with Heavy armor.',1)
ta=mkid('r2:sentinel'); sent['system']['advancement']={ta:{'_id':ta,'type':'Trait','level':1,'title':'Sentinel','hint':'','icon':None,'classRestriction':'','flags':{},
    'configuration':{'mode':'default','allowReplacements':False,'grants':['weapon:mar','armor:hvy'],'choices':[]},'value':{}}}
edge=newfeat('ascendant-edge','Ominous Horizon: Ascendant Edge','Once on each of your turns when you hit a creature with an attack roll using a weapon, the target takes an extra 1d8 Necrotic or Radiant damage (your choice). The damage increases to 2d8 at Oracle level 14 (Fatal Omen).',7)
i,a=act(edge,'edge','damage','Ascendant Edge','special','Once per turn, hit with a weapon attack',target=one()); dmg(a,[dpart(None,None,['necrotic','radiant'],f'(1 + min(1, floor({OL} / 14)))d8')]); setacts(edge,[(i,a)])
flare=newfeat('mystic-flare','Ominous Horizon: Mystic Flare','Add your Wisdom modifier to the damage you deal with any Oracle cantrip. At Oracle level 14 (Fatal Omen), when an Oracle cantrip damages a creature, you or another creature within 60 feet gains Temporary Hit Points equal to twice your Wisdom modifier.',7)
flare['effects']=[eff(flare,'Mystic Flare',[],'flare',transfer=True,desc='<p>Add your Wisdom modifier to Oracle cantrip damage (add it in the cantrip\u2019s damage bonus).</p>')]
i,a=act(flare,'thp','heal','Mystic Flare: Vitality','special','An Oracle cantrip damages a creature',rng=ft(60),target=one(),minlvl=14,cls='oracle'); a['healing']=heal('2 * @abilities.wis.mod','temphp'); setacts(flare,[(i,a)])
for y,slug in [(seer,'seer'),(sent,'sentinel'),(edge,'ascendant-edge'),(flare,'mystic-flare')]: D(O+f'class-features/{slug}.yml',y)
NF='Compendium.neon-odyssey.features.Item.'
for f,pool in [('destined-path-1',[seer,sent]),('ominous-horizon-7',[edge,flare])]:
    p=O+f'class-features/{f}.yml'; d=L(p)
    for a in d['system']['advancement'].values():
        a['configuration']['pool']=[{'uuid':NF+y['_id'],'sort':0} for y in pool]
        a['name']={'destined-path-1':'Destined Path Choice','ominous-horizon-7':'Ominous Horizon Choice'}[f]
        a['hint']={'destined-path-1':'<p>You have dedicated yourself to one of the following cosmic pursuits of your choice.</p>','ominous-horizon-7':'<p>Your strikes become guided by cosmic forces. You gain one of the following options of your choice.</p>'}[f]
    D(p,d)
# ---- Dreamer
p=O+'dreamer/dream-figment-3.yml'; d=L(p)
fx=[eff(d,'Dream Figment: Cozy Bubble',[],'cozy',duration=mins(1),desc='<p>Temporary Hit Points equal to your Wisdom modifier (twice at Oracle 6) at the start of each turn; Immunity to Frightened at Oracle 6.</p>'),
    eff(d,'Dream Figment: Glitter Burst',[],'glitter',duration=mins(1),desc='<p>Once per turn, +1d4 Psychic or Radiant on a hit (1d8 at Oracle 6, +5 ft reach, ignore Half Cover).</p>'),
    eff(d,'Dream Figment: Rainbow Boost',[chg('system.attributes.movement.bonus',10,'add')],'rainbow',duration=mins(1),desc='<p>+10 ft Speed, Opportunity Attacks against it have Disadvantage; teleport 15 ft once per turn at Oracle 6.</p>')]
d['effects']=fx
i1,a1=act(d,'create','utility','Create Dream Figment','bonus',uses(1,CC),rng=ft(30),target=one(),effects=[e['_id'] for e in fx],duration=MIN(1),flavor='Apply one benefit to the target and to yourself.')
i2,a2=act(d,'cozy','heal','Cozy Bubble','special','Start of an affected creature\u2019s turn',target=one()); a2['healing']=heal(f'max(1, @abilities.wis.mod) * (1 + min(1, floor({OL} / 6)))','temphp')
i3,a3=act(d,'glitter','damage','Glitter Burst','special','Once per turn, an affected creature hits',target=one()); dmg(a3,[dpart(None,None,['psychic','radiant'],f'1d(4 + 4 * min(1, floor({OL} / 6)))')])
setacts(d,[(i1,a1),(i2,a2),(i3,a3)]); D(p,d)
p=O+'dreamer/vivid-imagination-6.yml'; d=L(p); d['system']['activities']={}; d['effects']=[]; D(p,d)
p=O+'dreamer/unbroken-reverie-3.yml'; d=L(p)
setacts(d,[act(d,'reverie','utility','Unbroken Reverie','reaction','You or a creature within 30 ft fails a Concentration save',uses(1),rng=ft(30),target=one(),roll=roll('max(1, @abilities.wis.mod)','Bonus to the save'),flavor='Not expended if the target has your Dream Figment.')]); D(p,d)
# ---- Harmonious
p=O+'harmonious/weave-duality-3.yml'; d=L(p)
i1,a1=act(d,'somber','damage','Somber Grasp','special','A spell slot spell restores Hit Points (one target per creature healed)',rng=ft(30),target=one())
dmg(a1,[dpart(None,None,['radiant','necrotic'],'3')]); a1['damage']['parts'][0]['scaling']={'mode':'whole','number':None,'formula':'1'}; a1['consumption']['scaling']={'allowed':True,'max':'8'}
i2,a2=act(d,'vital','heal','Vital Surge','special','A spell slot spell deals damage (one target per creature damaged)',rng=ft(30),target=one('ally'))
a2['healing']=heal('3'); a2['healing']['scaling']={'mode':'whole','number':None,'formula':'1'}; a2['consumption']['scaling']={'allowed':True,'max':'8'}
for a in (a1,a2): a['description']['chatFlavor']='Base is a level 1 slot (2 + 1); scale up one step per slot level above 1.'
setacts(d,[(i1,a1),(i2,a2)]); D(p,d)
p=O+'harmonious/flow-of-energy-6.yml'; d=L(p)
i1,a1=act(d,'flow','damage','Flow of Energy','reaction','A creature within 30 ft takes Acid, Cold, Fire, Lightning, Necrotic, Radiant or Thunder damage',uses(1),rng=ft(30),target=one(),flavor='Give that creature Resistance to the triggering type; a different creature takes this damage.')
dmg(a1,[dpart(None,None,['necrotic','radiant'],f'floor({OL} / 2)')]); setacts(d,[(i1,a1)]); D(p,d)
p=O+'harmonious/lifeforce-confluence-17.yml'; d=L(p); noacteff(d,{'Incapacitated','Unconscious'}); D(p,d)
# ---- Stargazer
p=O+'stargazer/field-of-stars-3.yml'; d=L(p)
U6=f'min(1, floor({OL} / 6))'
i1,a1=act(d,'field','utility','Field of Stars','action',uses(1,CC),target=area('radius',20),duration=MIN(1),flavor='Dim Light; Frightened is suppressed for you and allies inside. Apply your triad benefit.')
i2,a2=act(d,'beacon','damage','Beacon','special','Once per turn, an affected creature hits and deals damage',target=one()); dmg(a2,[dpart(None,None,['radiant'],f'1d(4 + 2 * {U6})')])
i3,a3=act(d,'chron','utility','Chronicle','special',flavor='+5 ft Speed (+10 at Oracle 6) for you and allies entering or starting in the field; no Opportunity Attacks while boosted.')
i4,a4=act(d,'fount','utility','Fountain','reaction','An affected creature fails a saving throw',roll=roll(f'1d(4 + 2 * {U6})','Add to the save'))
i5,a5=act(d,'tower','utility','Tower','special','An affected creature takes damage (its Reaction)',roll=roll(f'1d(4 + 4 * {U6}) + max(1, @abilities.wis.mod)','Damage reduced'))
d['effects']=[]; setacts(d,[(i1,a1),(i2,a2),(i3,a3),(i4,a4),(i5,a5)]); D(p,d)
p=O+'stargazer/guiding-starlight-3.yml'; d=L(p)
for a in d['system']['activities'].values(): a['roll']=roll('1d4','Add or subtract'); a['name']='Guiding Starlight'; a['range']=ft(30)
D(p,d)
cac=L(F+'cryptist/cacophonous/cacophonous-spells-3.yml'); CH=next(a for a in cac['system']['advancement'].values() if a['type']=='ItemChoice')
GEN={3:['phbsplGuidingBol',PNO+'rFOqMpX3JRXjiGhd','phbsplStarryWisp'],5:['phbsplSpiritGuar'],7:['phbsplDivination'],9:[PNO+'O8Ol022jP2ih0oAR']}
TRI={3:['phbsplFaerieFire','phbsplScorchingR','phbsplIdentify00','phbsplMistyStep0','phbsplCureWounds',PNO+'or2IiLF4cMFbLkbX','phbsplShieldofFa','phbsplWardingBon'],
     5:['phbsplFireball00','phbsplHaste00000',PNO+'61LHNZtzRRtxBsaa','phbProtectionFro'],7:[PNO+'0v2e6WBYr6qvJdsA','phbsplDimensionD','phbsplAuraofLife',PNO+'rASJHD2XMwwEUUJa'],
     9:['phbsplFlameStrik','phbsplScrying000','phbsplGreaterRes','phbsplHallow0000']}
U=lambda x: x if x.startswith('Compendium') else P24+x
p=O+'stargazer/stargazer-spells-3.yml'; d=L(p); g0=next(iter(d['system']['advancement'].values())); adv={}
for lv in (3,5,7,9):
    g=copy.deepcopy(g0); g['_id']=mkid(f'stgz:g{lv}'); g['level']=lv; g['title']='Stargazer Spells (General)'; g['configuration']['items']=[{'uuid':U(x),'optional':False,'sort':0} for x in GEN[lv]]; g['value']={}; adv[g['_id']]=g
    c=copy.deepcopy(CH); c['_id']=mkid(f'stgz:c{lv}'); c['level']=lv; c['title']='Triad Spells'; c['hint']='Pick the spells of your Guiding Starlight triad (Beacon, Chronicle, Fountain or Tower).'
    c['configuration']['pool']=[{'uuid':U(x),'sort':0} for x in TRI[lv]]; c['configuration']['choices']={str(lv):{'count':2 if lv==3 else 1,'replacement':False}}; c['value']={}; adv[c['_id']]=c
d['system']['advancement']=adv; D(p,d)
# ---- Voidcaller
p=O+'voidcaller/abyssal-breach-3.yml'; d=L(p)
cd=eff(d,'Crushing Deep',[],'crush',duration=rnd(1),desc='<p>Speed halved in the breach; Disadvantage on attack rolls and ability checks until the start of its next turn.</p>')
d['effects']=[cd]
i1,a1=act(d,'open','utility','Open Abyssal Breach','bonus',uses(1,CC),rng=ft(60),target=area('sphere',10),duration=MIN(1),flavor='10-ft Sphere (20-ft at Oracle 6). Move it 30 ft as a Bonus Action on later turns.')
i2,a2=act(d,'crush','save','Crushing Deep','special','A creature enters or starts its turn in the breach',target=one(),effects=[cd['_id']]); svdc(a2,'wis',dict(SPDC))
i3,a3=act(d,'hunger','save','Hunger Beyond','special','A creature enters or starts its turn in the breach',target=one()); svdc(a3,'dex',dict(SPDC))
dmg(a3,[dpart(None,None,['necrotic','psychic'],f'(1 + min(1, floor({OL} / 5)) + min(1, floor({OL} / 13)))d8')],'none')
setacts(d,[(i1,a1),(i2,a2),(i3,a3)]); D(p,d)
p=O+'voidcaller/call-of-the-void-6.yml'; d=L(p)
d['effects'].append(eff(d,'Deep Resilience',[chg('system.traits.dr.value','necrotic','add'),chg('system.traits.dr.value','psychic','add')],'deep',transfer=True)); D(p,d)
p=O+'voidcaller/unfathomable-whispers-3.yml'; d=L(p); t=mkid('r2:whispers')
d['system']['advancement']={t:{'_id':t,'type':'Trait','level':3,'title':'Unfathomable Whispers','hint':'Arcana and Religion (Expertise if already proficient).','icon':None,'classRestriction':'','flags':{},
  'configuration':{'mode':'upgrade','allowReplacements':False,'grants':['skills:arc','skills:rel'],'choices':[]},'value':{}}}; D(p,d)
p=O+'voidcaller/abyssal-maw-17.yml'; d=L(p)
a=next(iter(d['system']['activities'].values())); a['type']='save'; a['name']='Devouring Collapse'; svdc(a,'cha',dict(SPDC)); a['damage']['onSave']='full'; a['flavor']=''; a['description']['chatFlavor']='Failed targets are affected by Banishment (you concentrate).'
D(p,d)
print('round2 oracle ok')
p='classes/juggernaut/juggernaut.yml'; d=L(p)
ADV=d['system']['advancement']
for a in (ADV.values() if isinstance(ADV,dict) else ADV):
    for k in ('name','title'):
        if a.get('type')=='ScaleValue' and a.get(k) in ('Rage Damage','Rages'): a[k]={'Rage Damage':'Surge Damage','Rages':'Surges'}[a[k]]
D(p,d); print('round2 juggernaut scale titles ok')
p=M+'boomdoctor/inspired-invention-9.yml'; d=L(p); ADV=d['system'].get('advancement') or {}
if isinstance(ADV,dict): d['system']['advancement']={k:v for k,v in ADV.items() if v.get('type')!='ItemGrant'}
else: d['system']['advancement']=[v for v in ADV if v.get('type')!='ItemGrant']
D(p,d); print('round2 boomsday duplicate grant removed')

REN={'Channel Divinity':'Cosmic Conduit','Divine Spark Die Count':'Cosmic Pulse Die Count'}
import glob
for p in ['classes/oracle/oracle.yml']+[os.path.relpath(x,OUT) for x in glob.glob(os.path.join(OUT,'features/oracle/**/*.yml'),recursive=True)]:
    d=L(p)
    if 'system' not in d: continue
    ADV=d['system'].get('advancement') or {}; ch=False
    for a in (ADV.values() if isinstance(ADV,dict) else ADV):
        for k in ('name','title'):
            if a.get(k) in REN: a[k]=REN[a[k]]; ch=True
    if ch: D(p,d); print('round2 renamed advancement in',p)
