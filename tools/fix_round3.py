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
# ================= ROUND 3: SCOUNDREL =================
import glob
S='features/scoundrel/'; C=S+'class-features/'
SL='@classes.scoundrel.levels'; CS='@scale.scoundrel.sneak-attack'; DEXDC={'calculation':'dex','formula':''}
UC='feat:unstable-compounds'
NI='Compendium.neon-odyssey.items.Item.'; NS='Compendium.neon-odyssey.spells.Item.'
def actuse(a,n=1,*per):
    a['uses']={'spent':0,'recovery':rec(*per),'max':str(n)}
    a['consumption']['targets']=[{'type':'activityUses','value':'1','target':'','scaling':{}}]
def grant(tag,lvl,title,uuids):
    i=mkid('r3grant:'+tag); return i,{'_id':i,'type':'ItemGrant','configuration':{'items':[{'uuid':u,'optional':False,'sort':0} for u in uuids],'optional':False,'spell':None},'value':{},'level':lvl,'title':title,'hint':'','icon':None,'classRestriction':'','flags':{}}
def trait(tag,lvl,title,grants,hint=''):
    i=mkid('r3trait:'+tag); return i,{'_id':i,'type':'Trait','level':lvl,'title':title,'hint':hint,'icon':None,'classRestriction':'','flags':{},
      'configuration':{'mode':'default','allowReplacements':False,'grants':grants,'choices':[]},'value':{}}
REN=[('Sneak Attack','Cheap Shot'),('Cunning Strike','Dirty Trick'),('Devious Strikes','Dirty Deeds'),("Thieves' Cant","Smuggler's Slang"),('Thieves\u2019 Cant','Smuggler\u2019s Slang'),('roguish','underworld')]
def walk(o):
    if isinstance(o,dict): return {k:(v if k in ('identifier','uuid','_key') else walk(v)) for k,v in o.items()}
    if isinstance(o,list): return [walk(x) for x in o]
    if isinstance(o,str):
        for a,b in REN: o=o.replace(a,b)
    return o
# ---- base class: terminology
p='classes/scoundrel/scoundrel.yml'; d=walk(L(p))
for a in d['system']['advancement'].values():
    if a.get('type')=='Trait' and 'languages:exotic:cant' in a['configuration'].get('grants',[]):
        a['configuration']['grants']=['languages:neonOdyssey:smugglersslang']
        a['hint']='Your time in the galaxy\u2019s underworld has allowed you to pick up useful languages. You know Smuggler\u2019s Slang and one other language of your choice.'
D(p,d)
for f in glob.glob(os.path.join(OUT,S+'**/*.yml'),recursive=True):
    p=os.path.relpath(f,OUT); d=L(p)
    if 'system' not in d: continue
    D(p,walk(d))
p=C+'cheap-shot-1.yml'; d=L(p); noacteff(d,{'Incapacitated'}); next(iter(d['system']['activities'].values()))['name']='Cheap Shot'; D(p,d)
for f,old,new in [('zero-in-3','Steady Aim','Zero In'),('lucky-break-5','Uncanny Dodge','Lucky Break'),('fortune-favored-20','Stroke of Luck','Defy the Odds')]:
    p=C+f+'.yml'; d=L(p)
    for a in d['system']['activities'].values():
        if a['name']==old: a['name']=new
    D(p,d)
p=C+'fortune-favored-20.yml'; d=L(p); setuses(d,1,'sr','lr'); D(p,d)
p=C+'upper-hand-7.yml'; d=L(p)
for e in d['effects']:
    if e['name']=='Reliable Talent': e['name']='Upper Hand'
D(p,d)
p=C+'dirty-trick-5.yml'; d=L(p)
v=d['system']['description']['value']; v=re.sub(r'\+2 Cheap Shot, Expertise.*?Fortune Favored\s*','',v,flags=re.S); v=v.replace('number of Cheap Shot damage dice','number of Cheap Shot damage dice')
d['system']['description']['value']=v
EN={'RazTM6biKVtNtjEW':'Toxic Payload: Poisoned','La47n2N3VtECtnA9':'Tendon Strike: Prone'}
for e in d['effects']:
    if e['_id'] in EN: e['name']=EN[e['_id']]
noacteff(d,{'Poisoned','Prone'})
AN={'Poison':'Toxic Payload (1d6)','Trip':'Tendon Strike (1d6)','Withdraw':'Quick Getaway (1d6)','Dirty Trick':'Cheap Shot (pay die cost)'}
for a in d['system']['activities'].values():
    a['name']=AN.get(a['name'],a['name'])
    if a['name'].startswith('Quick'): a['description']['chatFlavor']='Move up to half your Speed without provoking Opportunity Attacks.'
D(p,d)
p=C+'dirty-deeds-14.yml'; d=L(p)
EN={'wWFV1p8u9C1TUPg5':'Brain Rattle','C2IGgt4PnRMxZVey':'Blackout: Unconscious','Fb1n6Yk2MlOAckf0':'Blind Spot: Blinded'}
for e in d['effects']:
    if e['_id'] in EN: e['name']=EN[e['_id']]
    if e['_id']=='wWFV1p8u9C1TUPg5': e['description']='<p>On its next turn, it can do only one of the following: move, take an action, or take a Bonus Action.</p>'
noacteff(d,{'Blinded','Unconscious'})
AN={'Daze':'Brain Rattle (2d6)','Knock Out':'Blackout (6d6)','Obscure':'Blind Spot (3d6)'}
for a in d['system']['activities'].values(): a['name']=AN.get(a['name'],a['name'])
D(p,d)
# ---- Chemboss
p=S+'chemboss/chemical-executive-3.yml'; d=L(p)
setacts(d,[act(d,'mix','utility','Quick Mixing','bonus',flavor="Take the Utilize action with Chemist's Supplies or a Toxin Kit.")])
d['system']['advancement']=dict([trait('chemtools',3,'Black Market Tools',['tool:art:alchemist','tool:pois'],"Chemist's Supplies (Alchemist's Supplies) and Toxin Kit (Poisoner's Kit)."),
  grant('chemkit',3,'Black Market Tools',[NI+'yTNGm8Mlp1gckpKP',NI+'BtfnXgHN6AsXeJVt'])]); D(p,d)
p=S+'chemboss/unstable-compounds-3.yml'; d=L(p)
ST=f'(min(1, floor({SL} / 5)) + min(1, floor({SL} / 9)) + min(1, floor({SL} / 13)) + min(1, floor({SL} / 17)))'
d['system']['uses']={'max':f'4 + 2 * {ST}','spent':0,'recovery':[{'period':'lr','type':'recoverAll'},{'period':'sr','type':'formula','formula':f'2 + {ST}'}]}
po=eff(d,'Chem Strike: Poisoned',[],'chempois',statuses=['poisoned'],duration=rnd(1))
stim=eff(d,'Stim Injection',[],'stim',duration=rnd(1),desc='<p>Advantage on the next ability check or attack roll before the end of the Chemboss\u2019s next turn.</p>')
tox=eff(d,'Toxic Delegation',[chg(f'system.bonuses.{k}','-1d4','add') for k in ['abilities.check','abilities.save','mwak.attack','rwak.attack','msak.attack','rsak.attack']],'toxdel',duration=rnd(1),desc='<p>Subtract 1d4 from D20 Tests until the start of the Chemboss\u2019s next turn.</p>')
d['effects']=[po,stim,tox]
i1,a1=act(d,'chem','utility','Chem Strike','special','When you deal Cheap Shot damage within 30 ft (damage becomes Poison)',uses(1),ft(30),one(),[po['_id']])
i2,a2=act(d,'stim','utility','Stim Injection','bonus','',uses(1),ft(30),one(),[stim['_id']])
i3,a3=act(d,'deleg','damage','Toxic Delegation','special',"Forgo one attack; an ally's Reaction attack hits",uses(1),ft(60),one(),[tox['_id']]); dmg(a3,[dpart(None,None,['poison'],CS)])
setacts(d,[(i1,a1),(i2,a2),(i3,a3)]); D(p,d)
p=S+'chemboss/specialized-supply-9.yml'; d=L(p); d['effects']=[]
setacts(d,[act(d,'emstim','utility','Emergency Stim','reaction','A creature you can see within 30 ft drops to 0 HP but isn\u2019t killed',uses(1,UC),ft(30),one(),flavor='The target drops to 1 Hit Point instead.')]); D(p,d)
p=S+'chemboss/nerve-agent-13.yml'; d=L(p); a=next(iter(d['system']['activities'].values()))
a['name']='Berserk Toxin (3d6)'; a['activation']={'type':'special','value':None,'override':False,'condition':'Dirty Trick when you deal Cheap Shot damage'}; a['target']=one()
a['description']['chatFlavor']='On a failed save the target uses its Reaction to attack one of its allies; with no ally in reach or range it takes the 2d6 Psychic damage.'
a.setdefault('damage',{})['onSave']='none'; D(p,d)
p=S+'chemboss/biohazard-broker-17.yml'; d=L(p)
i1,a1=act(d,'lethal','damage','Lethal Dose','special','Start of the Poisoned creature\u2019s turn',target=one()); dmg(a1,[dpart(3,10,['acid','necrotic','poison','psychic'])])
setacts(d,[(i1,a1)]); D(p,d)
# ---- Echo
p=S+'echo/afterimage-3.yml'; d=L(p); setuses(d,'max(1, @abilities.dex.mod)','lr')
d['effects']=[eff(d,'Afterimage',[chg('system.attributes.movement.walk',5,'add'),chg('system.attributes.init.bonus','@prof','add')],'after',transfer=True,desc='<p>Dilated Steps (+5 ft Speed) and Prescient Glimpse (add Proficiency Bonus to Initiative).</p>')]
a=next(iter(d['system']['activities'].values())); a['name']='Try Again'; a['activation']={'type':'special','value':None,'override':False,'condition':'You fail a D20 Test (Cheap Shot -1d6 until end of next turn)'}; D(p,d)
p=S+'echo/time-skip-3.yml'; d=L(p); setuses(d,2,'lr'); a=next(iter(d['system']['activities'].values())); a['name']='Time Skip'; a['range']=ft(30)
a['description']['chatFlavor']='Teleport up to 30 feet to an unoccupied space you can see (no use spent if you return to a space you occupied this turn).'; D(p,d)
p=S+'echo/temporal-rewind-9.yml'; d=L(p)
i1,a1=act(d,'rewind','heal','Temporal Rewind','special','Lucky Break Reaction, or no damage from Agile Escape',[{'type':'hitDice','value':'1','target':'smallest','scaling':{}}])
a1['healing']=heal('1d8 + @abilities.dex.mod'); setacts(d,[(i1,a1)]); D(p,d)
p=S+'echo/chrono-control-13.yml'; d=L(p); setuses(d,1,'lr'); a=next(iter(d['system']['activities'].values())); a['name']='Chrono Control'; a['target']=one()
a['activation']={'type':'special','value':None,'override':False,'condition':'When you deal Cheap Shot damage'}
for e in d['effects']: e['duration']=rnd(1)
D(p,d)
p=S+'echo/diverging-timelines-17.yml'; d=L(p); setuses(d,1,'lr')
ec=eff(d,'Diverging Timelines',[],'echo',duration=mins(1),desc='<p>Your echo is present. Swap with it when you take an action or Bonus Action, or as a Reaction when hit, damaged, or forced to save.</p>')
d['effects']=[ec]
setacts(d,[act(d,'split','utility','Split Timeline','action','Magic action, or when you roll Initiative',uses(1),effects=[ec['_id']],duration=MIN(1)),
  act(d,'swapa','utility','Switch Timelines (Action)','special','When you take an action or Bonus Action'),
  act(d,'swaph','utility','Switch Timelines (Harm)','reaction','Hit by an attack, take damage, or forced to save',flavor='If you are now out of reach or range, the triggering effect fails.')]); D(p,d)
# ---- Operative
p=S+'operative/precision-protocol-3.yml'; d=L(p); next(iter(d['system']['activities'].values()))['name']='Gadget Savvy'
d['system']['advancement']=dict([trait('opprof',3,'Precision Protocol',['weapon:mar:sniperrifle','tool:forg','tool:disg'],"Sniper Rifles, Forger's Kit, Infiltrator's Kit (Disguise Kit)."),
  grant('opkit',3,'Tools of the Trade',[NI+'8yxOAgALwDE6AMmB',NI+'zc9lxJDbkrn3oAq8',NI+'xOz8LRmBRgySduYQ'])]); D(p,d)
p=S+'operative/smooth-operator-3.yml'; d=L(p)
d['system']['uses']={'max':'max(1, @abilities.dex.mod)','spent':0,'recovery':[{'period':'lr','type':'recoverAll'},{'period':'sr','type':'formula','formula':'1'}]}
d['effects']=[eff(d,'Overwatch',[chg('system.attributes.init.bonus','@prof','add')],'overwatch',transfer=True)]
i1,a1=act(d,'grace','utility','Grace Under Pressure','reaction','A creature finds you with Perception, or you fail a Deception/Persuasion check',roll=roll('1d20','New d20')); actuse(a1,1,'sr','lr')
i2,a2=act(d,'oneshot','utility','One Shot, One Kill','special','Hit (add Sap) or miss (Graze) with a weapon or Unarmed Strike',uses(1),target=one())
setacts(d,[(i1,a1),(i2,a2)]); D(p,d)
p=S+'operative/without-a-trace-9.yml'; d=L(p); setuses(d,'max(1, @abilities.dex.mod)','lr'); a=next(iter(d['system']['activities'].values())); a['name']='Without a Trace'
a['activation']={'type':'special','value':None,'override':False,'condition':'End of a turn you dealt Cheap Shot damage (Stealth check as Hide)'}; D(p,d)
p=S+'operative/phantom-strike-13.yml'; d=L(p); a=next(iter(d['system']['activities'].values())); a['name']='Phantom Strike'; a['target']=one()
a['activation']={'type':'special','value':None,'override':False,'condition':'When you use Without a Trace'}
for e in d['effects']: e['duration']=rnd(1)
D(p,d)
p=S+'operative/contingency-plan-17.yml'; d=L(p); setuses(d,1,'lr')
d['system']['advancement']={k:v for k,v in d['system']['advancement'].items() if v.get('type')!='ItemGrant'}
DC='8 + @abilities.dex.mod + @prof'
def cp(tag,name,uuid,lvl,actv,cond=''):
    i,a=cast(d,tag,name,uuid,lvl,actv,cond,uses(1)); a['spell']['properties']=[]; a['spell']['ability']='dex'; a['spell']['challenge']={'attack':None,'save':None,'override':False}; return i,a
setacts(d,[cp('fore','Anticipated Tactics (Foresight)',P24+'phbsplForesight0',9,'special','Start of your turn, until end of next turn'),
  cp('misl','Exit Strategy (Mislead)',P24+'phbsplMislead000',5,'bonus','Requires a Holoprojector'),
  cp('chain','The Best Defense: Chain Lightning',P24+'phbsplChainLight',6,'bonus'),
  cp('cloud','The Best Defense: Cloudkill',P24+'phbsplCloudkill0',5,'bonus','1 minute, no Concentration, stationary'),
  cp('cone','The Best Defense: Cone of Cold',P24+'phbsplConeofCold',5,'bonus'),
  cp('fire','The Best Defense: Fireball',P24+'phbsplFireball00',3,'bonus'),
  cp('storm','The Best Defense: Psychic Storm',NS+'KVted2ztd8uPdBmG',5,'bonus')]); D(p,d)
# ---- Quickdraw
p=S+'quickdraw/deadeye-3.yml'; d=L(p); setuses(d,'max(1, @abilities.dex.mod)','lr')
d['effects']=[eff(d,'One Eye Open',[chg('flags.dnd5e.initiativeAdv','true','override')],'oeo',transfer=True)]
i1,a1=act(d,'bull','utility','Bullseye','special','You roll an 18 or 19 on an attack roll (make it a Critical Hit)',uses(1))
i2,a2=act(d,'shoot','utility','Shoot First','reaction','When you roll Initiative and can see an enemy',flavor='Make one attack with a Ranged weapon that lacks Heavy and Two-Handed; Advantage if your Initiative is higher than the target\u2019s.'); actuse(a2,1,'sr','lr')
setacts(d,[(i1,a1),(i2,a2)]); D(p,d)
p=S+'quickdraw/fast-hands-3.yml'; d=L(p); next(iter(d['system']['activities'].values()))['name']='Now You See It'; D(p,d)
p=S+'quickdraw/trick-shot-9.yml'; d=L(p); a=next(iter(d['system']['activities'].values())); a['name']='Drop It (2d6)'; a['target']=one()
a['activation']={'type':'special','value':None,'override':False,'condition':'Dirty Trick when you deal Cheap Shot damage with a Ranged weapon'}
i2,a2=act(d,'fan','damage','Fan the Hammer (1d6)','special','Dirty Trick: second creature within 30 ft of the first',rng=ft(30),target=one())
dmg(a2,[dpart(None,None,['acid','bludgeoning','cold','fire','force','lightning','necrotic','piercing','poison','psychic','radiant','slashing','thunder'],f'(ceil({CS}.number / 2))d6')])
setacts(d,[(a['_id'],a),(i2,a2)]); D(p,d)
p=S+'quickdraw/heads-down-13.yml'; d=L(p); setuses(d,'max(1, @abilities.dex.mod)','lr')
hd=eff(d,'Heads Down',[],'hd',duration=rnd(1),desc='<p>Disadvantage on attack rolls and ability checks until the start of the Quickdraw\u2019s next turn.</p>'); d['effects']=[hd]
a=next(iter(d['system']['activities'].values())); a['name']='Heads Down'; a['target']=one(); a['effects']=[RID(hd)]
a['activation']={'type':'special','value':None,'override':False,'condition':'When you hit a creature with an attack roll'}; D(p,d)
p=S+'quickdraw/gunslinging-legend-17.yml'; d=L(p)
i1,a1=act(d,'deadshot','damage','Deadshot (half Cheap Shot)','special','Extra attack after dropping a creature to 0 HP with a Ranged weapon hits',target=one())
dmg(a1,[dpart(None,None,['acid','bludgeoning','cold','fire','force','lightning','necrotic','piercing','poison','psychic','radiant','slashing','thunder'],f'floor(({CS}) / 2)')])
setacts(d,[(i1,a1),act(d,'cover','utility','Run for Cover','special','When you use Lucky Break',flavor='Move up to half your Speed without provoking Opportunity Attacks.')]); D(p,d)
# sniper rifle base item for proficiency
p='items/weapons/martial-ranged/sniper-rifle.yml'; d=L(p); d['system']['type']['baseItem']='sniperrifle'; D(p,d)
print('round3 scoundrel done')
