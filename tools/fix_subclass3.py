import sys,os,copy,yaml,glob,re; sys.path.insert(0,'.')
from common import OUT,uuid,stats,write
from autoact import mkid
def L(p): return yaml.safe_load(open(os.path.join(OUT,p)))
def D(p,d): yaml.safe_dump(d,open(os.path.join(OUT,p),'w'),sort_keys=False,allow_unicode=True,width=200)
def chg(k,v,t): return {'key':k,'value':str(v),'priority':None,'type':t,'phase':'initial','_id':mkid(f'fs3:{k}:{v}')}
def eff(d,name,changes,tag,transfer=False,disabled=False,statuses=(),img=None,desc='',duration=None,flags=None):
    eid=mkid(d['_id']+':fs3:'+tag)
    return {'_id':eid,'name':name,'img':img or d.get('img'),'type':'base','system':{'changes':changes},'disabled':disabled,'transfer':transfer,
      'duration':duration or {'value':None,'units':'seconds','expiry':None,'expired':False},'description':desc,'tint':'#ffffff','statuses':list(statuses),'sort':0,'flags':flags or {},
      'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"}
VIS={'level':{'min':None,'max':None},'identifier':'','requireAttunement':False,'requireIdentification':False,'requireMagic':False}
def act(d,tag,typ,name,activation='action',cond='',cons=None,rng=None,target=None,effects=(),**extra):
    i=mkid(d['_id']+':fs3act:'+tag)
    a={'_id':i,'type':typ,'name':name,'img':'','sort':0,'activation':{'type':activation,'value':None,'override':False,'condition':cond},
       'consumption':{'scaling':{'allowed':False,'max':''},'spellSlot':False,'targets':cons or []},'description':{'chatFlavor':''},
       'duration':{'units':'inst','concentration':False,'override':False,'value':'','special':''},
       'effects':[{'_id':e,'riders':{'activity':[],'effect':[],'item':[]}} for e in effects],
       'range':rng or {'units':'self','override':False,'special':''},
       'target':target or {'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'','type':'self'},'override':False,'prompt':False},
       'uses':{'spent':0,'recovery':[],'max':''},'flags':{},'visibility':copy.deepcopy(VIS),'behaviors':[]}
    a.update(extra); return i,a
def uses(n,tgt=''): return [{'type':'itemUses','value':str(n),'target':tgt,'scaling':{}}]
def dpart(n,f,types,custom=None):
    return {'number':n,'denomination':f,'bonus':'','types':list(types),'custom':{'enabled':bool(custom),'formula':custom or ''},'scaling':{'mode':'','number':None,'formula':''}}
def emanation(sz): return {'template':{'contiguous':False,'units':'ft','type':'radius','size':str(sz),'count':'','stationary':False},'affects':{'choice':True,'count':'','type':'creature'},'override':False,'prompt':True}
def one(kind='creature',rng=30): return {'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'1','type':kind},'override':False,'prompt':False}
def ft(n): return {'value':str(n),'units':'ft','special':'','override':False}
def castact(d,tag,name,spell,lvl,cons=None,activation='action',cond='',spuses=None):
    i,a=act(d,tag,'cast',name,activation,cond,cons)
    a['spell']={'uuid':'Compendium.dnd5e.spells24.Item.'+spell,'challenge':{'override':False},'properties':['vocal','somatic'],'spellbook':False,'ability':'','level':lvl}
    a['target']['prompt']=True
    return i,a
def setacts(d,pairs): d['system']['activities']={i:a for i,a in pairs}
F='features/'

# ---------- A. Renamed 2024 features: activity/effect names + class visibility ----------
BASE={'warlock':'cryptist','monk':'disciple','paladin':'enforcer','sorcerer':'esper','wizard':'gridrunner','bard':'icon','barbarian':'juggernaut','cleric':'oracle','druid':'primalist','rogue':'scoundrel','fighter':'soldier','ranger':'tracer'}
REN=[('Flurry of Blows','Ensouled Strikes'),('Patient Defense','Measured Guard'),('Step of the Wind','Flowing Step'),('Focus Point','Essence Point'),('Heightened','Amplified'),
     ('Wild Shape','Primal Channel'),('Cunning Sneak Attack','Dirty Trick'),('Aura of Courage','Fearless Conviction'),('Divine Sense','Vigilance'),('Regain Rage','Regain Surge'),
     ('Sorcery Points','Psi Points'),('Divine Spark','Cosmic Pulse'),('Martial Arts Damage','Combat Tradition Die')]
def ren(s):
    for a,b in REN: s=s.replace(a,b)
    return s
n=0
for p in glob.glob(os.path.join(OUT,'features/**/*.yml'),recursive=True):
    d=yaml.safe_load(open(p)); ch=False
    if not isinstance(d,dict) or 'system' not in d: continue
    for a in (d['system'].get('activities') or {}).values():
        nm=a.get('name') or ''
        if ren(nm)!=nm: a['name']=ren(nm); ch=True
        v=a.get('visibility') or {}
        if v.get('identifier') in BASE: v['identifier']=BASE[v['identifier']]; ch=True
    for e in d.get('effects') or []:
        if ren(e.get('name',''))!=e.get('name',''): e['name']=ren(e['name']); ch=True
        if e.get('name')=='Rage' and 'juggernaut' in p: e['name']='Surge'; ch=True
    if ch: yaml.safe_dump(d,open(p,'w'),sort_keys=False,allow_unicode=True,width=200); n+=1
print('renamed in',n,'features')

# ---------- B. Primeval Cryptist ----------
ct=L(F+'cryptist/primeval/calamity-touched-3.yml'); fold=ct.get('folder')
ELEM=['acid','cold','fire','lightning','thunder']
IMG={'acid':'icons/magic/acid/projectile-faceted-glob.webp','cold':'icons/magic/water/projectile-ice-snowball.webp','fire':'icons/magic/fire/projectile-fireball-orange.webp',
     'lightning':'icons/magic/lightning/bolt-blue.webp','thunder':'icons/magic/sonic/explosion-shock-wave-teal.webp'}
pool=[]
for el in ELEM:
    E=el.capitalize(); d=copy.deepcopy(ct); d['_id']=mkid('primeval:archaic:'+el); d['name']=f'Archaic Element: {E}'; d['img']=IMG[el]
    s=d['system']; s['identifier']=f'archaic-element-{el}'; s['uses']={'max':'','spent':0,'recovery':[]}
    s['description']={'value':f'<p><strong>Archaic Element ({E}).</strong> You have mastered {E} damage. You have Resistance to {E} damage. When you deal damage with a spell or a weapon, you can change the damage type to {E}, and you ignore Resistance to {E} damage.</p>'
        f'<p><em>One with the Cataclysm:</em> if this is the element you chose for Immunity, enable the <strong>{E} Immunity</strong> effect (you can change it when you finish a Long Rest).</p>','chat':''}
    s['activities']={}; s['advancement']={}
    d['effects']=[eff(d,f'Archaic Element: {E} Resistance',[chg('system.traits.dr.value',el,'add')],'res',transfer=True),
                  eff(d,f'{E} Immunity (One with the Cataclysm)',[chg('system.traits.di.value',el,'add')],'imm',transfer=True,disabled=True)]
    write('features',f'cryptist/primeval/archaic-element-{el}.yml',d); pool.append(uuid('features',d['_id']))
pp='classes/cryptist/primeval.yml'; pc=L(pp); cid=mkid('primeval:archaic-choice')
pc['system']['advancement'][cid]={'_id':cid,'type':'ItemChoice','level':3,'title':'Archaic Element','hint':'Choose a damage type to master (a second at level 6, a third at level 10).','icon':None,'classRestriction':'','flags':{},
  'configuration':{'choices':{'3':{'count':1,'replacement':False},'6':{'count':1,'replacement':False},'10':{'count':1,'replacement':False}},'allowDrops':False,'type':'feat','pool':[{'uuid':u} for u in pool],'spell':None,
  'restriction':{'type':'','subtype':'','list':[],'level':'','school':[]},'sorting':'a'},'value':{}}
D(pp,pc)
# Calamity-Touched: Consuming Calamity
s=ct['system']
i,a=act(ct,'consume','heal','Consuming Calamity','reaction','A creature you can see within 30 feet takes damage of your Archaic Element type',uses(1),ft(30),one())
a['healing']={'number':None,'denomination':None,'bonus':'','types':['temphp'],'custom':{'enabled':True,'formula':'0'},'scaling':{'mode':'','number':None,'formula':''}}
a['description']['chatFlavor']='The creature has Resistance to that damage; you gain Temporary Hit Points equal to the damage it takes (enter the amount).'
a['target']['affects']['type']='self'; a['range']={'units':'self','override':False,'special':''}
a['healing']['custom']['formula']=''; a['roll']={'prompt':False,'visible':False,'name':'','formula':''}
setacts(ct,[(i,a)]); D(F+'cryptist/primeval/calamity-touched-3.yml',ct)
# Primordial Fury: free Elemental Wrath
pfp=F+'cryptist/primeval/primordial-fury-6.yml'; pf=L(pfp)
pf['system']['uses']={'max':'1','spent':0,'recovery':[{'period':'lr','type':'recoverAll'}]}
i,a=act(pf,'ew','cast','Elemental Wrath (free)','action','',uses(1))
a['spell']={'uuid':uuid('spells','I55GXJPjj1aqzIIs'),'challenge':{'override':False},'properties':['vocal','somatic'],'spellbook':False,'ability':'','level':None}; a['target']['prompt']=True
setacts(pf,[(i,a)]); D(pfp,pf)
# One with the Cataclysm: Primordial Barrier
op=F+'cryptist/primeval/one-with-the-cataclysm-10.yml'; oc=L(op)
i,a=act(oc,'barrier','utility','Primordial Barrier','reaction','You or an ally within 10 feet is targeted by an attack roll',uses(1),None,emanation(10))
a['duration']={'units':'turn','value':'1','concentration':False,'override':False,'special':'Until the end of your next turn'}
a['description']['chatFlavor']='You and allies in the barrier have Half Cover.'
j,b=act(oc,'barrierdmg','damage','Primordial Barrier Ends (2d8)','special','When the barrier ends',None,None,emanation(10))
b['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(2,8,ELEM)]}
setacts(oc,[(i,a),(j,b)]); D(op,oc)
# Herald of Calamity: Earthquake
hp=F+'cryptist/primeval/herald-of-calamity-14.yml'; hc=L(hp)
hc['system']['uses']={'max':'1','spent':0,'recovery':[{'period':'lr','type':'recoverAll'}]}
i,a=castact(hc,'eq','Earthquake (free)','phbsplEarthquake',8,uses(1))
j,b=act(hc,'fissure','save','Elemental Fissure (3d10)','special','A creature in a fissure fails its save against Earthquake',None,ft(500),one())
b['damage']={'onSave':'half','parts':[dpart(3,10,ELEM)]}; b['save']={'ability':['dex'],'dc':{'calculation':'spellcasting','formula':''}}
b['description']['chatFlavor']='Acid: Poisoned; Cold: Speed -10 ft; Fire: starts burning; Lightning: no Reactions; Thunder: Deafened (until the start of your next turn).'
setacts(hc,[(i,a),(j,b)]); D(hp,hc)

# ---------- C. Symmetric ----------
ESS='feat:channeled-essence'
lp=F+'disciple/symmetric/lifeforce-control-3.yml'; lc=L(lp)
i,a=act(lc,'rv','heal','Redirect Vitality','special','When you spend an Essence Point on a Channeled Essence option (once per turn)',None,ft(30),one())
a['healing']=dpart(None,None,['healing'],'@scale.disciple.die')
j,b=act(lc,'sc','damage','Somber Cull','special','Next creature you hit before the end of your next turn',None,None,one())
b['damage']={'critical':{'allow':True,'bonus':''},'parts':[dpart(None,None,['necrotic'],'@scale.disciple.die')]}
setacts(lc,[(i,a),(j,b)]); D(lp,lc)
fp=F+'disciple/symmetric/fear-and-wisdom-6.yml'; fw=L(fp)
i,a=castact(fw,'sug','Mind Touch: Suggestion (3 Essence)','phbsplSuggestion',2,uses(3,ESS))
j,b=castact(fw,'fear','Inevitable End: Fear (3 Essence)','phbsplFear000000',3,uses(3,ESS))
setacts(fw,[(i,a),(j,b)]); D(fp,fw)
plp=F+'disciple/symmetric/path-of-life-and-death-11.yml'; pl=L(plp)
fly=eff(pl,'Path of Life and Death: Flight',[chg('system.attributes.movement.fly','@attributes.movement.walk','upgrade')],'fly',duration={'value':1,'units':'turns','expiry':'turnStart','expired':False})
i,a=act(pl,'fly','utility','Harmony Flight','special','When you use Flowing Step',None,None,None,[fly['_id']])
j,b=act(pl,'vital','heal','Vital Imparting','special','Move within 5 feet of a creature (Flowing Step with an Essence Point)',None,ft(5),one())
b['healing']=dpart(None,None,['healing'],'@scale.disciple.die')
k,c=act(pl,'somber','damage','Somber Imparting','special','Move within 5 feet of a creature (Flowing Step with an Essence Point)',None,ft(5),one())
c['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(None,None,['necrotic'],'@scale.disciple.die')]}
pl['effects']=[fly]; setacts(pl,[(i,a),(j,b),(k,c)]); D(plp,pl)
owp=F+'disciple/symmetric/one-with-the-harmony-17.yml'; ow=L(owp)
i,a=act(ow,'ls','utility','Leveled Scales (1 Essence)','special','On your turn, no action required',uses(1,ESS))
a['duration']={'units':'minute','value':'1','concentration':False,'override':False,'special':''}
j,b=act(ow,'hr','utility','Harmonic Realignment','reaction','You take Necrotic or Radiant damage, or make a Constitution saving throw')
setacts(ow,[(i,a),(j,b)]); D(owp,ow)
for w in ['harmonic-combat-staff','harmonic-saber']:
    wp=F+f'disciple/symmetric/{w}.yml'; wd=L(wp); wd['system']['uses']={'max':'','spent':0,'recovery':[]}; D(wp,wd)
hbp=F+'disciple/symmetric/harmonys-balance-3.yml'; hb=L(hbp)
for e in hb['effects']:
    e.setdefault('flags',{}).setdefault('neon-odyssey',{})['exclusive']='harmony-balance'
    e['duration']={'value':None,'units':'seconds','expiry':None,'expired':False}
D(hbp,hb)

# ---------- D. Boomdoctor ----------
COMP='feat:experimental-composition'
bsp='classes/machinist/boomdoctor.yml'; bc=L(bsp); rid=mkid('boomdoctor:bomb-radius')
bc['system']['advancement'][rid]={'_id':rid,'type':'ScaleValue','level':0,'title':'Impromptu Bomb Radius','hint':'','icon':None,'classRestriction':'','flags':{},
  'configuration':{'identifier':'radius','type':'distance','distance':{'units':'ft'},'scale':{'3':{'value':10},'9':{'value':20}}},'value':{}}
D(bsp,bc)
bp=F+'machinist/boomdoctor/experimental-composition-3.yml'; bd=L(bp)
for a in bd['system']['activities'].values():
    if a['type']=='save': a['target']['template'].update({'type':'sphere','size':'@scale.boomdoctor.radius'})
D(bp,bd)
rp=F+'machinist/boomdoctor/ray-gun-5.yml'; rg=L(rp)
RAY=[('Sleep','phbsplSleep00000',['unconscious'],'Unconscious (Sleep). Ends if it takes damage or someone uses an action to wake it.'),
     ('Hold Person','phbsplHoldPerson',['paralyzed'],'Paralyzed (Hold Person). Repeats the save at the end of each of its turns.'),
     ('Ray of Enfeeblement','phbsplRayofEnfee',[],'Disadvantage on Strength-based D20 Tests; its Strength-based attacks deal 1d8 less damage.'),
     ('Slow','phbsplSlow000000',[],'Speed halved, -2 AC and Dexterity saves, no Reactions, only an action or a Bonus Action on its turn, max one attack.'),
     ('Bestow Curse','phbsplBestowCurs',[],'Cursed (Bestow Curse): you choose the curse option from the spell.'),
     ('Fear','phbsplFear000000',['frightened'],'Frightened (Fear): drops what it holds and must Dash away from you.')]
DUR={'value':1,'units':'minutes','expiry':None,'expired':False}
effs=[]; pairs=[]
atk=list(rg['system']['activities'].values())[0]; atk['name']='Fire Ray Gun'; atk['_id']=atk['_id']
atk['consumption']={'scaling':{'allowed':False,'max':''},'spellSlot':False,'targets':uses(1,COMP)}
atk['range']=ft(90); atk['target']=one(); atk['activation']={'type':'action','value':None,'override':False,'condition':'Magic action'}
atk['description']={'chatFlavor':'On a hit, use Roll Ray Effect (1d6) or spend a Composition to choose.'}
atk['attack']={'ability':'','bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':'ranged','classification':'spell'}}
pairs.append((atk['_id'],atk))
i,a=act(rg,'roll','utility','Roll Ray Effect (1d6)','special','On a hit')
a['roll']={'formula':'1d6','name':'Ray Gun Effect','prompt':False,'visible':True}
a['description']['chatFlavor']='1 Sleep, 2 Hold Person, 3 Ray of Enfeeblement, 4 Slow, 5 Bestow Curse, 6 Fear.'
pairs.append((i,a))
i,a=act(rg,'choose','utility','Choose Effect (+1 Composition)','special','On a hit, instead of rolling',uses(1,COMP)); pairs.append((i,a))
for k,(nm,sid,st,txt) in enumerate(RAY,1):
    e=eff(rg,f'Ray Gun: {nm}',[],'ray'+str(k),statuses=st,desc=f'<p>{txt} No Concentration; lasts 1 minute. At the start of each of your turns roll 1d6: on a 1 the effect ends.</p>',
          img=f'systems/dnd5e/icons/svg/statuses/{st[0]}.svg' if st else None,duration=DUR)
    effs.append(e)
    i,a=act(rg,'eff'+str(k),'utility',f'{k}: {nm}','special','Ray Gun hit',None,ft(90),one(),[e['_id']])
    a['duration']={'units':'minute','value':'1','concentration':False,'override':False,'special':''}
    pairs.append((i,a))
i,a=act(rg,'end','utility','End Check (1d6, ends on 1)','special','Start of each of your turns')
a['roll']={'formula':'1d6','name':'Ray Gun: does the effect end? (1 = ends)','prompt':False,'visible':True}; pairs.append((i,a))
rg['effects']=effs; setacts(rg,pairs); D(rp,rg)
bip=F+'machinist/boomdoctor/boom-inator-15.yml'; bi=L(bip)
bi['system']['uses']={'max':'1','spent':0,'recovery':[{'period':'lr','type':'recoverAll'}]}
BT=['acid','cold','fire','lightning','piercing','poison','thunder']
i,a=act(bi,'big','save','Big Boom','action','Magic action, or Reaction when you would drop to 0 HP',uses(1),None,emanation(30))
a['damage']={'onSave':'half','parts':[dpart(5,8,BT),dpart(5,8,BT)]}; a['save']={'ability':['dex'],'dc':{'calculation':'spellcasting','formula':''}}
j,b=act(bi,'chaos','utility','Chaos Boom','action','Magic action, or Reaction when you would drop to 0 HP',uses(1),None,emanation(30))
b['description']['chatFlavor']='Pick a Ray Gun spell (Sleep, Hold Person, Ray of Enfeeblement, Slow, Bestow Curse, Fear); each creature in the Emanation is targeted (your spell save DC), no Concentration, 1 minute.'
k,c=act(bi,'cure','heal','Cure-All Boom','action','Magic action, or Reaction when you would drop to 0 HP',uses(1),None,emanation(30))
c['healing']=dpart(5,8,['healing'])
setacts(bi,[(i,a),(j,b),(k,c)]); D(bip,bi)
iip=F+'machinist/boomdoctor/inspired-invention-9.yml'; ii=L(iip)
ii['system']['uses']={'max':'1','spent':0,'recovery':[{'period':'lr','type':'recoverAll'}]}
setacts(ii,[castact(ii,'b'+str(n),f'Boomsday Device: {nm}',sid,lv,uses(1),'action','While holding Chemist’s Supplies') for n,(nm,sid,lv) in enumerate(
    [('Confusion','phbsplConfusion0',4),('Dimension Door','phbsplDimensionD',4),('Greater Invisibility','phbsplGreaterInv',4),('Polymorph','phbsplPolymorph0',4)])])
D(iip,ii)
print('subclass3 fixed')

# Leftover Monk terminology inside Disciple items (descriptions, effect names/descriptions, scale titles)
MONK=[('Martial Arts column of the Monk Features table','Combat Tradition column of the Disciple Features table'),
      ('Martial Arts Die','Combat Tradition Die'),('Monk weapons','Disciple weapons'),('Monk levels','Disciple levels'),
      ('Monk weapon','Disciple weapon'),('Focus Points','Essence Points'),('Focus Point','Essence Point'),
      ('Flurry of Blows','Ensouled Strikes'),('Patient Defense','Measured Guard'),('Step of the Wind','Flowing Step'),
      ("Monk's Focus",'Channeled Essence'),('Martial Arts','Combat Tradition')]
def demonk(s):
    if not isinstance(s,str): return s
    for a,b in MONK: s=s.replace(a,b)
    return s
def walk(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in ('uuid','_id','identifier','srcIdentifier','key','_key','img'): continue
            o[k]=demonk(v) if isinstance(v,str) else walk(v)
    elif isinstance(o,list):
        for i,v in enumerate(o): o[i]=demonk(v) if isinstance(v,str) else walk(v)
    return o
n=0
for p in glob.glob(os.path.join(OUT,'features/disciple/**/*.yml'),recursive=True)+glob.glob(os.path.join(OUT,'classes/disciple/*.yml')):
    d=yaml.safe_load(open(p)); before=yaml.safe_dump(d); walk(d)
    if yaml.safe_dump(d)!=before: yaml.safe_dump(d,open(p,'w'),sort_keys=False,allow_unicode=True,width=200); n+=1
print('demonked',n)

# Formulas copied from 2024 classes still reference the dnd5e class identifier (e.g. @classes.monk.levels)
pat=re.compile(r'@classes\.('+'|'.join(BASE)+r')\.')
n=0
for p in glob.glob(os.path.join(OUT,'**/*.yml'),recursive=True):
    s=open(p).read()
    t=pat.sub(lambda m:'@classes.'+BASE[m.group(1)]+'.',s)
    if t!=s: open(p,'w').write(t); n+=1
print('class refs fixed',n)

# Elemental Wrath: base 2d8 of the chosen element; per-element riders as separate buttons
ewp=os.path.join(OUT,'spells/level-3/elemental-wrath.yml'); ew=L(ewp)
acts=ew['system']['activities']; sv=[a for a in acts.values() if a['type']=='save'][0]
ELEM5=['acid','cold','fire','lightning','thunder']
def dp(n,d,t): return {'number':n,'denomination':d,'bonus':'','types':t,'custom':{'enabled':False,'formula':''},'scaling':{'mode':'','number':None,'formula':''}}
sv['damage']['parts']=[dp(2,8,ELEM5)]; sv['name']='Save (2d8 chosen element)'
for k in [k for k,a in acts.items() if a.get('flags',{}).get('neon-odyssey',{}).get('ewRider')]: del acts[k]
for nm,n,d,t in [('Acid: extra 2d8 Acid (Speed halved)',2,8,'acid'),('Cold: extra 1d8 Cold (Disadvantage on D20 Tests)',1,8,'cold'),('Fire: burning 1d10 Fire',1,10,'fire'),('Thunder: extra 1d8 Thunder (Prone)',1,8,'thunder')]:
    r=copy.deepcopy(sv); r['_id']=mkid('ew:'+t); r['type']='damage'; r.pop('save',None); r['name']=nm
    r['damage']={'critical':{'allow':False,'bonus':''},'parts':[dp(n,d,[t])]}; r['effects']=[]
    r['activation']={'type':'special','value':None,'condition':'Target fails the save','override':False}
    r['consumption']={'scaling':{'allowed':False,'max':''},'spellSlot':False,'targets':[]}
    r.setdefault('flags',{}).setdefault('neon-odyssey',{})['ewRider']=True
    acts[r['_id']]=r
D(ewp,ew)
# Consumption targets that still point at dnd5e class features
TGT={'Compendium.dnd5e.classes24.Item.phbwlkMagicalCun':'feat:cryptic-guile','Compendium.dnd5e.classes24.Item.phbdrdWildShape0':'feat:primal-channel','Compendium.dnd5e.classes24.Item.phbftrSecondWind':'feat:frontline-rally'}
n=0
for p in glob.glob(os.path.join(OUT,'features/**/*.yml'),recursive=True):
    s=open(p).read(); t=s
    for a,b in TGT.items(): t=t.replace('target: '+a,'target: '+b)
    if t!=s: open(p,'w').write(t); n+=1
print('dnd5e targets fixed',n)

# Ray Gun effects: copy mechanical changes from the dnd5e 2024 spells, 1 minute duration
DN=os.path.expanduser('~/work/dnd5e/packs/_source/spells24/')
RSRC={'Sleep':('1st-level/sleep.yml',None),'Hold Person':('2nd-level/hold-person.yml',None),'Ray of Enfeeblement':('2nd-level/ray-of-enfeeblement.yml','Enervated'),
      'Slow':('3rd-level/slow.yml',None),'Fear':('3rd-level/fear.yml',None),'Bestow Curse':('3rd-level/bestow-curse.yml','*')}
rgp=os.path.join(OUT,'features/machinist/boomdoctor/ray-gun-5.yml'); rg=L(rgp)
byname={e['name']:e for e in rg['effects']}
def cp_changes(src,key):
    return [{**{k:c[k] for k in ('key','priority','type','phase')},'value':str(c['value']),'_id':mkid(f'rg:{key}:{c["key"]}:{c["value"]}')} for c in src.get('system',{}).get('changes',[])]
for sp,(f,pick) in RSRC.items():
    srcs=yaml.safe_load(open(DN+f)).get('effects',[])
    base=byname.get('Ray Gun: '+sp)
    if base is None: continue
    base['duration']={'value':60,'units':'seconds','expiry':'turnStart','expired':False} if 'units' in base.get('duration',{}) else {**base.get('duration',{}),'seconds':60}
    if pick=='*':
        act=[a for a in rg['system']['activities'].values() if a['name'].endswith(': Bestow Curse')][0]
        rg['effects']=[e for e in rg['effects'] if not e['name'].startswith('Ray Gun: Bestow Curse')]
        act['effects']=[]
        for s in srcs:
            e=copy.deepcopy(base); e['name']='Ray Gun: Bestow Curse ('+s['name'].replace('Cursed ','')+')'
            e['_id']=mkid('rgbc:'+s['name']); e['_key']=f"!items.effects!{rg['_id']}.{e['_id']}"
            e['statuses']=s.get('statuses',[]); e['system']={'changes':cp_changes(s,s['name'])}
            e['description']=s.get('description') or base.get('description','')
            rg['effects'].append(e); act['effects'].append({'_id':e['_id'],'onSave':False})
        continue
    s=[x for x in srcs if (pick is None or x['name']==pick)][0]
    base['statuses']=s.get('statuses') or base.get('statuses',[]); base['system']={'changes':cp_changes(s,sp)}
D(rgp,rg)
print('ray gun effects',[(e['name'],len(e['system']['changes']),e['statuses'],e['duration']) for e in L(rgp)['effects']][:3])

# Mystic Arcanum: use the Cryptist list and fill pool with list spells of the exact level
DN5=os.path.expanduser('~/work/dnd5e/packs/_source/spells24/')
lvl={}
for f in glob.glob(os.path.join(OUT,'spells/**/*.yml'),recursive=True):
    x=yaml.safe_load(open(f))
    if x and x.get('type')=='spell': lvl['Compendium.neon-odyssey.spells.Item.'+x['_id']]=x['system']['level']
for f in glob.glob(DN5+'**/*.yml',recursive=True):
    x=yaml.safe_load(open(f))
    if x and x.get('type')=='spell': lvl['Compendium.dnd5e.spells24.Item.'+x['_id']]=x['system']['level']
sl=L(os.path.join(OUT,'spell-lists/neon-odyssey-spell-lists.yml'))
cl=[p for p in sl['pages'] if p['system'].get('identifier')=='cryptist'][0]['system']['spells']
mp=os.path.join(OUT,'features/cryptist/class-features/eldritch-revelation-11.yml'); m=L(mp)
for a in m['system']['advancement'].values() if isinstance(m['system']['advancement'],dict) else m['system']['advancement']:
    if a['type']=='ItemChoice' and 'Arcanum' in (a.get('title') or ''):
        c=a['configuration']; L_=int(c['restriction']['level'])
        c['restriction']['list']=['class:cryptist']
        c['pool']=[{'uuid':u} for u in cl if lvl.get(u)==L_]
        print('arcanum',L_,len(c['pool']))
D(mp,m)

# Channeled Essence: replace remote dnd5e action effects with local Neon-named copies
EFS={}
for f in glob.glob(os.path.expanduser('~/work/dnd5e/packs/_source/effects/**/*.yml'),recursive=True):
    x=yaml.safe_load(open(f)); EFS['Compendium.dnd5e.effects.ActiveEffect.'+x['_id']]=x
cep=os.path.join(OUT,'features/disciple/class-features/channeled-essence-2.yml'); ce=L(cep)
made={e['flags']['neon-odyssey']['ceKey']:e['_id'] for e in ce.get('effects',[]) if e.get('flags',{}).get('neon-odyssey',{}).get('ceKey')}
for a in ce['system']['activities'].values():
    base=a['name'].split(' (')[0]; new=[]
    for r in a.get('effects',[]):
        u=r.get('uuid')
        if not u or u not in EFS: new.append(r); continue
        s=EFS[u]; key=base+':'+s['name']
        if key not in made:
            e=copy.deepcopy(s); e['_id']=mkid('ce:'+key); e['_key']=f"!items.effects!{ce['_id']}.{e['_id']}"
            e['name']=f"{base}: {s['name']}"; e['transfer']=False; e['origin']=None
            e['duration']={'value':1,'units':'rounds','expiry':'turnStart','expired':False} if s['name']!='Dashing' else {'value':None,'units':'turn','expiry':'turnEnd','expired':False}
            e.setdefault('flags',{}).setdefault('neon-odyssey',{}).update(ceLocal=True,ceKey=key)
            e.pop('folder',None); e.pop('sort',None); e.pop('_stats',None)
            ce['effects'].append(e); made[key]=e['_id']
        new.append({'_id':made[key],'level':r.get('level',{'min':None,'max':None})})
    a['effects']=new
D(cep,ce); print('ce local effects',sorted(made))

# Elemental Wrath: Lightning rider (Incapacitated until start of next turn)
ew=L(ewp); acts=ew['system']['activities']
for k in [k for k,a in acts.items() if a.get('flags',{}).get('neon-odyssey',{}).get('ewLightning')]: del acts[k]
ew['effects']=[e for e in ew.get('effects',[]) if e['name']!='Elemental Wrath: Lightning']
eid=mkid('ew:lightning-eff')
ew['effects'].append({'_id':eid,'_key':f"!items.effects!{ew['_id']}.{eid}",'name':'Elemental Wrath: Lightning','img':'icons/magic/lightning/bolt-blue.webp',
  'type':'base','system':{'changes':[]},'statuses':['incapacitated'],'disabled':False,'transfer':False,'tint':'#ffffff','origin':None,'showIcon':1,'start':None,
  'duration':{'value':1,'units':'rounds','expiry':'turnStart','expired':False},'description':'<p>Incapacitated until the start of its next turn.</p>','flags':{}})
th=[a for a in acts.values() if a['name'].startswith('Thunder:')][0]
r=copy.deepcopy(th); r['_id']=mkid('ew:lightning'); r['type']='utility'; r.pop('damage',None)
r['name']='Lightning: Incapacitated until start of its next turn'; r['effects']=[{'_id':eid}]
r['roll']={'prompt':False,'visible':False,'name':'','formula':''}
r['sort']=th.get('sort',0)-1; r['flags']={'neon-odyssey':{'ewRider':True,'ewLightning':True}}
acts[r['_id']]=r
pid=mkid('ew:thunder-prone-eff')
ew['effects']=[e for e in ew['effects'] if e['_id']!=pid and e['name'] not in ('Incapacitated','Prone')]
ew['effects'].append({**copy.deepcopy([e for e in ew['effects'] if e['_id']==eid][0]),'_id':pid,'_key':f"!items.effects!{ew['_id']}.{pid}",'name':'Elemental Wrath: Thunder','img':'systems/dnd5e/icons/svg/statuses/prone.svg','statuses':['prone'],'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},'description':'<p>Prone.</p>'})
for a in acts.values(): a['effects']=[]
r['effects']=[{'_id':eid,'onSave':False}]; th['effects']=[{'_id':pid,'onSave':False}]
ew.setdefault('flags',{}).setdefault('neon-odyssey',{})['noAutoCond']=True
D(ewp,ew); print('ew acts',[a['name'] for a in acts.values()])

# Broken image paths (non-existent dnd5e/core icons)
IMGFIX={'systems/dnd5e/icons/svg/action/attack.svg':'systems/dnd5e/icons/svg/activity/attack.svg',
 'systems/dnd5e/icons/svg/action/magic.svg':'systems/dnd5e/icons/svg/activity/cast.svg',
 'systems/dnd5e/icons/svg/action/move.svg':'systems/dnd5e/icons/svg/action/dash.svg',
 'systems/dnd5e/icons/svg/action/disengage.svg':'systems/dnd5e/icons/svg/activity/forward.svg',
 'systems/dnd5e/icons/svg/action/restore-use.svg':'systems/dnd5e/icons/svg/activity/heal.svg',
 'systems/dnd5e/icons/svg/action/push.svg':'systems/dnd5e/icons/svg/activity/utility.svg',
 'systems/dnd5e/icons/svg/action/dodge.svg':'systems/dnd5e/icons/svg/activity/utility.svg',
 'icons/magic/unholy/orb-colllecting-energy-green.webp':'icons/magic/unholy/orb-collecting-energy-green.webp',
 'icons/sundries/books/book-embossed-bound-purple.webp':'icons/sundries/books/book-embossed-bound-brown.webp'}
n=0
for p in glob.glob(os.path.join(OUT,'**/*.yml'),recursive=True):
    s=open(p).read(); t=s
    for a,b in IMGFIX.items(): t=t.replace(a,b)
    if t!=s: open(p,'w').write(t); n+=1
print('img paths fixed',n)

# Harmonic weapons are Disciple weapons: Dex + Combat Tradition die, Necrotic/Radiant option
for fn in ['harmonic-combat-staff.yml','harmonic-saber.yml']:
    hp=os.path.join(OUT,'features/disciple/symmetric',fn); h=L(hp)
    base=list(h['system'].get('damage',{}).get('base',{}).get('types') or [])
    types=base+[t for t in ('necrotic','radiant') if t not in base]
    for a in h['system']['activities'].values():
        if a['type']!='attack': continue
        a['attack']['ability']='dex'
        a['damage']={'critical':{'bonus':''},'includeBase':False,'parts':[{'number':None,'denomination':None,'bonus':'','types':types,
            'custom':{'enabled':True,'formula':'@scale.disciple.die + @mod'},'scaling':{'mode':'','number':None,'formula':''}}]}
    D(hp,h); print('harmonic',fn,types)
