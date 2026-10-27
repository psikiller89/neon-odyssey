import sys,yaml,glob,os,re,copy; sys.path.insert(0,'.')
from common import OUT, stats
from autoact import mkid
F=os.path.join(OUT,'features','machinist'); C=os.path.join(OUT,'classes','machinist','machinist.yml')
def dump(d,p): yaml.safe_dump(d,open(p,'w'),sort_keys=False,allow_unicode=True,width=200)
def chg(key,val,typ='add'): return {'key':key,'value':str(val),'priority':None,'type':typ,'phase':'initial','_id':mkid(f'chg:{key}:{val}:{typ}')}
# --- Spark of Innovation: per-level grants on the class
SPARK=[(5,3,['phbProtectionFro','phbsplStinkingCl']),(7,4,['phbsplArcaneEye0','phbsplFabricate0']),(9,5,['phbsplAnimateObj','phbsplCreation00']),
       (11,6,['phbsplContingenc','phbsplDisintegra']),(13,7,['phbsplForcecage0','phbsplSymbol0000']),(15,8,['phbsplIncendiary','phbsplPowerWordS'])]
sp=os.path.join(F,'class-features','spark-of-innovation-3.yml'); s=yaml.safe_load(open(sp)); s['system']['advancement']={}; dump(s,sp)
c=yaml.safe_load(open(C)); adv=c['system']['advancement']
for k in [k for k,a in adv.items() if a['type']=='ItemGrant' and (a.get('title') or '').startswith('Spark of Innovation')]: del adv[k]
for lvl,sl,ids in SPARK:
    aid=mkid(f'spark:{lvl}')
    adv[aid]={'_id':aid,'type':'ItemGrant','configuration':{'items':[{'uuid':f'Compendium.dnd5e.spells24.Item.{i}','optional':False,'sort':0} for i in ids],'optional':False,
      'spell':{'ability':[],'uses':{'max':'1','per':'lr','requireSlot':False},'method':'innate','prepared':0}},'value':{},'level':lvl,
      'title':f'Spark of Innovation (level {sl} spells)','hint':'Cast one of these with Spark of Innovation without a spell slot; Spark recharges on a Long Rest.'}
# --- Hypertech Schematics choice: start at 2, swap one per later level
for a in adv.values():
    if a['type']=='ItemChoice' and a.get('title')=='Hypertech Schematics':
        ch=a['configuration']['choices']; ch.pop('1',None)
        for L in range(2,21): ch.setdefault(str(L),{'count':None,'replacement':True}); ch[str(L)]['replacement']=L>2
        a['hint']='Choose schematics you qualify for. Each schematic has a "Apply Schematic" button that enchants a piece of gear.'
dump(c,C)
# --- Schematics: enchant activities
SPECIAL={'Weapon Upgrade':[(None,None,[chg('system.magicalBonus',1,'override')])],
         'Shield Upgrade':[(None,None,[chg('system.armor.magicalBonus',1,'override')])],
         'Armor Upgrade':[(None,13,[chg('system.armor.magicalBonus',1,'override')]),(14,None,[chg('system.armor.magicalBonus',2,'override')])]}
n=0
for f in glob.glob(os.path.join(F,'hypertech-schematics','*.yml')):
    if f.endswith('_folder.yml'): continue
    d=yaml.safe_load(open(f)); sy=d['system']; html=sy['description']['value']; txt=re.sub('<[^>]+>',' ',html)
    gear=(re.search(r'Gear:\s*([^\n]*?)\s{2,}',txt) or re.search(r'Gear:\s*(.*)',txt)).group(1).lower()
    wpn='weapon' in gear; arm=('armor' in gear or 'shield' in gear)
    rtype='weapon' if wpn and not arm else ('equipment' if arm and not wpn and not any(w in gear for w in('device','hat','helmet','jewelry','belt','boots','focus','tools','datapad'))  else '')
    effs=[]; refs=[]
    for i,(mn,mx,extra) in enumerate(SPECIAL.get(d['name'],[(None,None,[])])):
        eid=mkid(d['_id']+f':ench:{i}')
        effs.append({'_id':eid,'name':d['name'],'img':d['img'],'type':'enchantment','system':{'changes':[chg('name',f", {d['name']}"),chg('system.properties','mgc')]+extra,'magical':True},
          'disabled':True,'transfer':False,'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},'description':html,'tint':'#ffffff','statuses':[],'sort':0,'flags':{},
          'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"})
        refs.append({'_id':eid,'uuid':None,'level':{'min':mn,'max':mx},'riders':{'activity':[],'effect':[],'item':[]}})
    d['effects']=[e for e in (d.get('effects') or []) if e.get('type')!='enchantment']+effs
    aid=mkid(d['_id']+':enchant')
    sy.setdefault('activities',{})[aid]={'_id':aid,'type':'enchant','name':'Apply Schematic','img':'','activation':{'type':'special','value':None,'override':False,'condition':'When you finish a Short or Long Rest'},
      'consumption':{'scaling':{'allowed':False,'max':''},'spellSlot':True,'targets':[]},'description':{'chatFlavor':''},'duration':{'units':'perm','concentration':False,'override':False},
      'effects':refs,'range':{'override':False,'units':'touch','special':''},'target':{'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'1','type':'object','special':''},'override':False,'prompt':False},
      'uses':{'spent':0,'recovery':[],'max':''},'sort':0,'enchant':{'self':False},'restrictions':{'allowMagical':True,'categories':[],'properties':[],'type':rtype},
      'visibility':{'level':{'min':None,'max':None},'identifier':'machinist','requireAttunement':False,'requireIdentification':False,'requireMagic':False}}
    dump(d,f); n+=1
print('schematics enchanted',n)
