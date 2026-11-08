import sys,os,copy,yaml; sys.path.insert(0,'.')
from common import OUT,stats
from autoact import mkid
def L(p): return yaml.safe_load(open(os.path.join(OUT,p)))
def D(p,d): yaml.safe_dump(d,open(os.path.join(OUT,p),'w'),sort_keys=False,allow_unicode=True,width=200)
def chg(k,v,t,pr=None): return {'key':k,'value':str(v),'priority':pr,'type':t,'phase':'initial','_id':mkid(f"r3:{k}:{v}")}
def eff(d,name,changes,tag,transfer=False,disabled=False,statuses=(),desc='',duration=None):
    eid=mkid(d['_id']+':r3:'+tag)
    return {'_id':eid,'name':name,'img':d.get('img'),'type':'base','system':{'changes':changes},'disabled':disabled,'transfer':transfer,
      'duration':duration or {'value':None,'units':'seconds','expiry':None,'expired':False},'description':desc,'tint':'#ffffff','statuses':list(statuses),'sort':0,'flags':{},
      'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"}
VIS={'level':{'min':None,'max':None},'identifier':'','requireAttunement':False,'requireIdentification':False,'requireMagic':False}
def act(d,tag,typ,name,activation='action',cond='',cons=None,rng=None,target=None,effects=(),flavor='',minlvl=None,cls=None,**extra):
    i=mkid(d['_id']+':r3act:'+tag)
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
# ================= ROUND 4: TRACER =================
import re
T='features/tracer/'; NI='Compendium.neon-odyssey.items.Item.'
def actuse(a,n=1,*per):
    a['uses']={'spent':0,'recovery':rec(*per),'max':str(n)}
    a['consumption']['targets']=[{'type':'activityUses','value':'1','target':'','scaling':{}}]
def grant(tag,lvl,title,uuids):
    i=mkid('r4grant:'+tag); return i,{'_id':i,'type':'ItemGrant','configuration':{'items':[{'uuid':u,'optional':False,'sort':0} for u in uuids],'optional':False,'spell':None},'value':{},'level':lvl,'title':title,'hint':'','icon':None,'classRestriction':'','flags':{}}
def trait(tag,lvl,title,grants=(),choices=(),mode='default'):
    i=mkid('r4trait:'+tag); return i,{'_id':i,'type':'Trait','level':lvl,'title':title,'hint':'','icon':None,'classRestriction':'','flags':{},
      'configuration':{'mode':mode,'allowReplacements':False,'grants':list(grants),'choices':list(choices)},'value':{}}
def spc(c): return {'type':'special','value':None,'override':False,'condition':c}
def first(d): return next(iter(d['system']['activities'].values()))
def noadv(d,typ): d['system']['advancement']={k:v for k,v in d['system']['advancement'].items() if v.get('type')!=typ}
def atk(a,kind,cls,ability,parts):
    a['attack']={'ability':ability,'bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':kind,'classification':cls}}
    a['damage']={'critical':{'bonus':''},'includeBase':False,'parts':parts}
BPS=['bludgeoning','piercing','slashing']
# ---- class features
p=T+'class-features/hunters-eye-1.yml'; d=L(p); first(d)['name']="Hunter's Mark (free)"; D(p,d)
p=T+'class-features/cloaking-14.yml'; d=L(p); first(d)['name']='Cloaking'
for e in d['effects']:
    if e['name']=='Veiled': e['name']='Cloaked'
    if e['name']=='Invisible': e['duration']=turn()
D(p,d)
p=T+'class-features/inescapable-hunt-20.yml'; d=L(p); setuses(d,1,'lr')
setacts(d,[cast(d,'amp',"Amplified Instincts (Hunter's Mark)",P24+'phbsplHuntersMar',1,'special','When you hit a creature with an attack roll (ignore range)',uses(1))]); D(p,d)
p=T+'class-features/outlast-10.yml'; d=L(p)
for a in d['system']['activities'].values():
    if a['type']=='heal': a['name']='Hunt Hardened'; actuse(a,'max(1, @abilities.wis.mod)','lr')
    else: a['name']='Tireless Pursuit'
D(p,d)
# fighting style: Tracer options + dnd5e Fighting Style feats
base=L(T+'class-features/tenacious-trace-5.yml'); newfs=[]
for nm,desc,adv in [('Primal Hunter','<p>You learn two Primalist cantrips of your choice (Guidance and Starry Wisp are recommended). The chosen cantrips count as Tracer spells for you, and Wisdom is your spellcasting ability for them. Whenever you gain a Tracer level, you can replace one of these cantrips with another Primalist cantrip.</p>',{}),
    ('Urban Hunter','<p>You gain proficiency in two skills of your choice from the following: Acrobatics, Deception, Intimidation, or Persuasion.</p>',dict([trait('urban',None,'Urban Hunter',choices=[{'count':2,'pool':['skills:acr','skills:dec','skills:itm','skills:per']}])]))]:
    n=copy.deepcopy(base); n['_id']=mkid('r4fs:'+nm); n['name']=nm; n['_key']='!items!'+n['_id']; n['effects']=[]
    n['system']['description']['value']=desc; n['system']['identifier']=nm.lower().replace(' ','-'); n['system']['activities']={}; n['system']['advancement']=adv
    n['system']['type']={'value':'feat','subtype':'fightingStyle'}; n['system']['requirements']='Tracer'; n['system']['prerequisites']={'level':None,'items':[],'repeatable':False}
    D(T+'class-features/'+n['system']['identifier']+'.yml',n); newfs.append('Compendium.neon-odyssey.features.Item.'+n['_id'])
p=T+'class-features/fighting-style-2.yml'; d=L(p)
for a in d['system']['advancement'].values():
    if a['type']=='ItemChoice':
        a['configuration']['pool']=[{'uuid':u,'sort':0} for u in newfs+['Compendium.dnd5e.feats24.Item.'+x for x in ['phbfstArchery000','phbfstDefense000','phbfstGreatWeapo','phbfstTwoWeaponF']]]
        a['level']=2; a['title']='Fighting Style'
D(p,d)
# ---- Bloodhound
B=T+'bloodhound/'
p=B+'dead-or-alive-15.yml'; d=L(p); setuses(d,1,'sr','lr'); a=first(d); a['name']="Bring 'Em In"; a['activation']=spc('When you hit a creature with an attack roll'); a['target']=one()
for e in d['effects']: e['duration']=rnd(1)
setacts(d,[(a['_id'],a),act(d,'dog','utility','Dogged Pursuit','special','Once per turn: move Hunter\u2019s Mark without a Bonus Action')]); D(p,d)
p=B+'gritty-interrogation-7.yml'; d=L(p); d['system']['uses']={'max':'','spent':0,'recovery':[]}
ch=eff(d,'Gritty Interrogation: Charmed',[],'gch',statuses=['charmed'],duration=mins(1)); fr=eff(d,'Gritty Interrogation: Frightened',[],'gfr',statuses=['frightened'],duration=mins(1)); d['effects']=[ch,fr]
setacts(d,[act(d,'per','utility','Persuade (Charmed)','action','Influence action, creature within 60 ft (Wis save vs check total)',rng=ft(60),target=one(),effects=[ch['_id']],roll=roll('1d20 + @skills.per.total','Persuasion (save DC)')),
  act(d,'itm','utility','Intimidate (Frightened)','action','Influence action, creature within 60 ft (Wis save vs check total)',rng=ft(60),target=one(),effects=[fr['_id']],roll=roll('1d20 + @skills.itm.total','Intimidation (save DC)'))]); D(p,d)
p=B+'hounds-hunch-7.yml'; d=L(p)
setacts(d,[act(d,'hunch','utility',"Hound's Hunch",'action','Study action, creature within 60 ft (DC 15)',rng=ft(60),target=one(),roll=roll('1d20 + @skills.inv.total','Investigation'))]); D(p,d)
p=B+'sleuths-eye-silver-tongue-3.yml'; d=L(p)
d['system']['advancement']=dict([trait('sleuth',3,'Silver Tongue',choices=[{'count':1,'pool':['skills:dec','skills:his','skills:inv','skills:per']}])]); D(p,d)
p=B+'sniff-em-out-11.yml'; d=L(p); setuses(d,1,'lr')
LV={'Clairvoyan':3,'LocateCrea':4,'LocateObje':2,'SeeInvisib':2}
us=[i['uuid'] for v in d['system']['advancement'].values() if v['type']=='ItemGrant' for i in v['configuration']['items']]
noadv(d,'ItemGrant'); pairs=[]
for u in us:
    k=next(k for k in LV if k in u); pairs.append(cast(d,'sniff'+k,{'Clairvoyan':'Clairvoyance','LocateCrea':'Locate Creature','LocateObje':'Locate Object','SeeInvisib':'See Invisibility'}[k],u,LV[k],'bonus','',uses(1)))
setacts(d,pairs); D(p,d)
p=B+'split-second-read-3.yml'; d=L(p)
d['system']['uses']={'max':'max(1, @abilities.wis.mod)','spent':0,'recovery':[{'period':'lr','type':'recoverAll'},{'period':'sr','type':'formula','formula':'1'}]}
setacts(d,[act(d,'ssr','utility','Split-Second Read','reaction','You miss with an attack roll or fail a Dexterity save',uses(1),roll=roll('max(1, @abilities.wis.mod)','Bonus to the roll'))]); D(p,d)
p=B+'streetwise-wits-3.yml'; d=L(p)
setacts(d,[act(d,'sw','utility','Streetwise Wits','bonus','Influence, Search or Study as a Bonus Action',flavor='Search to scrutinize a creature within 60 ft (DC 15 Insight): Advantage on your first attack roll against it each turn for 1 minute.',roll=roll('1d20 + @skills.ins.total','Insight'))]); D(p,d)
# ---- Powertech
P=T+'powertech/'
p=P+'power-armor-3.yml'; d=L(p); a=first(d); a['name']='Activate Power Armor'; a['activation']={'type':'action','value':None,'override':False,'condition':"Magic action with Mechanic's Tools in hand"}; D(p,d)
p=P+'hunters-arsenal-3.yml'; d=L(p); d['system']['uses']={'max':'max(2, @abilities.wis.mod)','spent':0,'recovery':rec('sr','lr')}
i1,a1=act(d,'arsm','attack','Arsenal System (Melee)','action',rng={'units':'ft','value':'5','override':False,'special':''},target=one()); atk(a1,'melee','weapon','dex',[dpart(1,8,['force'],bonus='@mod')])
i2,a2=act(d,'arsr','attack','Arsenal System (Ranged)','action',rng={'units':'ft','value':'100','long':'300','override':False,'special':''},target=one()); atk(a2,'ranged','weapon','dex',[dpart(1,8,['force'],bonus='@mod')])
i3,a3=act(d,'burst','attack','Charge Burst','bonus','On a hit, activate Push or Sap',uses(1),{'units':'ft','value':'100','long':'300','override':False,'special':''},one()); atk(a3,'ranged','weapon','dex',[dpart(1,8,['force'],bonus='@mod')])
maxlvl(a3,'tracer',14)
i4,a4=act(d,'burst2','attack','Overcharged Pulse','bonus','On a hit, activate Push, Sap or Topple',uses(1),{'units':'ft','value':'100','long':'300','override':False,'special':''},one(),minlvl=15,cls='tracer'); atk(a4,'ranged','weapon','dex',[dpart(2,8,['force'],bonus='@mod')])
setacts(d,[(i1,a1),(i2,a2),(i3,a3),(i4,a4)]); D(p,d)
mt=L('items/tools/mechanics-tools.yml'); bk=mt['system']['type'].get('baseItem') or 'tinker'
ART={'alchemist','brewer','calligrapher','carpenter','cartographer','cobbler','cook','glassblower','jeweler','leatherworker','mason','painter','potter','smith','tinker','weaver','woodcarver'}
p=P+'suit-specialist-3.yml'; d=L(p)
d['system']['advancement']=dict([trait('suit',3,'Suit Specialist',['armor:hvy','tool:art:'+bk if bk in ART else 'tool:'+bk]),grant('mech',3,'Power Mechanic',[NI+mt['_id']])]); D(p,d)
p=P+'mark-ii-armor-7.yml'; d=L(p); setuses(d,'max(1, @abilities.wis.mod)','lr')
fj=eff(d,'Flight Jets',[chg('system.attributes.movement.speeds.fly','@attributes.movement.speed','upgrade')],'fj',duration=mins(1)); d['effects']=[fj]
setacts(d,[act(d,'fj','utility','Flight Jets','bonus','While wearing your Power Armor',uses(1),effects=[fj['_id']],duration=MIN(1))]); D(p,d)
p=P+'power-core-11.yml'; d=L(p); setuses(d,1,'sr','lr'); a=first(d); a['name']='Stim Jolt'; a['activation']['condition']='You fail a saving throw (succeed instead)'; D(p,d)
p=P+'mark-iii-armor-15.yml'; d=L(p); setuses(d,1,'lr')
rr=eff(d,'Reinforced Plating',[chg('system.traits.dr.value','radiant','add')],'rp',duration=mins(1)); d['effects']=[rr]
i1,a1=cast(d,'skin','Reinforced Plating (Stoneskin)',P24+'phbsplStoneskin0',4,'action','',uses(1))
setacts(d,[(i1,a1),act(d,'rad','utility','Reinforced Plating: Radiant Resistance','special','Stoneskin cast without Concentration (1 minute)',effects=[rr['_id']],duration=MIN(1))]); D(p,d)
# ---- Protostalker summons
tur=L('bestiary/summons/rivet-turret.yml'); RB=next(i for i in tur['items'] if i['name']=='Rivet Burst'); TR=next(i for i in tur['items'] if i['name']=='Relocate')
PROTOS=[('Bloodripper','med',{'walk':'40','climb':'40','swim':'60'},(14,15,14,10,15,6),5,(1,6),'Medium or Small Beast. Climb 40 ft. (Land only), Swim 60 ft. (Sea only).',
   [('Aspect','Choose Land or Sea when summoned. Amphibious (Sea only): breathes air and water, and you gain this trait.'),('Pack Tactics','Advantage on an attack roll against a creature if an ally of the protosaur is within 5 feet of it and isn\u2019t Incapacitated.')]),
  ('Bonestomper','lg',{'walk':'30','swim':'60'},(16,10,14,8,15,11),5,(1,8),'Large or Medium Beast. Swim 60 ft. (Sea only).',
   [('Aspect','Choose Land or Sea when summoned. Amphibious (Sea only): breathes air and water, and you gain this trait.'),('Standing Leap (Land Only)','Long Jump up to 20 feet and High Jump up to 10 feet, with or without a running start.'),('Trampling Charge','If the protosaur moved at least 20 feet straight toward the target before a Proto Strike hit, the target takes an extra 1d6 damage and is Prone if Large or smaller.')]),
  ('Skyterror','med',{'walk':'10','fly':'60'},(14,16,12,8,14,8),4,(1,4),'Medium or Small Beast. Fly 60 ft.',
   [('Flyby','Doesn\u2019t provoke Opportunity Attacks when it flies out of an enemy\u2019s reach.')])]
ptuu={}
for nm,size,mv,ab,hp,(dn,df),bio,traits in PROTOS:
    a=copy.deepcopy(tur); aid=mkid('r4proto:'+nm); a['_id']=aid; a['_key']='!actors!'+aid; a['name']='Protosaur '+nm; a['prototypeToken']['name']='Protosaur '+nm
    s=a['system']
    for k,v in zip(['str','dex','con','int','wis','cha'],ab): s['abilities'][k]={'value':v,'proficient':0}
    s['attributes']['ac']={'flat':13,'calc':'natural'}; s['attributes']['hp'].update({'value':hp,'max':hp})
    s['attributes']['movement']={'walk':mv.get('walk','0'),'climb':mv.get('climb',''),'swim':mv.get('swim',''),'fly':mv.get('fly',''),'units':'ft','hover':False}
    s['attributes']['senses']['ranges']['darkvision']=60
    s['details']['type']={'value':'beast','subtype':'','custom':''}
    s['details']['biography']['value']=f'<p>{bio} Summoned by the Protostalker Tracer\u2019s Protosaur Packmate. AC 13 + your Wisdom modifier; HP {hp} + 5 \u00d7 your Tracer level. Primal Bond: add your Proficiency Bonus to its ability checks and saving throws. Understands the languages you know.</p>'
    s['traits'].update({'size':size,'dr':{'value':[]},'di':{'value':[]},'ci':{'value':[]}})
    items=[]
    st=copy.deepcopy(RB); st['_id']=mkid(aid+'strike'); st['name']='Proto Strike'; st['_key']=f'!actors.items!{aid}.{st["_id"]}'
    st['system']['description']['value']=f'<p>Melee Attack Roll: bonus equals your spell attack modifier, reach 5 ft. Hit: {dn}d{df} + 2 plus your Wisdom modifier Bludgeoning, Piercing, or Slashing damage.</p>'
    for x in st['system']['activities'].values():
        x['name']='Proto Strike'; x['attack']['type']={'value':'melee','classification':'spell'}; x['range']={'units':'ft','value':'5','override':False,'special':''}
        x['damage']['parts']=[dpart(dn,df,BPS,bonus='2')]
    items.append(st)
    for tn,td in traits+[('Primal Bond','Add your Proficiency Bonus to any ability check or saving throw the protosaur makes.')]:
        t=copy.deepcopy(TR); t['_id']=mkid(aid+tn); t['name']=tn; t['_key']=f'!actors.items!{aid}.{t["_id"]}'; t['system']['activities']={}; t['system']['description']['value']=f'<p>{td}</p>'; items.append(t)
    a['items']=items; a['effects']=[]
    D(f'bestiary/summons/protosaur-{nm.lower()}.yml',a); ptuu[nm]='Compendium.neon-odyssey.bestiary.Actor.'+aid
R=T+'protostalker/'
p=R+'protosaur-packmate-3.yml'; d=L(p); d['effects']=[]; did=d['_id']
sm={'_id':mkid(did+':r4summon'),'type':'summon','name':'Summon Protosaur','img':'','sort':0,'activation':{'type':'special','value':None,'condition':'When you finish a Long Rest','override':False},
   'consumption':{'targets':[],'scaling':{'allowed':False,'max':''},'spellSlot':False},'description':{'chatFlavor':''},'duration':{'units':'inst','override':False,'concentration':False,'value':'','special':''},
   'range':{'override':False,'units':'ft','value':'5','special':''},'target':{'override':False,'prompt':False,'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'','type':''}},'effects':[],'uses':{'spent':0,'recovery':[],'max':''},
   'bonuses':{'ac':'@abilities.wis.mod','hd':'','hp':'5 * @classes.tracer.levels','attackDamage':'@abilities.wis.mod','saveDamage':'','healing':''},'match':{'attacks':True,'proficiency':True,'saves':True,'ability':''},
   'profiles':[{'_id':mkid(did+n),'count':'1','cr':'','level':{'min':None,'max':None},'name':'Protosaur '+n,'uuid':u} for n,u in ptuu.items()],'summon':{'mode':'','prompt':True},'creatureSizes':[],'creatureTypes':[],'flags':{},'visibility':copy.deepcopy(VIS)}
setacts(d,[(sm['_id'],sm),act(d,'cmd','utility','Command Protosaur','bonus',flavor='The protosaur takes an action in its stat block (or Proto Strike in place of one of your attacks).')]); D(p,d)
p=R+'primal-rage-7.yml'; d=L(p); a=first(d); a['name']='Savage Wound (close)'; a['activation']=spc('End of the bleeding creature\u2019s turn'); a['target']=one()
i2,a2=act(d,'bleed','damage','Savage Wound (bleed)','special','Start of the wounded creature\u2019s turn',target=one()); dmg(a2,[dpart(1,8,[])])
setacts(d,[(a['_id'],a),(i2,a2),act(d,'ki','utility','Killer Instinct','bonus',flavor='The protosaur also takes the Dash, Disengage, Dodge, Help, or Hide action.')]); D(p,d)
p=R+'hunt-as-one-11.yml'; d=L(p); i1,a1=act(d,'hao','damage','Hunt as One (1d8)','special','Hit while your protosaur is within 5 ft of the target',target=one()); dmg(a1,[dpart(1,8,BPS+['force'])]); setacts(d,[(i1,a1)]); D(p,d)
p=R+'ancient-apex-15.yml'; d=L(p); setuses(d,1,'lr')
ap=eff(d,'Ancient Apex',[chg('system.bonuses.abilities.save','max(1, @abilities.wis.mod)','add')],'apex',duration=mins(1),desc='<p>Apex Onslaught: the protosaur makes two Proto Strikes when it takes the Attack action. Preternatural Packmates: Advantage on attacks against targets within 5 ft of your protosaur. Survival Sense: you and the protosaur add your Wisdom modifier to saving throws.</p>')
d['effects']=[ap]; setacts(d,[act(d,'roar','utility','Fearsome Roar','bonus','',uses(1),effects=[ap['_id']],duration=MIN(1))]); D(p,d)
# ---- X-Agent
X=T+'x-agent/'
p=X+'agent-of-the-unknown-3.yml'; d=L(p); d['system']['advancement']=dict([trait('agent',3,'Agent of the Unknown',choices=[{'count':1,'pool':['skills:arc','skills:his','skills:rel']}])])
setacts(d,[act(d,'esot','utility','Agent of the Unknown','special','Intelligence check with Arcana, History, or Religion',roll=roll('max(1, @abilities.wis.mod)','Bonus'))]); D(p,d)
p=X+'occultech-weapon-3.yml'; d=L(p); setacts(d,[act(d,'unc','utility','Uncanny Intrusion','special','Hit with your occultech weapon (damage becomes Psychic)')]); D(p,d)
p=X+'esoteric-revelation-7.yml'; d=L(p); a=first(d); a['name']='Occult Scouring (1d8)'; a['activation']=spc('Once per turn, hit with your occultech weapon'); a['target']=one(); D(p,d)
p=X+'secure-and-contain-11.yml'; d=L(p); a=first(d); a['name']='Containment Protocol'; a['activation']=spc('Bonus Action attack hits and the target is Bloodied'); a['target']=one()
for e in d['effects']: e['duration']=rnd(1)
D(p,d)
p=X+'rewrite-the-truth-15.yml'; d=L(p); setuses(d,1,'lr'); d['effects']=[]; noadv(d,'ItemGrant')
v=d['system']['description']['value']; k=v.find('Benthos (BEN'); 
if k>0: v=v[:v.rfind('<p',0,k)] if v.rfind('<p',0,k)>0 else v[:k]
d['system']['description']['value']=v
setacts(d,[cast(d,'hold','Hold Monster (free)',P24+'phbsplHoldMonste',5,'action','',uses(1)),cast(d,'mod','Modify Memory (free)',P24+'phbsplModifyMemo',5,'action','',uses(1))]); D(p,d)
p=T+'class-features/omni-traversal-6.yml'; d=L(p)
for e in d['effects']:
    if e['name']=='Roving': e['name']='Omni-Traversal'
D(p,d)
print('round4 tracer done')
