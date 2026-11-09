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
def newfeat(src,path,name,desc,ident):
    d=L(src); i=mkid('r5feat:'+name); d['_id']=i; d['_key']='!items!'+i; d['name']=name; d['system']['description']['value']=desc
    d['system']['identifier']=ident; d['system']['activities']={}; d['effects']=[]; d['system']['uses']={'max':'','spent':0,'recovery':[]}; D(path,d); return 'Compendium.neon-odyssey.features.Item.'+i
def resist(d,types,label,tag):
    return [eff(d,f'{label}: {t.title()}',[chg('system.traits.dr.value',t,'add')],tag+t,transfer=True,disabled=True,desc='<p>Turn on the type you chose.</p>') for t in types]
# ================= ROUND 6: ENFORCER =================
E_='features/enforcer/'; EL='@classes.enforcer.levels'; CHA='max(1, @abilities.cha.mod)'
FU='Compendium.neon-odyssey.features.Item.'
def ccons(): return [{'type':'itemUses','value':'1','target':CC,'scaling':{}}]
def iu(): return [{'type':'itemUses','value':'1','target':'','scaling':{}}]
DT=['acid','bludgeoning','cold','fire','force','lightning','necrotic','piercing','poison','psychic','radiant','slashing','thunder']
# ---- class
p=E_+'class-features/fighting-style-2.yml'; d=L(p); base=L(E_+'class-features/extra-attack-5.yml')
n=copy.deepcopy(base); n['_id']=mkid('r6fs:adj'); n['_key']='!items!'+n['_id']; n['name']='Cosmic Adjudicator'; n['effects']=[]
n['system']['description']['value']='<p>You learn two Oracle cantrips of your choice (Guidance and Sacred Flame are recommended). The chosen cantrips count as Enforcer spells for you, and Charisma is your spellcasting ability for them. Whenever you gain an Enforcer level, you can replace one of these cantrips with another Oracle cantrip.</p>'
n['system']['identifier']='cosmic-adjudicator'; n['system']['activities']={}; n['system']['advancement']={}
n['system']['type']={'value':'feat','subtype':'fightingStyle'}; n['system']['requirements']='Enforcer'; n['system']['prerequisites']={'level':None,'items':[],'repeatable':False}
D(E_+'class-features/cosmic-adjudicator.yml',n)
for a in d['system']['advancement'].values():
    if a['type']=='ItemChoice':
        a['configuration']['pool']=[{'uuid':u,'sort':0} for u in [FU+n['_id']]+['Compendium.dnd5e.feats24.Item.'+x for x in ['phbfstArchery000','phbfstDefense000','phbfstGreatWeapo','phbfstTwoWeaponF']]]
        a['level']=2; a['title']='Fighting Style'
D(p,d)
p=E_+'class-features/relentless-ride-5.yml'; d=L(p)
for a in d['system']['advancement'].values(): a['configuration']['items'][0]['uuid']=PNO+'pMUW91MVaFti0hpy'
D(p,d)
p=E_+'class-features/cosmic-conduit-3.yml'; d=L(p); noacteff(d,['Incapacitated'])
for e in d['effects']: e['duration']=mins(10)
D(p,d)
p=E_+'class-features/invigorate-1.yml'; d=L(p); noacteff(d,['Poisoned']); D(p,d)
p=E_+'class-features/threat-suppression-9.yml'; d=L(p); noacteff(d,['Abjured'])
for e in d['effects']: e['duration']=mins(1)
a=first(d); a['range']=ft(60); a['target']=one('creature',CHA); D(p,d)
p=E_+'class-features/fearless-conviction-10.yml'; d=L(p); noacteff(d,['Frightened']); setacts(d,[])
for e in d['effects']: e['transfer']=True; e['description']='<p>Immunity to Frightened. Allies in your Zone of Safety get it too (applied automatically by the aura).</p>'
D(p,d)
p=E_+'class-features/cosmic-wrath-11.yml'; d=L(p)
d['effects'][0]['system']['changes']=[chg('system.bonuses.mwak.damage','1d8[radiant]','add'),chg('system.bonuses.rwak.damage','1d8[radiant]','add')]; D(p,d)
p=E_+'class-features/zone-of-safety-6.yml'; d=L(p)
d['effects'][0]['description']='<p>You add your Charisma modifier (min +1) to saving throws. Allied tokens in your Zone of Safety get the same bonus automatically.</p>'; D(p,d)
# ---- Arbiter
A_=E_+'arbiter/'
p=A_+'aspect-of-balance-3.yml'; d=L(p)
es=eff(d,'Imbued: Somber',[],'som',duration=mins(10),desc='<p>Somber: your imbued weapons can deal Necrotic damage; once per turn add twice your Charisma modifier (min 2).</p>')
ev=eff(d,'Imbued: Vital',[],'vit',duration=mins(10),desc='<p>Vital: your imbued weapons can deal Radiant damage; once per turn regain Charisma modifier (min 1) HP, excess as Temp HP.</p>')
d['effects']=[es,ev]
i1,a1=act(d,'isom','utility','Imbue: Somber','special','When you take the Attack action',ccons(),effects=[es['_id']],duration=MIN(10))
i2,a2=act(d,'ivit','utility','Imbue: Vital','special','When you take the Attack action',ccons(),effects=[ev['_id']],duration=MIN(10))
i3,a3=act(d,'ssom','damage','Somber Strike','special','Once per turn, when you hit with a Somber weapon'); dmg(a3,[dpart(None,None,['necrotic'],'max(2, 2 * @abilities.cha.mod)')])
i4,a4=act(d,'svit','heal','Vital Strike','special','Once per turn, when you hit with a Vital weapon'); a4['healing']=heal(CHA)
setacts(d,[(i1,a1),(i2,a2),(i3,a3),(i4,a4)]); D(p,d)
p=A_+'arbiter-spells-3.yml'; d=L(p); spc_cfg=copy.deepcopy(next(iter(d['system']['advancement'].values()))['configuration']['spell'])
ARB={3:(['phbsplBane000000',PNO+'3NqjXkINWCjCeBSt'],['phbsplCommand000','phbsplHealingWor']),5:(['phbsplHoldPerson','phbsplRayofEnfee'],[PNO+'4FFg2gtVtRPWV5RA','phbsplSuggestion']),
 9:(['phbsplFear000000',PNO+'PW3cPsltN2947cCR'],['phbsplRevivify00','phbsplSending000']),13:(['phbsplBlight0000','phbsplPhantasmal'],['phbsplCharmMonst','phbsplDivination']),17:(['phbsplAntilifeSh','phbsplContagion0'],['phbsplMassCureWo','phbsplScrying000'])}
U=lambda x: x if x.startswith('Compendium') else P24+x
adv={}
for lv,(so,vi) in ARB.items():
    for nm,lst in [('Somber',so),('Vital',vi)]:
        gi,ga=grant(f'arb:{nm}:{lv}',lv,f'Arbiter Spells ({nm})',[U(x) for x in lst]); ga['configuration']['spell']=copy.deepcopy(spc_cfg); adv[gi]=ga
d['system']['advancement']=adv; D(p,d)
p=A_+'harmonys-grasp-3.yml'; d=L(p); a=first(d); a['name']="Harmony's Grasp"; a['activation']=spc('In place of an attack (Attack action)'); a['activation']['type']='action'
a['range']=ft(30); a['target']=one(); D(p,d)
p=A_+'harmonic-vigil-7.yml'; d=L(p); setacts(d,[])
d['effects']=[eff(d,'Harmonic Vigil',[chg('system.traits.dr.value','necrotic','add'),chg('system.traits.dr.value','radiant','add')],'hv',transfer=True,desc='<p>Resistance to Necrotic and Radiant. Allies in your Zone of Safety get it too (applied automatically by the aura).</p>')]; D(p,d)
p=A_+'warden-of-life-and-death-15.yml'; d=L(p)
i1,a1=act(d,'sret','utility','Somber Retribution','reaction','A creature hits you or an ally in your Zone of Safety (Somber)',flavor="Make one melee attack against it, or use Harmony's Grasp on it without expending a use.")
i2,a2=act(d,'vdef','utility','Vital Deflection','reaction','You or an ally in your Zone of Safety takes damage (Vital)',roll=roll('2d8 + '+CHA,'Damage Reduced'))
setacts(d,[(i1,a1),(i2,a2)]); D(p,d)
p=A_+'embodiment-of-the-cycle-20.yml'; d=L(p)
es=eff(d,'Embodiment: Somber',[],'esom',duration=mins(10),desc="<p>Choking Grasp and Death Sentence are active.</p>")
ev=eff(d,'Embodiment: Vital',[],'evit',duration=mins(10),desc="<p>Harmony's Reach and Life Spring are active.</p>")
rs=[e for e in d['effects'] if e['name']=='Restrained'][0]; rs['duration']=rnd(1); d['effects']=[es,ev,rs]
i1,a1=act(d,'esom','utility','Embody: Somber','bonus','',iu(),effects=[es['_id']],duration=MIN(10))
i2,a2=act(d,'evit','utility','Embody: Vital','bonus','',iu(),effects=[ev['_id']],duration=MIN(10))
i3,a3=act(d,'chok','save','Choking Grasp','special',"A creature fails its save against Harmony's Grasp",effects=[rs['_id']]); svdc(a3,'str',SPDC); dmg(a3,[dpart(3,10,['necrotic'])],'half'); a3['target']=one()
i4,a4=act(d,'dsen','damage','Death Sentence','special','You hit a creature that is missing Hit Points'); dmg(a4,[dpart(2,10,['necrotic'])])
i5,a5=act(d,'lspr','heal','Life Spring','special','On activation and at the start of each of your turns'); a5['healing']=heal('10','temphp'); a5['target']=one()
setacts(d,[(i1,a1),(i2,a2),(i3,a3),(i4,a4),(i5,a5)]); D(p,d)
# ---- Cyberguard
C_=E_+'cyberguard/'
src=C_+'tactical-cybernetics-3.yml'; imps=[]
for nm,desc in [('Dermal-Fused Armor','<p>Your armor is integrated into your body and can’t be doffed except with surgery. When you use Invigorate to target another creature, you also regain half as many Hit Points (rounded down).</p>'),
    ('Optical Scanner','<p>You gain Darkvision with a range of 60 feet, and you have Advantage on Intelligence (Investigation) and Wisdom (Perception) checks.</p>'),
    ('Pursuit Chassis','<p>As a Bonus Action, you can take the Dash action, and your jump distance is doubled until the end of your turn.</p>'),
    ('Vox Amplifier','<p>Your voice can be audible to 300 feet. You can cast Command once without a spell slot (regained on a Long Rest), and a target of your Command has Disadvantage on the save.</p>')]:
    fp=C_+'implant-'+nm.lower().replace(' ','-')+'.yml'; u=newfeat(src,fp,nm,desc,'implant-'+nm.lower().replace(' ','-')); x=L(fp); x['system']['advancement']={}
    if nm=='Optical Scanner': x['effects']=[eff(x,nm,[chg('system.attributes.senses.ranges.darkvision','60','upgrade'),chg('system.skills.inv.roll.mode','1','add'),chg('system.skills.prc.roll.mode','1','add')],'opt',transfer=True)]
    if nm=='Pursuit Chassis': setacts(x,[act(x,'dash','utility','Pursuit Dash','bonus','',flavor='Dash; your jump distance is doubled until the end of your turn.')])
    if nm=='Vox Amplifier':
        i,a=cast(x,'vox','Command (Vox Amplifier)',P24+'phbsplCommand000',1); actuse(a,1,'lr'); setacts(x,[(i,a)])
    D(fp,x); imps.append(u)
d=L(src); setacts(d,[])
ch=copy.deepcopy(next(a for a in L(E_+'class-features/fighting-style-2.yml')['system']['advancement'].values() if a['type']=='ItemChoice'))
ch['_id']=mkid('r6:implants'); ch['title']='Cybernetic Systems'; ch['name']='Cybernetic Systems'; ch['hint']='Choose two implants.'; ch['level']=3; ch['configuration']['choices']={'3':{'count':2,'replacement':False}}
ch['configuration']['pool']=[{'uuid':u,'sort':0} for u in imps]
ti,ta=trait('cgtool',3,'Tool Proficiencies',['tool:art:tinker'])
gi,ga=grant('cgtools',3,"Engineer's Tools",[ 'Compendium.neon-odyssey.items.Item.33sXsmnMQakxMFCD'])
d['system']['advancement']={ch['_id']:ch,ti:ta,gi:ga}; D(src,d)
p=C_+'full-system-upgrade-15.yml'; d=L(p); d['system']['advancement']={}
d['system']['description']['value']+='<p><em>The module adds any Tactical Cybernetics implants you don’t already have when you gain this feature.</em></p>'; D(p,d)
p=C_+'peacekeeper-3.yml'; d=L(p); pk=eff(d,'Peacekeeper',[],'pk',duration=mins(10),desc='<p>You ignore Half Cover, and after you hit with a Ranged weapon you can cast Cosmic Smite as a Bonus Action (target makes a Con save or is Restrained).</p>')
rs=[e for e in d['effects'] if e['name']=='Restrained'][0]; rs['duration']=mins(1); d['effects']=[pk,rs]
i1,a1=act(d,'pk','utility','Imbue Ranged Weapon','special','When you take the Attack action',ccons(),effects=[pk['_id']],duration=MIN(10))
sa=first(d); sa['name']='Peacekeeper Restraint'; sa['activation']=spc('You hit with Cosmic Smite using a Ranged weapon'); sa['effects']=[RID(rs)]; sa['target']=one()
setacts(d,[(i1,a1),(sa['_id'],sa)]); D(p,d)
p=C_+'ballistic-shielding-7.yml'; d=L(p)
setacts(d,[act(d,'bs','utility','Ballistic Shielding','reaction','You or an ally in your Zone of Safety takes damage from a ranged attack',roll=roll(f'min(6, 3 + floor(({EL} - 5) / 4))','Damage Reduced'))]); D(p,d)
p=C_+'more-machine-than-mortal-20.yml'; d=L(p)
mm=eff(d,'More Machine than Mortal',[],'mmm',duration=mins(10),desc='<p>Body Reforged: you are a Construct. Disruptor Pulse: Cosmic Smite also Blinds and Deafens until the start of your next turn. Multi-Target Array: Reaction attack after a ranged hit. Threat Simulator: enemies can’t gain Advantage on attacks against you, and you ignore Disadvantage on your attacks and saves.</p>')
d['effects']=[mm]
setacts(d,[act(d,'mmm','utility','More Machine than Mortal','bonus','',iu(),effects=[mm['_id']],duration=MIN(10)),
  act(d,'mta','utility','Multi-Target Array','reaction','You hit a target with a Ranged weapon',flavor='Make one Ranged weapon attack against another target within range.')]); D(p,d)
# ---- Renegade
R_=E_+'renegade/'
p='classes/enforcer/renegade.yml'; d=L(p); cls=L('classes/enforcer/enforcer.yml')
sv=copy.deepcopy(next(a for a in cls['system']['advancement'].values() if a['type']=='ScaleValue' and a['configuration']['identifier']=='aura'))
sv['_id']=mkid('r6sv:street'); sv['title']='Street Brawler'; sv['configuration'].update({'identifier':'street-brawler','type':'dice','scale':{'3':{'number':1,'faces':6,'modifiers':[]},'5':{'number':1,'faces':8,'modifiers':[]},'11':{'number':1,'faces':10,'modifiers':[]},'17':{'number':1,'faces':12,'modifiers':[]}}})
sv['configuration'].pop('distance',None); d['system']['advancement'][sv['_id']]=sv; D(p,d)
SB='@scale.renegade.street-brawler + @abilities.str.mod'
p=R_+'dirty-fighting-3.yml'; d=L(p)
d['effects']=[eff(d,'Rowdy Defense',[chg('system.attributes.ac.calc','custom','override'),chg('system.attributes.ac.formula','10 + @abilities.dex.mod + @abilities.cha.mod','override')],'rowdy',transfer=True,desc='<p>AC 10 + Dex + Cha while you wear no armor (Shield allowed). Turn this off while wearing armor.</p>')]
i,a=act(d,'sb','attack','Street Brawler Strike','action','Unarmed Strike or improvised weapon',rng={'units':'ft','value':'5','override':False,'special':''},target=one()); atk(a,'melee','weapon','str',[dpart(None,None,['bludgeoning'],SB)])
setacts(d,[(i,a)]); D(p,d)
p=R_+'rage-of-the-streets-3.yml'; d=L(p); rg=eff(d,'Rage of the Streets',[],'rage',duration=mins(1),desc='<p>As a Bonus Action on each of your turns, make one Unarmed Strike or improvised weapon attack.</p>'); d['effects']=[rg]
i1,a1=act(d,'rage','utility','Rage of the Streets','bonus','',ccons(),effects=[rg['_id']],duration=MIN(1))
i2,a2=act(d,'rstr','attack','Rage Strike','bonus','While Rage of the Streets is active',rng={'units':'ft','value':'5','override':False,'special':''},target=one()); atk(a2,'melee','weapon','str',[dpart(None,None,['bludgeoning'],SB)])
setacts(d,[(i1,a1),(i2,a2)]); D(p,d)
p=R_+'beatdown-7.yml'; d=L(p); a=first(d); a['save']['dc']={'calculation':'str','formula':''}; a['name']='Beatdown'; a['target']=one(); D(p,d)
p=R_+'tough-as-nails-15.yml'; d=L(p); tn=eff(d,'Tough as Nails',[chg('system.traits.dr.value',t,'add') for t in BPS],'tough',duration=mins(1),desc='<p>Resistance to Bludgeoning, Piercing and Slashing; damage can’t break your Concentration.</p>'); d['effects']=[tn]
setacts(d,[act(d,'tn','utility','Tough as Nails','special','When you activate Rage of the Streets',effects=[tn['_id']],duration=MIN(1))]); D(p,d)
p=R_+'urban-legend-20.yml'; d=L(p); ul=eff(d,'Urban Legend',[chg('system.attributes.movement.walk','2','multiply')],'ul',duration=mins(1),desc='<p>Combo Breaker: two Unarmed Strike or improvised weapon attacks as a Bonus Action. Shrug It Off: Resistance to two damage types (turn on two Shrug It Off effects). Street Runner: Speed doubled.</p>')
d['effects']=[ul]+[eff(d,f'Shrug It Off: {t.title()}',[chg('system.traits.dr.value',t,'add')],'sio'+t,transfer=True,disabled=True,desc='<p>Turn on the two types you chose while Urban Legend lasts.</p>') for t in DT]
setacts(d,[act(d,'ul','utility','Urban Legend','special','When you activate Rage of the Streets',iu(),effects=[ul['_id']],duration=MIN(1))]); D(p,d)
# ---- Supersprite
S_=E_+'supersprite/'
p=S_+'supersprite-spells-3.yml'; d=L(p)
for a in d['system']['advancement'].values():
    us=[i['uuid'] for i in a['configuration']['items']]
    if a['level']==5 and P24+'phbsplAid0000000' not in us: a['configuration']['items'].append({'uuid':P24+'phbsplAid0000000','optional':False,'sort':0})
    if a['level']==13 and PNO+'pOQPNetkP9uakzDL' not in us: a['configuration']['items'].append({'uuid':PNO+'pOQPNetkP9uakzDL','optional':False,'sort':0})
D(p,d)
p=S_+'extra-life-3.yml'; d=L(p); a=first(d); a['type']='heal'; a['name']='Extra Life'; a['activation']=spc('You would drop to 0 Hit Points but aren’t killed outright')
a['healing']=heal('1 + 1d10 + '+CHA); a['description']['chatFlavor']='You drop to 1 HP instead, then expend and roll a Hit Point Die (the heal includes the 1 HP).'
a['consumption']['targets']=iu()+[{'type':'hitDice','value':'1','target':'smallest','scaling':{}}]; D(p,d)
p=S_+'heros-power-up-3.yml'; d=L(p)
e1=eff(d,'Dragon Pepper',[],'dp',duration=mins(1),desc='<p>Reach +10 ft; no Disadvantage at long range; once per turn a weapon hit sets the target burning.</p>')
e2=eff(d,'Hearty Honeycomb',[chg('system.abilities.str.save.roll.mode','1','add'),chg('system.abilities.con.save.roll.mode','1','add')],'hh',duration=mins(1),desc='<p>Advantage on Strength and Constitution saves.</p>')
e3=eff(d,'Spring Sneakers',[chg('system.attributes.movement.walk','10','add')],'ss',duration=mins(1),desc='<p>Speed +10 ft; Opportunity Attacks have Disadvantage against you; once per turn jump 30 ft for 10 ft of movement.</p>')
d['effects']=[e1,e2,e3]; L3=[]
for tag,e in [('dp',e1),('hh',e2),('ss',e3)]:
    i,a=act(d,tag,'heal' if tag=='hh' else 'utility',e['name'],'special','When you take the Attack action (switch at the start of your turn without spending a use)',ccons(),effects=[e['_id']],duration=MIN(1))
    if tag=='hh': a['healing']=heal('max(2, 2 * @abilities.cha.mod)','temphp')
    L3.append((i,a))
setacts(d,L3); D(p,d)
p=S_+'rare-power-up-15.yml'; d=L(p)
r1=eff(d,'Colossus Roar',[chg('system.traits.size','lg','override'),chg('system.bonuses.mwak.damage','1d12[force]','add'),chg('system.bonuses.rwak.damage','1d12[force]','add')],'cr',duration=mins(1))
r2=eff(d,'Fairy Dust',[chg('system.attributes.movement.fly','60','upgrade'),chg('system.attributes.movement.hover','true','override')],'fd',duration=mins(1))
r3=eff(d,'Steel Block',[],'sb',duration=mins(1),desc='<p>You can’t be moved or teleported against your will, and damage you take is reduced by your Charisma modifier (min 1).</p>')
d['effects']=[r1,r2,r3]
setacts(d,[act(d,t,'utility',e['name'],'special',"Instead of a Hero's Power-Up option",ccons(),effects=[e['_id']],duration=MIN(1)) for t,e in [('cr',r1),('fd',r2),('sb',r3)]]+[act(d,'sbr','utility','Steel Block: Reduce Damage','special','You take damage while Steel Block is active',roll=roll(CHA,'Damage Reduced'))]); D(p,d)
p=S_+'spinning-shell-7.yml'; d=L(p); setuses(d,3,'turnStart'); a=first(d); a['name']='Spinning Shell'
a['activation']=spc('You or an ally in your Zone of Safety is hit by an attack roll'); a['activation']['type']='reaction'
a['consumption']['targets']=iu(); a['consumption']['scaling']={'allowed':True,'max':'3'}; a['roll']=roll('@scaling','AC Bonus (tokens spent)'); D(p,d)
p=S_+'super-prism-20.yml'; d=L(p); sp=eff(d,'Super Prism',[chg('system.traits.dr.value',t,'add') for t in DT],'sp',duration=mins(1),desc='<p>Resistance to all damage. Ignore Difficult Terrain; spend 10 ft of movement to end Grappled, Paralyzed, Restrained or Stunned. Super Smash when you move within 5 ft of a creature.</p>'); d['effects']=[sp]
sm=first(d); sm['name']='Super Smash'; sm['activation']=spc('You move within 5 feet of a creature (once per creature per turn)'); sm['consumption']['targets']=[]; sm['target']=one()
setacts(d,[act(d,'sp','utility','Super Prism','bonus','',iu(),effects=[sp['_id']],duration=MIN(1)),(sm['_id'],sm)]); D(p,d)
print('round6 enforcer done')
