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
# ================= ROUND 5: PRIMALIST =================
PR='features/primalist/'; PL='@classes.primalist.levels'; PC='feat:primal-channel'; WIS='max(1, @abilities.wis.mod)'
def newfeat(src,path,name,desc,ident):
    d=L(src); i=mkid('r5feat:'+name); d['_id']=i; d['_key']='!items!'+i; d['name']=name; d['system']['description']['value']=desc
    d['system']['identifier']=ident; d['system']['activities']={}; d['effects']=[]; d['system']['uses']={'max':'','spent':0,'recovery':[]}; D(path,d); return 'Compendium.neon-odyssey.features.Item.'+i
def resist(d,types,label,tag):
    return [eff(d,f'{label}: {t.title()}',[chg('system.traits.dr.value',t,'add')],tag+t,transfer=True,disabled=True,desc='<p>Turn on the type you chose.</p>') for t in types]
# ---- class: Archaic Pathways / Untamed Wrath choices
CF=PR+'class-features/'
gu=newfeat(CF+'archaic-pathways-1.yml',CF+'archaic-guardian.yml','Guardian','<p>Trained for battle, you gain proficiency with Martial weapons and training with Medium armor.</p>','guardian')
d=L(CF+'archaic-guardian.yml'); d['effects']=[eff(d,'Guardian',[chg('system.traits.weaponProf.value','mar','add'),chg('system.traits.armorProf.value','med','add')],'guard',transfer=True)]; D(CF+'archaic-guardian.yml',d)
na=newfeat(CF+'archaic-pathways-1.yml',CF+'archaic-naturalist.yml','Naturalist','<p>You know one extra cantrip from the Primalist spell list. In addition, you gain a bonus to your Intelligence (Arcana, Investigation, or Nature) checks equal to your Wisdom modifier (minimum bonus of +1).</p>','naturalist')
d=L(CF+'archaic-naturalist.yml'); d['effects']=[eff(d,'Naturalist',[chg(f'system.skills.{s}.bonuses.check',WIS,'add') for s in ('arc','inv','nat')],'nat',transfer=True)]; D(CF+'archaic-naturalist.yml',d)
ec=newfeat(CF+'untamed-wrath-7.yml',CF+'wrath-elemental-chaos.yml','Elemental Chaos','<p>Once on each of your turns when you hit a creature with an attack roll using a weapon or a Primal Form\u2019s attack, you can cause the target to take an extra 1d8 Acid, Cold, Fire, Lightning, or Thunder damage (choose when you hit). <strong>Force of the Ancients (15):</strong> 2d8.</p>','elemental-chaos')
d=L(CF+'wrath-elemental-chaos.yml'); i,a=act(d,'chaos','damage','Elemental Chaos','special','Once per turn when you hit with a weapon or Primal Form attack',target=one())
dmg(a,[dpart(None,None,['acid','cold','fire','lightning','thunder'],'@scale.primalist.elemental-fury')]); setacts(d,[(i,a)]); D(CF+'wrath-elemental-chaos.yml',d)
fm=newfeat(CF+'untamed-wrath-7.yml',CF+'wrath-ferocious-mysticism.yml','Ferocious Mysticism','<p>Add your Wisdom modifier to the damage you deal with any Primalist cantrip. <strong>Force of the Ancients (15):</strong> when you cast a Primalist cantrip with a range of 10 feet or greater, the spell\u2019s range increases by 300 feet.</p>','ferocious-mysticism')
p='classes/primalist/primalist.yml'; d=L(p); adv=d['system']['advancement']
for k,a in list(adv.items()):
    c=a.get('configuration',{})
    if a['type']=='ItemChoice' and a['title']=='Primal Order': a['title']='Archaic Pathways'; c['pool']=[{'uuid':gu},{'uuid':na}]; a['hint']='Choose Guardian or Naturalist.'
    if a['type']=='ItemChoice' and a['title']=='Elemental Fury': a['title']='Untamed Wrath'; c['pool']=[{'uuid':ec},{'uuid':fm}]; a['hint']='Choose Elemental Chaos or Ferocious Mysticism.'
    if a['type']=='ScaleValue' and c.get('identifier') in ('wild-shape','known-forms'): del adv[k]
    if a['type']=='ScaleValue' and c.get('identifier')=='wild-shape-uses': a['title']='Primal Channel'
    if a['type']=='ScaleValue' and c.get('identifier')=='elemental-fury': a['title']='Elemental Chaos'
    if a['type']=='Trait' and a['title']=='Primalistic': a['title']='Speech of the Untamed'; c['grants']=['languages:neonOdyssey:clysmic']
ti,ta=trait('primtool',1,'Tool Proficiencies',['tool:herb']); adv[ti]=ta
for a in adv.values():
    if a['type']=='ScaleValue' and a['configuration'].get('identifier')=='wild-shape-uses': a['configuration']['scale']={'2':{'value':2},'6':{'value':3},'17':{'value':4}}
D(p,d)
# ---- Speech of the Untamed: Speak with Animals
p=CF+'speech-of-the-untamed-1.yml'; d=L(p); i,a=cast(d,'swa','Speak with Animals (always prepared)',P24+'phbsplSpeakwithA',1); a['consumption']['spellSlot']=True; setacts(d,[(i,a)]); D(p,d)
# ---- Primal Channel: Call Wildling + Primal Form transform + temp HP
p=CF+'primal-channel-2.yml'; d=L(p); d['effects']=[]
FORMS={'Ambush Form':'0coZyTudCtYtklqg','Battle Form':'Q6V1SUYogllCcBSQ','Swift Form':'0EGRvzqVxNKjLZQ1'}
tr=next(a for a in d['system']['activities'].values() if a['type']=='transform'); tr['name']='Primal Form'
tr['profiles']=[{'cr':'','name':n,'_id':mkid('r5pf'+n),'uuid':'Compendium.neon-odyssey.bestiary.Actor.'+u,'sizes':[],'types':[],'movement':[],'level':{'min':None,'max':None}} for n,u in FORMS.items()]
tr['transform']={'customize':False,'identifier':'primalist','preset':'wildshape'}; tr['consumption']['spellSlot']=False; tr['img']=''
tr['description']={'chatFlavor':'Lasts hours equal to half your Primalist level. Use "Primal Form: Temporary HP" after shifting.'}
th,ta=act(d,'thp','heal','Primal Form: Temporary HP','special','When you assume a Primal Form (Hardy: twice your level)'); ta['healing']=heal(PL,'temphp')
cw,ca=cast(d,'wild','Call Wildling',PNO+'PTGbnlcUXBRMfbeO',2,'action','',uses(1)); ca['spell']['properties']=['vocal','somatic']; ca['description']['chatFlavor']='Elemental or Monstrosity; disappears when you finish a Long Rest.'
setacts(d,[(tr['_id'],tr),(th,ta),(cw,ca)]); D(p,d)
# ---- Primal Form actors
for fn,ac,spd,atkname,die,extra in [('ambush-form',10,'40','Primal Pounce',6,'pounce'),('battle-form',12,'30','Primal Thrash',8,'thrash'),('swift-form',10,'50','Primal Strike',6,'')]:
    p='bestiary/summons/'+fn+'.yml'; a=L(p); s=a['system']
    s['attributes']['ac']={'calc':'custom','formula':f'{ac} + @abilities.wis.mod','flat':None}; s['attributes']['movement']['walk']=spd
    for it in a['items']:
        acts=it['system'].get('activities',{})
        if it['name']==atkname:
            x=next(iter(acts.values())); x['type']='attack'; x['name']=atkname; x['activation']['type']='action'; x['consumption']['spellSlot']=False
            x['range']={'units':'ft','value':'5','override':False,'special':''}; x['target']=one()
            atk(x,'melee','spell','wis',[dpart(1,die,BPS,bonus='@abilities.wis.mod')])
            pairs=[(x['_id'],x)]
            if extra=='pounce':
                i2,a2=act(it,'pounce','damage','Pounce Extra Damage','special','You moved at least 20 feet before the hit',target=one()); dmg(a2,[dpart(1,6,BPS)]); pairs.append((i2,a2))
            if extra=='thrash':
                i2,a2=act(it,'prone','save','Thrash: Knock Prone','special','Target no larger than you',target=one()); svdc(a2,'str',SPDC); pairs.append((i2,a2))
            it['system']['activities']={i:v for i,v in pairs}
        if it['name']=='Pack Protection':
            x=next(iter(acts.values()),None)
            if x: x['activation']['type']='reaction'; x['roll']=roll('1d8 + @abilities.wis.mod','Damage reduced')
    D(p,a)
# ---- Aspects
AS=PR+'primal-aspects/'
def aspeff(fn,name,changes):
    p=AS+fn+'.yml'; d=L(p); d['effects']=[eff(d,name,changes,'asp'+fn,transfer=True)]; D(p,d)
aspeff('aquatic','Aquatic',[chg('system.attributes.movement.speeds.swim','@attributes.movement.speed','upgrade')])
aspeff('burrower','Burrower',[chg('system.attributes.movement.speeds.burrow','@attributes.movement.speed','upgrade')])
aspeff('climber','Climber',[chg('system.attributes.movement.speeds.climb','@attributes.movement.speed','upgrade')])
aspeff('echolocation','Echolocation',[chg('system.attributes.senses.ranges.blindsight','30','upgrade')])
aspeff('tremorsense','Tremorsense',[chg('system.attributes.senses.ranges.tremorsense','60','upgrade')])
aspeff('flight','Flight',[chg('system.attributes.movement.speeds.fly','@attributes.movement.speed','upgrade')])
p=AS+'environmental-adaptation.yml'; d=L(p); d['effects']=resist(d,['acid','cold','fire','lightning','poison'],'Environmental Adaptation','env'); D(p,d)
p=AS+'venomous.yml'; d=L(p); a=first(d); a['name']='Venomous'; a['activation']=spc('You hit with an attack'); a['target']=one(); dmg(a,[dpart(None,None,['poison'],'(@classes.primalist.levels >= 8 ? 2 : 1)d6')]); D(p,d)
p=AS+'swallow.yml'; d=L(p); i,a=act(d,'swal','damage','Swallow (Acid)','special','End of each of your turns while a creature is swallowed',target=one()); dmg(a,[dpart(3,6,['acid'])])
d['effects']=[eff(d,'Swallowed',[],'swal',statuses=['blinded','restrained'])]; i0,a0=act(d,'sw0','utility','Swallow','action','A creature you are grappling that is smaller than you',target=one(),effects=[d['effects'][0]['_id']]); setacts(d,[(i0,a0),(i,a)]); D(p,d)
p=AS+'web-spinner.yml'; d=L(p); d['effects']=[eff(d,'Webbed',[],'web',statuses=['restrained'])]; i,a=act(d,'web','save','Web (Recharge 5\u20136)','action','',rng=ft(60),target=one(),effects=[d['effects'][0]['_id']]); svdc(a,'dex',SPDC); a['uses']={'spent':0,'max':'1','recovery':[{'period':'recharge','formula':'5','type':'recoverAll'}]}; a['consumption']['targets']=[{'type':'activityUses','value':'1','target':'','scaling':{}}]; setacts(d,[(i,a)]); D(p,d)
p=AS+'diminutive.yml'; d=L(p); a=first(d); a['name']='Impose Disadvantage'; a['activation']['condition']='A creature you can see targets you with an attack'; D(p,d)
p=AS+'thick-hide.yml'; d=L(p); D(p,d)
# ---- Hivemind
H=PR+'hivemind/'
p=H+'cacophonous-swarm-3.yml'; d=L(p); noacteff(d,{'Unconscious'})
ex=eff(d,'Exhaustion (Entropy)',[],'exh',statuses=['exhaustion'],duration=rnd(1)); d['effects'].append(ex); EIDS=[e['_id'] for e in d['effects']]
base=first(d); pairs=[]
for tag,n,lo,hi in [('s1',1,None,5),('s2',2,6,13),('s4',4,14,None)]:
    a=copy.deepcopy(base); a['_id']=mkid(d['_id']+':r5'+tag); a['name']=f'Cacophonous Swarm ({n}d6)'; a['target']=one(); a['range']=ft(10 if n==1 else 15)
    svdc(a,'con',SPDC); dmg(a,[dpart(n,6,['necrotic','cold','acid','lightning','psychic'])],'half' if n==4 else 'none')
    a['effects']=[{'_id':e,'riders':{'activity':[],'effect':[],'item':[]}} for e in EIDS]; a['consumption']['targets']=[]; a['consumption']['spellSlot']=False
    a['visibility']=copy.deepcopy(VIS); a['visibility']['identifier']='primalist'; a['visibility']['level']={'min':lo,'max':hi}; a['activation']={'type':'bonus','value':None,'override':False,'condition':'Swarm is active'}
    pairs.append((a['_id'],a))
mi,ma=act(d,'man','utility','Manifest Swarm','bonus','',[{'type':'itemUses','value':'1','target':PC,'scaling':{}}],duration=MIN(10),flavor='Then target a creature with Cacophonous Swarm.')
xi,xa=act(d,'extra','damage','Tone: Extra 1d6 Necrotic (Entropy/Thrill)','special','',target=one()); dmg(xa,[dpart(1,6,['necrotic'])])
setacts(d,[(mi,ma)]+pairs+[(xi,xa)]); D(p,d)
p=H+'swarming-corruption-6.yml'; d=L(p); d['effects']=resist(d,['cold','acid','lightning','psychic'],'Discordant Resistance','dres')+[eff(d,'Devouring Swarm',[chg('system.attributes.ac.bonus','-1','add')],'dev',duration=rnd(1))]; D(p,d)
def tonechoice(sub,lv,cnt,names):
    i=mkid(f'r5tone:{lv}'); return i,{'_id':i,'type':'ItemChoice','level':lv,'title':'Hivemind Spells','hint':'Pick the spells of your Discordant Tone (Entropy, Instinct, Progress or Thrill).',
      'configuration':{'choices':{str(lv):{'count':cnt,'replacement':False}},'allowDrops':False,'pool':[{'uuid':u} for u in names],'restriction':{'type':'','subtype':'','level':'','list':[]},'spell':{'ability':[],'preparation':'always','uses':{'max':'','per':'','requireSlot':False},'method':'spell','prepared':2},'type':'spell'},'value':{}}
S=lambda x:P24+x
TONES={3:(2,[S('phbsplBane000000'),S('phbsplRayofEnfee'),S('phbsplFaerieFire'),S('phbsplWeb0000000'),S('phbsplHoldPerson'),S('phbsplShield0000'),S('phbsplTashasHide'),S('phbsplMirrorImag')]),
       5:(1,[S('phbsplVampiricTo'),S('phbsplFly0000000'),S('phbsplLightningB'),S('phbsplHypnoticPa')]),
       7:(1,[S('phbsplBlight0000'),S('phbsplVitriolicS'),PNO+'nw8WLScRIXy19tAp',S('phbsplConfusion0')]),
       9:(1,[S('phbsplConeofCold'),S('phbsplInsectPlag'),S('phbsplAnimateObj'),S('phbsplMislead000')])}
p=H+'hivemind-spells-3.yml'; d=L(p); old=next(iter(d['system']['advancement'].values()),None); spc_cfg=(old or {}).get('configuration',{}).get('spell') or {'ability':[],'uses':{'max':'','per':'','requireSlot':False},'method':'spell','prepared':2}
d['system']['advancement']={}; d['system']['description']['value']+='<p><em>Your spells are granted by the Discordant Tone you choose.</em></p>'; D(p,d)
TONEDEF=[('Entropy','cold',0),('Instinct','acid',1),('Progress','lightning',2),('Thrill','psychic',3)]
tuuids=[]
for tn,dt,ix in TONEDEF:
    fn=H+f'discordant-tone-{tn.lower()}.yml'
    u=newfeat(H+'discordant-tone-3.yml',fn,f'Discordant Tone: {tn}',f'<p>Your tone is {tn}. Its damage type is {dt.title()}: when you deal damage with a spell or Hivemind feature, you can change the damage type to {dt.title()}.</p><p>You always have this tone\'s Hivemind spells prepared.</p>',f'discordant-tone-{tn.lower()}')
    td=L(fn); adv={}
    for lv,(cnt,pool) in TONES.items():
        picks=pool[ix*2:ix*2+2] if lv==3 else [pool[ix]]
        gi,ga=grant(f'tone:{tn}:{lv}',lv,f'Hivemind Spells ({tn})',picks); ga['configuration']['spell']=copy.deepcopy(spc_cfg); adv[gi]=ga
    td['system']['advancement']=adv; D(fn,td); tuuids.append(u)
p=H+'discordant-tone-3.yml'; d=L(p); ci=mkid('r5tonechoice')
d['system']['advancement']={ci:{'_id':ci,'type':'ItemChoice','level':3,'title':'Discordant Tone','hint':'Choose Entropy (Cold), Instinct (Acid), Progress (Lightning) or Thrill (Psychic).',
  'configuration':{'choices':{'3':{'count':1,'replacement':False}},'allowDrops':False,'pool':[{'uuid':u} for u in tuuids],'restriction':{'type':'','subtype':'','level':'','list':[]},'spell':None,'type':'feat'},'value':{}}}; D(p,d)
p=H+'cacophonous-swarm-3.yml'; d=L(p); noadv(d,'ItemGrant'); D(p,d)
# ---- Splicer / Worldspeaker / Xenotrainer spell fixes
def addspell(fn,lv,add=(),drop=()):
    d=L(fn); a=next(x for x in d['system']['advancement'].values() if x['level']==lv)
    a['configuration']['items']=[x for x in a['configuration']['items'] if x['uuid'] not in drop]+[{'uuid':u,'optional':False,'sort':0} for u in add]; D(fn,d)
addspell(PR+'splicer/splicer-spells-3.yml',3,[PNO+'RixDonTjNecGTNDP',S('phbsplWeb0000000')])
addspell(PR+'worldspeaker/worldspeaker-spells-3.yml',3,[PNO+'9j1zwLFm4wGwP9q1'])
addspell(PR+'xenotrainer/xenotrainer-spells-3.yml',3,[S('phbsplAid0000000')],[S('phbsplLight00000')])
# ---- Splicer features
SP=PR+'splicer/'
p=SP+'chimeric-splicing-3.yml'; d=L(p)
b1,ba=act(d,'barb','damage','Barbed Spines','reaction','A creature within 5 feet hits you with an attack roll',target=one()); dmg(ba,[dpart(1,8,['piercing'],bonus='@abilities.wis.mod')])
g1,ga=act(d,'tend','attack','Grasping Tendril','action','',rng=ft(10),target=one()); atk(ga,'melee','unarmed','wis',[dpart(1,6,['bludgeoning'],bonus='@abilities.wis.mod')])
n1,na_=act(d,'nox','damage','Noxious','special','A creature starts its turn within 5 feet of you',target=one()); dmg(na_,[dpart(1,6,['poison'])])
setacts(d,[(b1,ba),(g1,ga),(n1,na_)]); D(p,d)
p=SP+'radical-modification-10.yml'; d=L(p); par=next((e for e in d['effects'] if e['name']=='Paralyzed'),None)
if par: par['duration']=rnd(1)
d['effects']=([par] if par else [])+resist(d,['force','necrotic','psychic','radiant'],'Alien Adaptation','alien')
ni,na2=act(d,'neuro','save','Neurotoxin','special','You hit with Piercing or Slashing damage',target=one(),effects=[par['_id']] if par else []); svdc(na2,'con',SPDC); dmg(na2,[dpart(2,8,['poison'])],'half')
si,sa=act(d,'shriek','save','Shriek (Recharge 5\u20136)','bonus','',target=area('radius',30)); svdc(sa,'con',SPDC); dmg(sa,[dpart(4,8,['thunder'])],'none')
sa['uses']={'spent':0,'max':'1','recovery':[{'period':'recharge','formula':'5','type':'recoverAll'}]}; sa['consumption']['targets']=[{'type':'activityUses','value':'1','target':'','scaling':{}}]
ri,ra=act(d,'regen','heal','Regeneration','special','Start of your turn while Bloodied (at least 1 HP)'); ra['healing']=heal('5')
setacts(d,[(ni,na2),(si,sa),(ri,ra)]); D(p,d)
# ---- Worldspeaker
W=PR+'worldspeaker/'; WT=['acid','piercing','poison','necrotic','psychic','slashing','cold','lightning','thunder','bludgeoning','fire','radiant']
p=W+'planetary-embodiment-3.yml'; d=L(p); d['effects']=[eff(d,'Defiled: Disadvantage',[],'defd',duration=rnd(1),desc='<p>Disadvantage on attack rolls and ability checks until the start of your next turn.</p>')]
e1,ea=act(d,'emb','utility','Embody World Soul','bonus','',[{'type':'itemUses','value':'1','target':PC,'scaling':{}}],duration=MIN(10),flavor='Free once per Long Rest if you embody the bond matching the world you are on.')
a1,aa=act(d,'abund','heal','Abundant: Heal','special','When you activate this embodiment',rng=ft(30),target=one('ally')); aa['healing']=dpart(1,8,['healing'])
d1,da=act(d,'defil','save','Defiled','bonus','',rng=ft(30),target=one(),effects=[d['effects'][0]['_id']]); svdc(da,'con',SPDC); dmg(da,[dpart(None,None,WT,WIS)],'full')
t1,ta2=act(d,'turb','save','Turbulent: Push 10 ft','bonus','Speed halved until the start of your next turn',rng=ft(30),target=one()); svdc(ta2,'str',SPDC)
u1,ua=act(d,'unfor','save','Unforgiving','bonus','',rng=ft(30),target=one()); svdc(ua,'dex',SPDC); dmg(ua,[dpart(None,None,WT,f'({WIS})d6')],'none')
setacts(d,[(e1,ea),(a1,aa),(d1,da),(t1,ta2),(u1,ua)]); D(p,d)
p=W+'world-souls-mantle-6.yml'; d=L(p); d['effects']=resist(d,WT,'Worldly Resistance','wres'); D(p,d)
p=W+'biome-sanctuary-10.yml'; d=L(p); a=first(d); a['name']='Spend Hit Die'; a['activation']['condition']='You or an ally take damage of your Worldly Resistance type'; a['roll']=roll('1d@attributes.hd.largestFace','Hit Points regained'); D(p,d)
p=W+'the-world-speaks-14.yml'; d=L(p); a=first(d); a['name']='Empower Embodiment'
ci,ca2=cast(d,'cwn','Commune with Nature (free)',P24+'phbsplCommunewit',5,'action','',[]); actuse(ca2,1,'lr')
d['system']['activities'][ci]=ca2; D(p,d)
# ---- Xenotrainer summons
X5=PR+'xenotrainer/'
tur=L('bestiary/summons/rivet-turret.yml'); RB=next(i for i in tur['items'] if i['name']=='Rivet Burst'); TRT=next(i for i in tur['items'] if i['name']=='Relocate')
XENO=[('Arctic',{'walk':'30','swim':'60'},(8,'cold'),'Elemental Spray','ranged/melee 5 or 60 ft',{'di':['cold']},
       [('Amphibious','The xenomon can breathe air and water. While you and the xenomon are on the same plane of existence, you gain this trait.')],('Icy Splash','str','radius',10,'cold','prone')),
      ('Tropical',{'walk':'30','climb':'40'},(6,'acid'),'Elemental Whip','reach 10 ft; same size or smaller is Grappled (escape DC = your spell save DC)',{'dr':['acid','poison']},
       [('Rooted','While on the ground, the xenomon can\u2019t be moved against its will.')],('Seed Burst','con','cube',20,'acid','poisoned')),
      ('Volcanic',{'walk':'30','burrow':'30'},(6,'fire'),'Elemental Swipe','reach 5 ft; the target starts burning',{'di':['fire']},
       [('Illumination','The xenomon sheds Bright Light in a 20-foot radius and Dim Light for an additional 20 feet.')],('Magma Breath','dex','cone',30,'fire',None))]
xu={}
for nm,mv,(df,dt),an,adesc,tr,traits,(nn,nsv,nshape,nsz,ndt,ncond) in XENO:
    a=copy.deepcopy(tur); aid=mkid('r5xeno:'+nm); a['_id']=aid; a['_key']='!actors!'+aid; a['name']=nm+' Xenomon'; a['prototypeToken']['name']=nm+' Xenomon'; s=a['system']
    for k,v in zip(['str','dex','con','int','wis','cha'],(14,14,15,8,14,11)): s['abilities'][k]={'value':v,'proficient':0}
    s['attributes']['ac']={'flat':13,'calc':'natural'}; s['attributes']['hp'].update({'value':5,'max':5})
    s['attributes']['movement']={'walk':mv.get('walk','0'),'climb':mv.get('climb',''),'swim':mv.get('swim',''),'fly':'','burrow':mv.get('burrow',''),'units':'ft','hover':False}
    s['attributes']['senses']['ranges']['darkvision']=60
    if nm=='Volcanic': s['attributes']['senses']['ranges']['tremorsense']=60
    s['details']['type']={'value':'monstrosity','subtype':'','custom':''}
    s['details']['biography']['value']=f'<p>Small Monstrosity summoned by the Xenotrainer\u2019s Xenomon Partner. AC 13 + your Wisdom modifier; HP 5 + 5 \u00d7 your Primalist level. Metamorphosis: Medium at level 6, Large at level 14.</p>'
    s['traits'].update({'size':'sm','dr':{'value':tr.get('dr',[])},'di':{'value':tr.get('di',[])},'ci':{'value':[]}})
    items=[]
    st=copy.deepcopy(RB); st['_id']=mkid(aid+'atk'); st['name']=an; st['_key']=f'!actors.items!{aid}.{st["_id"]}'
    st['system']['description']['value']=f'<p>Attack roll: bonus equals your spell attack modifier, {adesc}. Hit: 1d{df} plus your Wisdom modifier {dt.title()} damage.</p>'
    for x in st['system']['activities'].values():
        x['name']=an; x['attack']['type']={'value':'melee' if nm!='Arctic' else 'ranged','classification':'spell'}
        x['range']={'units':'ft','value':'60' if nm=='Arctic' else ('10' if nm=='Tropical' else '5'),'override':False,'special':''}; x['damage']['parts']=[dpart(1,df,[dt])]
    items.append(st)
    sv=copy.deepcopy(RB); sv['_id']=mkid(aid+'new'); sv['name']=f'{nn} (1/Summon; Level 10+)'; sv['_key']=f'!actors.items!{aid}.{sv["_id"]}'
    sv['system']['description']['value']=f'<p>{nsv.upper()} save vs your spell save DC. Failure: 4d8 {ndt.title()} damage{", and "+ncond if ncond else ""}. Success: half damage.</p>'
    x=next(iter(sv['system']['activities'].values())); x['type']='save'; x['name']=nn; x.pop('attack',None); x['save']={'ability':[nsv],'dc':{'calculation':'','formula':'@attributes.spell.dc'}}
    x['damage']={'onSave':'half','parts':[dpart(4,8,[ndt])]}; x['target']=area(nshape,nsz); x['range']={'units':'ft','value':'120' if nshape=='radius' else '','override':False,'special':''}
    sv['system']['activities']={x['_id']:x}; items.append(sv)
    for tn,td in traits+[('Primal Bond','Add your Proficiency Bonus to any ability check or saving throw the xenomon makes.')]:
        t=copy.deepcopy(TRT); t['_id']=mkid(aid+tn); t['name']=tn; t['_key']=f'!actors.items!{aid}.{t["_id"]}'; t['system']['activities']={}; t['system']['description']['value']=f'<p>{td}</p>'; items.append(t)
    a['items']=items; a['effects']=[]
    D(f'bestiary/summons/xenomon-{nm.lower()}.yml',a); xu[nm]='Compendium.neon-odyssey.bestiary.Actor.'+aid
p=X5+'xenomon-partner-3.yml'; d=L(p); d['effects']=[]; did=d['_id']
sm={'_id':mkid(did+':r5summon'),'type':'summon','name':'Summon Xenomon','img':'','sort':0,'activation':{'type':'action','value':None,'condition':'','override':False},
   'consumption':{'targets':[{'type':'itemUses','value':'1','target':PC,'scaling':{}}],'scaling':{'allowed':False,'max':''},'spellSlot':False},'description':{'chatFlavor':''},'duration':{'units':'inst','override':False,'concentration':False,'value':'','special':''},
   'range':{'override':False,'units':'ft','value':'30','special':''},'target':{'override':False,'prompt':False,'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'','type':''}},'effects':[],'uses':{'spent':0,'recovery':[],'max':''},
   'bonuses':{'ac':'@abilities.wis.mod','hd':'','hp':'5 * @classes.primalist.levels','attackDamage':'@abilities.wis.mod','saveDamage':'','healing':''},'match':{'attacks':True,'proficiency':True,'saves':True,'ability':''},
   'profiles':[{'_id':mkid(did+n),'count':'1','cr':'','level':{'min':None,'max':None},'name':n+' Xenomon','uuid':u} for n,u in xu.items()],'summon':{'mode':'','prompt':True},'creatureSizes':[],'creatureTypes':[],'flags':{},'visibility':copy.deepcopy(VIS)}
setacts(d,[(sm['_id'],sm),act(d,'cmd','utility','Command Xenomon','bonus',flavor='The xenomon takes an action in its stat block (or its Elemental attack in place of one of your attacks).')]); D(p,d)
p=X5+'metamorphosis-6.yml'; d=L(p); a=first(d); a['name']='Switch Out'; a['target']=area('radius',10); svdc(a,'dex',SPDC); dmg(a,[dpart(2,6,['cold','acid','fire'])],'none')
a['activation']['condition']='Replace your summoned xenomon (damage type of the new xenomon)'; D(p,d)
p=X5+'doubled-adaptation-10.yml'; d=L(p); D(p,d)
print('round5 primalist done')
# ---- Worldspeaker / Xenotrainer gaps (pass 2)
W=PR+'worldspeaker/'; X=PR+'xenotrainer/'
p=W+'world-bond-3.yml'; d=L(p); gi,ga=grant('wbond-elem',3,'World Bond Cantrip',[P24+'phbsplElementali']); ga['configuration']['optional']=True; d['system']['advancement']={gi:ga}
d['effects']=[eff(d,f'World Bond: {b}',[],'wb'+b,transfer=True,disabled=True,desc=f'<p>Turn on after a Long Rest to mark your {b} bond. Damage types: {t}.</p>') for b,t in [('Abundant','Acid, Piercing, Poison'),('Defiled','Necrotic, Psychic, Slashing'),('Turbulent','Cold, Lightning, Thunder'),('Unforgiving','Bludgeoning, Fire, Radiant')]]; D(p,d)
p=X+'xenomon-partner-3.yml'; d=L(p)
for a in d['system']['activities'].values():
    if a['type']=='summon': a['creatureSizes']=['sm','med','lg']
D(p,d)
p=X+'doubled-adaptation-10.yml'; d=L(p)
ci,ca=act(d,'cinf','utility','Cosmic Infusion','special','When you summon a xenomon',flavor='Choose Lightning, Necrotic, Psychic, Radiant or Thunder: the xenomon gains Immunity to it and can deal that type instead.')
ni,na3=act(d,'nmove','utility','New Move','special','Your xenomon uses its level 10+ action',flavor='Once used, it can\u2019t be used again until you spend Primal Channel to summon a new xenomon.')
setacts(d,[(ci,ca),(ni,na3)]); D(p,d)
p=X+'metamorphic-champion-14.yml'; d=L(p)
si2,sa2=act(d,'supeff','utility','Super Effective','special','Based on your xenomon\u2019s Cosmic Infusion',flavor='Lightning: Incapacitated; Necrotic: Frightened; Radiant: Blinded (on a failed save vs its level 10+ action, until the start of your next turn). Psychic: Advantage on the next attack against a creature it hits. Thunder: Fly Speed equal to twice its Speed.')
setacts(d,[(si2,sa2)]); D(p,d)
print('round5 pass2 done')
