import sys,os,copy,yaml; sys.path.insert(0,'.')
from common import OUT,uuid,stats,write,SRC_HB
from autoact import mkid
def L(p): return yaml.safe_load(open(os.path.join(OUT,p)))
def D(p,d): yaml.safe_dump(d,open(os.path.join(OUT,p),'w'),sort_keys=False,allow_unicode=True,width=200)
def eff(d,name,changes,tag,transfer=True,disabled=False):
    eid=mkid(d['_id']+':'+tag)
    return {'_id':eid,'name':name,'img':d.get('img'),'type':'base','system':{'changes':changes},'disabled':disabled,'transfer':transfer,
      'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},'description':'','tint':'#ffffff','statuses':[],'sort':0,'flags':{},
      'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"}
def chg(k,v,t): return {'key':k,'value':str(v),'priority':None,'type':t,'phase':'initial','_id':mkid(f'fr:{k}:{v}')}
def grant(adv,u):
    its=adv['configuration'].setdefault('items',[])
    if u not in [i['uuid'] for i in its]: its.append({'uuid':u,'optional':False,'sort':0})
def strip_powered(w):
    s=w['system']; s['properties']=[p for p in s['properties'] if p!='powered']
    s['activities']={k:a for k,a in s['activities'].items() if a.get('name') in ('Attack','')}
    return w

# A. Disciple Unarmed Strike
us=yaml.safe_load(open(os.path.expanduser('~/work/dnd5e/packs/_source/classes24/monk/class-features/unarmed-strike.yml')))
us['_id']=mkid('disciple:unarmed-strike'); us['folder']=L('features/disciple/class-features/combat-tradition-1.yml').get('folder')
s=us['system']; s['damage']['base']['custom']['formula']='@scale.disciple.die + @mod'; s['source']=dict(SRC_HB); s['identifier']='unarmed-strike'
s['description']={'value':'<p>Your Unarmed Strike, using your Combat Tradition die and Dexterity (Combat Tradition). Use <strong>Bonus Unarmed Strike</strong> for the Bonus Action strike.</p>','chat':''}
atk=[a for a in s['activities'].values() if a['type']=='attack'][0]
b=copy.deepcopy(atk); b['_id']=mkid('disciple:bonus-unarmed'); b['name']='Bonus Unarmed Strike'; b['activation']['type']='bonus'; s['activities'][b['_id']]=b
for e in us.get('effects',[]): e.pop('_key',None)
write('features','disciple/class-features/unarmed-strike.yml',us)
cp='classes/disciple/disciple.yml'; c=L(cp)
grant([a for a in c['system']['advancement'].values() if a['type']=='ItemGrant' and a.get('level')==1][0],uuid('features',us['_id'])); D(cp,c)

# B. Harmonic Weapon
desc=('<p>As part of a Short or Long Rest, you can create a Combat Staff or two Sabers (your choice) that lack the Powered property. The striking ends or blades of the weapons are made of crystal and channel your balanced energies. You can activate their mastery properties. The weapons vanish if you create more or if you die.</p>'
 '<p>Whenever you can make an Unarmed Strike as part of a Bonus Action, you can make an attack with one of the weapons instead. Whenever you hit with one of the weapons, you can cause it to deal Necrotic or Radiant damage instead of the normal damage type.</p>')
sym='features/disciple/symmetric/harmonys-balance-3.yml'; hb=L(sym)
wpool=[]
for src,nm,qty in [('items/weapons/simple-melee/combat-staff.yml','Harmonic Combat Staff',1),('items/weapons/martial-melee/saber.yml','Harmonic Saber',2)]:
    w=strip_powered(L(src)); w['_id']=mkid('harmonic:'+nm); w['name']=nm; w['folder']=hb.get('folder'); s=w['system']
    s['quantity']=qty; s['proficient']=1; s['identifier']=nm.lower().replace(' ','-')
    for k in ('base','versatile'):
        if s['damage'][k].get('types'): s['damage'][k]['types']=s['damage'][k]['types'][:1]+['necrotic','radiant']
    s['description']={'value':desc,'chat':''}
    a=[a for a in s['activities'].values() if a['type']=='attack'][0]
    b=copy.deepcopy(a); b['_id']=mkid('harmonic-bonus:'+nm); b['name']='Bonus Action Attack'; b['activation']={'type':'bonus','value':None,'override':True,'condition':''}; s['activities'][b['_id']]=b
    for e in w.get('effects',[]) or []: e.pop('_key',None)
    write('features',f"disciple/symmetric/{s['identifier']}.yml",w); wpool.append(uuid('features',w['_id']))
hwp=os.path.join(OUT,'features/disciple/symmetric/harmonic-weapon-3.yml'); old=yaml.safe_load(open(hwp))['_id'] if os.path.exists(hwp) else None
if old==mkid('feat:harmonic-weapon'): old='ATvX6Mt8QAXnAytl'
hw=copy.deepcopy(hb); hw['_id']=old or mkid('feat:harmonic-weapon'); hw['name']='Harmonic Weapon'; hw['effects']=[]; hw['system']['activities']={}
hw['system']['description']={'value':desc,'chat':''}; hw['system']['identifier']='harmonic-weapon'; hw['system']['advancement']={}
write('features','disciple/symmetric/harmonic-weapon-3.yml',hw)
sp='classes/disciple/symmetric.yml'; sc=L(sp); adv=sc['system']['advancement']
g3=[a for a in adv.values() if a['type']=='ItemGrant' and a.get('level')==3][0]
g3['configuration']['items']=[i for i in g3['configuration']['items'] if i['uuid']!=uuid('features',mkid('feat:harmonic-weapon')) or hw['_id']==mkid('feat:harmonic-weapon')]
grant(g3,uuid('features',hw['_id']))
cid=mkid('symmetric:harmonic-choice')
adv[cid]={'_id':cid,'type':'ItemChoice','level':3,'title':'Harmonic Weapon','hint':'Choose a Combat Staff or two Sabers.','icon':None,'classRestriction':'','flags':{},
  'configuration':{'choices':{'3':{'count':1,'replacement':False}},'allowDrops':False,'type':'weapon','pool':[{'uuid':u} for u in wpool],'spell':None,
  'restriction':{'type':'','subtype':'','list':[],'level':'','school':[]},'sorting':'a'},'value':{}}
D(sp,sc)

# C. Harmony's Balance: Vital/Somber buttons
s=hb['system']
def util(nm,eid):
    i=mkid('hb-act:'+nm)
    return i,{'_id':i,'type':'utility','name':nm,'img':'','sort':0,'activation':{'type':'special','value':None,'override':False,'condition':''},
      'consumption':{'scaling':{'allowed':False},'spellSlot':True,'targets':[]},'description':{'chatFlavor':''},'duration':{'units':'perm','concentration':False,'override':False},
      'effects':[{'_id':eid}],'range':{'units':'self','override':False},'target':{'template':{'contiguous':False,'units':'ft'},'affects':{'type':'self','choice':False},'override':False,'prompt':False},
      'uses':{'spent':0,'recovery':[],'max':''},'roll':{'formula':'','name':'','prompt':False,'visible':False},'flags':{},'visibility':{'level':{},'requireAttunement':False,'requireIdentification':False,'requireMagic':False},'behaviors':[]}
def cast(nm,u):
    i=mkid('hb-cast:'+nm)
    return i,{'_id':i,'type':'cast','name':nm,'img':'','sort':0,'spell':{'uuid':u,'challenge':{'override':False},'properties':[],'spellbook':False,'ability':'','level':2},
      'activation':{'type':'action','override':False,'condition':''},'consumption':{'scaling':{'allowed':False},'spellSlot':False,'targets':[{'type':'itemUses','value':'2','target':'feat:channeled-essence','scaling':{}}]},
      'description':{'chatFlavor':''},'duration':{'units':'inst','concentration':False,'override':False},'range':{'units':'self','override':False},
      'target':{'template':{'contiguous':False,'units':'ft'},'affects':{'choice':False},'override':False,'prompt':True},'uses':{'spent':0,'recovery':[],'max':''},'flags':{},
      'visibility':{'level':{},'requireAttunement':False,'requireIdentification':False,'requireMagic':False},'behaviors':[]}
vit=eff(hb,'Vital Balance',[chg('system.traits.dr.value','necrotic','add'),chg('system.abilities.con.save.roll.mode','1','add')],'vital',transfer=False)
som=eff(hb,'Somber Balance',[chg('system.traits.dr.value','radiant','add'),chg('system.attributes.init.roll.mode','1','add')],'somber',transfer=False)
hb['effects']=[vit,som]; s['activities']={}
for i,a in [util('Shift to Vital',vit['_id']),util('Shift to Somber',som['_id']),cast('Lesser Restoration (2 Essence)','Compendium.dnd5e.spells24.Item.phbsplLesserRest'),cast('Hold Person (2 Essence)','Compendium.dnd5e.spells24.Item.phbsplHoldPerson')]: s['activities'][i]=a
D(sym,hb)

# D. Impromptu Bomb
bp='features/machinist/boomdoctor/experimental-composition-3.yml'; bd=L(bp); s=bd['system']
s['uses']={'max':'max(2, 2 * @abilities.int.mod)','spent':0,'recovery':[{'period':'lr','type':'recoverAll'},{'period':'sr','type':'formula','formula':'1'}]}
T=['acid','cold','fire','lightning','piercing','poison','thunder']
part=lambda: {'number':None,'denomination':None,'bonus':'','types':list(T),'custom':{'enabled':True,'formula':'@scale.boomdoctor.bomb'},'scaling':{'mode':'','number':None,'formula':''}}
for a in s['activities'].values():
    if a['type']=='save':
        a['name']='Impromptu Bomb'; a['damage']['parts']=[part(),part()]; a['damage']['onSave']='half'
        a['activation']={'type':'action','value':None,'override':False,'condition':'Magic action'}
        a['range']={'value':'60','units':'ft','special':'','override':False}
        a['target']['template'].update({'type':'sphere','size':'10','units':'ft','count':''})
        a['consumption']['targets']=[{'type':'itemUses','value':'1','target':'','scaling':{}}]
        a['save']={'ability':['dex'],'dc':{'calculation':'spellcasting','formula':''}}
D(bp,bd)
bsp='classes/machinist/boomdoctor.yml'; b=L(bsp); sid=mkid('boomdoctor:bomb-scale')
b['system']['advancement'][sid]={'_id':sid,'type':'ScaleValue','level':0,'title':'Impromptu Bomb (per type)','hint':'','icon':None,'classRestriction':'','flags':{},
  'configuration':{'identifier':'bomb','type':'dice','distance':{'units':''},'scale':{'3':{'number':2,'faces':6},'9':{'number':2,'faces':8}}},'value':{}}
D(bsp,b)

# E. Zorbrak Scything Claws weapon
sc_=copy.deepcopy(us); sc_['_id']=mkid('zorbrak:scything-claws-weapon'); sc_['name']='Scything Claws'; sc_['img']='modules/neon-odyssey/icons/species/zorbrak.webp'
sc_['folder']=L('origins/species-traits/zorbrak/scything-claws.yml').get('folder'); s=sc_['system']; s['identifier']='scything-claws'
s['damage']['base']={'number':1,'denomination':8,'bonus':'','types':['slashing'],'custom':{'enabled':False,'formula':''},'scaling':{'number':1},'modifiers':[]}
s['properties']=['fin']; s['description']={'value':'<p>Unarmed Strike (Damage option only) with your second pair of arms: 1d8 Slashing + your ability modifier, Finesse. With Advantage, scores a Critical Hit on a 19 or 20.</p>','chat':''}
s['activities']={k:a for k,a in s['activities'].items() if a['type']=='attack' and not a.get('name')}; sc_['effects']=[]
write('origins','species-traits/zorbrak/scything-claws-weapon.yml',sc_)
zp='origins/species/zorbrak.yml'; z=L(zp)
grant([a for a in z['system']['advancement'].values() if a['type']=='ItemGrant'][0],uuid('origins',sc_['_id'])); D(zp,z)
print('reports fixed')
