#!/usr/bin/env python3
"""Loot, shop and credits roll tables (packs/_source/tables) built from the Equipment compendium."""
import os,sys,glob,yaml
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import OUT,stats,write,folder,reset,mkid,MOD
ITEMS=[]
for f in sorted(glob.glob(os.path.join(OUT,'items','**','*.yml'),recursive=True)):
    if f.endswith('_folder.yml') or '/pack-contents/' in f: continue
    d=yaml.safe_load(open(f)); p=((d['system'].get('price') or {}).get('value')) or 0
    if not p: continue
    ITEMS.append({'id':d['_id'],'name':d['name'],'img':d.get('img'),'price':p,'cat':f.split('/items/')[1].split('/')[0],'type':d['type']})
reset('tables')
FL={k:folder('tables',k,n,typ='RollTable',sort=i) for i,(k,n) in enumerate([('loot','Loot by Value'),('shops','Shop Stock'),('credits','Credits by Challenge Rating')])}
def table(fold,name,desc,results,img,formula=None):
    tid=mkid(f'table:{name}')
    res=[]
    for i,r in enumerate(results,1):
        rid=mkid(f'table:{name}:{i}:{r.get("name") or r.get("description")}')
        x={'type':r['type'],'weight':1,'range':[i,i],'drawn':False,'_id':rid,'img':r.get('img') or img,'flags':{},'_stats':stats(),
           'name':r.get('name',''),'description':r.get('description',''),'_key':f'!tables.results!{tid}.{rid}'}
        if r['type']=='document': x['documentUuid']=r['uuid']
        res.append(x)
    doc={'_id':tid,'name':name,'img':img,'description':f'<p>{desc}</p>','results':res,'replacement':True,'displayRoll':True,
         'folder':FL[fold],'formula':formula or f'1d{len(res)}','sort':0}
    write('tables',f'{fold}/{tid}.yml',doc,kind='tables')
def items(pred): return [{'type':'document','name':i['name'],'img':i['img'],'uuid':f'Compendium.{MOD}.items.Item.{i["id"]}'} for i in ITEMS if pred(i)]
TIERS=[('Loot: Cheap (under 100 GN)',0,100),('Loot: Standard (100–999 GN)',100,1000),('Loot: Valuable (1,000–4,999 GN)',1000,5000),('Loot: Premium (5,000+ GN)',5000,10**9)]
for n,lo,hi in TIERS:
    table('loot',n,f'A random Neon Odyssey item worth {n.split("(")[1][:-1]}.',items(lambda i:lo<=i['price']<hi),'icons/containers/chest/chest-reinforced-steel-cherry.webp')
SHOPS=[('Shop: General Gear',lambda i:i['cat']=='gear' and i['type']!='consumable','icons/environment/settlement/market-stall.webp'),
       ('Shop: Weapons',lambda i:i['cat'] in ('weapons','ammunition'),'icons/weapons/guns/gun-pistol-flintlock-metal.webp'),
       ('Shop: Armor & Modules',lambda i:i['cat'] in ('armor','modules'),'icons/equipment/chest/breastplate-banded-steel.webp'),
       ('Shop: Tools & Instruments',lambda i:i['cat']=='tools','icons/tools/hand/hammer-and-nail.webp'),
       ('Shop: Consumables & Explosives',lambda i:i['type']=='consumable','icons/consumables/potions/bottle-round-corked-green.webp')]
for n,pred,img in SHOPS: table('shops',n,f'A random item for a {n[6:]} shop.',items(pred),img)
for n,f in [('Credits: CR 0–4','3d6 * 50'),('Credits: CR 5–10','2d8 * 500'),('Credits: CR 11–16','2d10 * 5000'),('Credits: CR 17+','2d8 * 50000')]:
    table('credits',n,'Galactic Notes carried by one creature of this Challenge Rating.',[{'type':'text','description':f'[[/r {f}]] Galactic Notes'}],'icons/commodities/currency/coins-plain-stack-gold.webp','1d1')
print(len(ITEMS),'items')
