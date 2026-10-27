import sys, re, json, glob, os, yaml, html as H; sys.path.insert(0,'.')
from common import *
from autoact import build_activity, uses_of, mkid
from outline import Item
L=json.load(open('lines.json')); ET=json.load(open('eqtables.json'))
SRDI={}
for f in glob.glob(os.path.expanduser('~/work/dnd5e/packs/_source/equipment24/**/*.yml'),recursive=True):
    d=yaml.safe_load(open(f))
    if d and d.get('system') and d.get('img'): SRDI[d['system'].get('identifier') or ident(d['name'])]=d
ABL={'strength':'str','dexterity':'dex','constitution':'con','intelligence':'int','wisdom':'wis','charisma':'cha'}
PROP={'finesse':'fin','light':'lgt','heavy':'hvy','two-handed':'two','two handed':'two','versatile':'ver','thrown':'thr','reach':'rch','ammunition':'amm','loading':'lod',
      'powered':'powered','burst':'burst','braced':'braced','close quarters':'closeQuarters','reload':'reload','scatter':'scatter','pummel':'pummel'}
MASTERY={'cleave','graze','nick','push','sap','slow','topple','vex'}
ALIAS={'Grapnel':'grappling-hook','Flashlight':'lantern-hooded','Handcuffs':'manacles','Lighter':'tinderbox','Steel Chain':'chain','Spade':'shovel','Pry Bar':'crowbar','Sleeping Bag':'bedroll','Shelter Tent':'tent','Magnifying Lens':'magnifying-glass','Healing Stim':'potion-of-healing','Antidote':'antitoxin','Acid Vial':'acid','Rucksack':'backpack','Canteen':'waterskin','Ration Pouch':'rations','Mesh Net':'net','Steel Bearings':'ball-bearings','Synth Line':'rope','Cord':'string','Climbing Gear':'climbers-kit','Thermal Blanket':'blanket','Bottle':'bottle-glass','Vial, Glass':'vial','Footlocker':'chest','Bag':'sack','Spring Trap':'hunting-trap','Fuel Oil':'oil','Stationery':'paper','Omni Pen':'ink-pen','Fragrance':'perfume','Spell Chip':'spell-scroll','Toxin, Simple':'basic-poison','Med Pack':'healers-kit','Pharma Kit':'herbalism-kit','Toxin Kit':'poisoners-kit','Bypass Tools':'thieves-tools','Forger’s Kit':'forgery-kit','Infiltrator’s Kit':'disguise-kit','Disguise':'costume','Navigation Tools':'navigators-tools','Game Set':'dice-set','Musician’s Instrument':'lute','Artist’s Supplies':'painters-supplies','Brewing Supplies':'brewers-supplies','Chef’s Utensils':'cooks-utensils','Chemist’s Supplies':'alchemists-supplies','Construction Tools':'masons-tools','Electronics Tools':'tinkers-tools','Engineer’s Tools':'tinkers-tools','Jewelry Tools':'jewelers-tools','Mechanic’s Tools':'smiths-tools','Polymer-Molding Tools':'glassblowers-tools','Surveying Tools':'cartographers-tools','Textile Tools':'weavers-tools','Collapsible Pole':'pole','Folding Ladder':'ladder','Hauling Pulley':'block-and-tackle','Clothes, Designer':'fine-clothes','Clothes, Streetwear':'travelers-clothes','Trench Coat':'travelers-clothes','Storage Drum':'barrel','Utility Jug':'jug','Briefcase':'case-map-or-scroll','Belt Pack':'pouch','Component Pack':'component-pouch','Hypertech Component Pack':'component-pouch','Grav Spikes':'iron-spikes','Camo Netting':'net','Nav Chart':'map','Gas Canister':'flask','Thermasene':'alchemists-fire'}
WIMG=[('Axe','battleaxe'),('Hatchet','handaxe'),('Sword','longsword'),('Saber','scimitar'),('Blade','shortsword'),('Hammer','warhammer'),('Maul','maul'),('Knife','dagger'),('Whip','whip'),('Flail','flail'),('Spear','spear'),('Pike','pike'),('Glaive','glaive'),('Lance','lance'),('Staff','quarterstaff'),('Baton','club'),('Cudgel','greatclub'),('Sap','mace'),('Claw','sickle'),('Fist','unarmed-strike'),('Knuckles','unarmed-strike')]
def srd_img(key,default):
    d=SRDI.get(key); return d['img'] if d else default
def money(s):
    m=re.search(r'\$\s*([\d,]+)',s or '')
    if not m: return 0
    v=m.group(1)
    if re.fullmatch(r'\d,\d\d',v) or re.fullmatch(r'\d,\d\d\d,\d\d',v): v+='0'
    return int(v.replace(',',''))
def weight(s):
    s=(s or '').replace('lb.','').strip()
    if s in('','—','Varies'): return 0
    tot=0
    for part in s.split():
        if '/' in part: a,b=part.split('/'); tot+=int(a)/int(b)
        else:
            try: tot+=float(part)
            except: pass
    return round(tot,3)
def phys(price,wt):
    return {'quantity':1,'weight':{'value':wt,'units':'lb'},'price':{'value':price,'denomination':'gn'},'rarity':'','attunement':'','identified':True,'unidentified':{'description':''},'container':None,'equipped':False,'attuned':False}
def act(typ,seed,name,actv='action',**extra):
    a={'_id':mkid(seed),'type':typ,'name':name,'activation':{'type':actv,'value':None,'condition':'','override':False},'consumption':{'targets':[],'scaling':{'allowed':False,'max':''},'spellSlot':True},
       'description':{'chatFlavor':''},'duration':{'units':'inst','concentration':False,'override':False},'effects':[],'range':{'override':False},'target':{'override':False,'prompt':True,'template':{'contiguous':False,'units':'ft'},'affects':{'choice':False}},'uses':{'spent':0,'recovery':[],'max':''},'sort':0}
    a.update(extra); return a
def dmgpart(n,d,types,bonus=''):
    return {'number':n,'denomination':d,'bonus':bonus,'types':types,'custom':{'enabled':False,'formula':''},'scaling':{'mode':'','number':None,'formula':''}}
# ---------- descriptions from text ----------
def parse_desc():
    lines=[l for l in L['handbook'] if 148<=l['p']<=162]
    sec=None; items=[]; cur=None; tab=False; pending=None
    for ln in lines:
        k=ln.get('k'); t=ln.get('text','').strip()
        if k=='TAB': tab=True; continue
        if k=='H_SECTION':
            if t=='NEW WEAPON PROPERTIES': sec='props'
            elif t.startswith('NON-LETHAL'): sec=None
            elif t=='WEAPON MODULES': sec='wmod'
            elif t=='ARMOR MODULES': sec='amod'
            elif t in('CRAFTER’S TOOLS','OTHER TOOLS'): sec='tools'
            cur=None; continue
        if k=='H_SUBCLASSES':
            if t=='TOOLS': sec='tools'
            elif t=='OUTRUNNING GEAR': sec='gear'
            cur=None; continue
        if k in('STAT','SIDEBAR','TABLE','SIDEHEAD'): continue
        if k=='H_FEATURE' and sec:
            if pending: t=pending+' '+t; pending=None
            if t.count('(')>t.count(')'): pending=t; continue
            cur={'sec':sec,'head':t,'meta':{},'body':Item(t)}; items.append(cur); tab=False; continue
        if cur is None: continue
        if k=='SPELLMETA':
            m=re.match(r'^(Ability|Weight|Utilize|Craft|Variants):\s*(.*)$',t)
            if m: cur['meta'][m.group(1)]=m.group(2); cur['_l']=m.group(1)
            elif cur.get('_l'): cur['meta'][cur['_l']]+=' '+t
            continue
        if k in('BODY','META','OTHER'): cur['body'].add(ln,tab); tab=False
    return items
def table_html(key):
    t=ET.get(key)
    if not t: return ''
    hdr=t['header'] or []
    rows=''.join('<tr>'+''.join(f'<td>{H.escape(c)}</td>' for c in r)+'</tr>' for r in t['rows'] if any(r))
    return f'<table><tbody>{rows}</tbody></table>'
VARIANT_TABLES={'Computer':'156.0','Cosmic Symbol':'156.1','Explosives':'157.0','False ID':'157.1','Media Device':'159.0','Occult Focus':'159.1','Primal Focus':'160.0','Ammunition':'155.0'}
def main():
    reset('items')
    F={k:folder('items',ident(k),k,sort=i) for i,k in enumerate(['Weapons','Armor','Weapon & Armor Modules','Tools','Outrunning Gear','Ammunition'])}
    Fw={k:folder('items',f'weapons/{ident(k)}',k,parent=F['Weapons'],sort=i) for i,k in enumerate(['Simple Melee','Simple Ranged','Martial Melee','Martial Ranged'])}
    desc=parse_desc()
    props={d['head']:d['body'].html() for d in desc if d['sec']=='props'}
    count={}
    # ---- weapons
    groups=[('149.0','martialM','Martial Melee'),('149.1','martialR','Martial Ranged')]
    simple=ET['150.0']['rows']; cur='simpleM'
    rows=[]
    for k,typ,fn in groups: rows+= [(r,typ,fn) for r in ET[k]['rows']]
    for r in simple:
        if r[0].startswith('►Simple Ranged'): cur='simpleR'; continue
        if r[0].startswith('►'): continue
        rows.append((r,cur,'Simple Melee' if cur=='simpleM' else 'Simple Ranged'))
    for r,typ,fn in rows:
        name,dmg,pr,mast,wt,cost=[c.strip() for c in r[:6]]
        m=re.match(r'(\d+)d(\d+)\s+(\w+)',dmg); n,d,dt=int(m.group(1)),int(m.group(2)),m.group(3).lower()
        plist=[p.strip() for p in re.split(r',\s*(?![^()]*\))',pr) if p.strip()]
        P=[]; rng={'value':None,'long':None,'units':'ft','reach':None}; ver=None; powered=None; reload=None; scatter=None
        for p in plist:
            base=re.sub(r'\s*\(.*$','',p).lower()
            if base in PROP: P.append(PROP[base])
            if base=='range' : P.append('thr')
            mr=re.search(r'Range (\d[\d,]*)/(\d[\d,]*)',p) or re.search(r'\((\d+)/(\d+)\)',p)
            if mr: rng['value']=int(mr.group(1).replace(',','')); rng['long']=int(mr.group(2).replace(',',''))
            if base=='versatile': mv=re.search(r'(\d+)d(\d+)',p); ver=(int(mv.group(1)),int(mv.group(2)))
            if base=='powered':
                mp=re.findall(r'(\d+)d(\d+)',p); mt=re.search(r'\d+d\d+\s+(\w+)',p)
                powered={'one':tuple(map(int,mp[0])),'two':tuple(map(int,mp[1])) if len(mp)>1 else None,'type':(mt.group(1).lower() if mt else dt)}
            if base=='reload': mr2=re.search(r'(\d+)',p); reload=int(mr2.group(1))
            if base=='scatter': ms=re.search(r'(\d+)',p); scatter=int(ms.group(1))
        P=list(dict.fromkeys(P))
        ranged=typ.endswith('R')
        _id=mkid('weapon:'+name)
        acts={}
        base_atk=act('attack',_id+':atk','Attack',attack={'ability':'','bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':'ranged' if ranged else 'melee','classification':'weapon'}},damage={'critical':{'bonus':''},'includeBase':True,'parts':[]})
        if reload: base_atk['consumption']['targets']=[{'type':'itemUses','value':'1','target':'','scaling':{}}]
        acts[base_atk['_id']]=base_atk
        uses={'max':'','spent':0,'recovery':[]}
        if 'thr' in P and not ranged:
            ta=act('attack',_id+':thr','Throw',attack={'ability':'','bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':'ranged','classification':'weapon'}},damage={'critical':{'bonus':''},'includeBase':True,'parts':[]}); acts[ta['_id']]=ta
        if powered:
            uses={'max':'25','spent':0,'recovery':[]}
            for hand,die in (('', powered['one']),(' (Two-Handed)',powered['two'])):
                if not die: continue
                pa=act('attack',_id+':pow'+hand,'Powered Attack'+hand,attack={'ability':'','bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':'melee','classification':'weapon'}},
                    damage={'critical':{'bonus':''},'includeBase':False,'parts':[dmgpart(die[0],die[1],[powered['type']],'@mod')]})
                pa['consumption']['targets']=[{'type':'itemUses','value':'1','target':'','scaling':{}}]; acts[pa['_id']]=pa
            rc=act('utility',_id+':cell','Replace Power Cell','bonus'); rc['consumption']['targets']=[{'type':'itemUses','value':'-25','target':'','scaling':{}}]; acts[rc['_id']]=rc
        if reload:
            uses={'max':str(reload),'spent':0,'recovery':[]}
            rl=act('utility',_id+':rel','Reload','bonus'); rl['consumption']['targets']=[{'type':'itemUses','value':f'-{reload}','target':'','scaling':{}}]; acts[rl['_id']]=rl
        if 'burst' in P:
            b=act('save',_id+':burst','Burst (Second Target)',save={'ability':['dex'],'dc':{'calculation':'','formula':'15'}},damage={'onSave':'none','parts':[dmgpart(n,d,[dt])]})
            b['consumption']['targets']=[{'type':'itemUses','value':'2','target':'','scaling':{}}] if reload else []
            acts[b['_id']]=b
        if scatter:
            s=act('save',_id+':scat','Scatter',save={'ability':['dex'],'dc':{'calculation':'','formula':'15'}},damage={'onSave':'none','parts':[dmgpart(n,d,[dt])]})
            s['target']={'override':True,'prompt':True,'template':{'type':'cone','size':str(scatter),'units':'ft','contiguous':False,'count':''},'affects':{'type':'creature','choice':False,'count':'','special':''}}
            s['consumption']['targets']=[{'type':'itemUses','value':'2','target':'','scaling':{}}] if reload else []
            acts[s['_id']]=s
        extra=''.join(f'<p><strong>{k}.</strong> {re.sub(r"^<p>|</p>$","",v)}</p>' for k,v in props.items() if PROP.get(k.lower()) in P and PROP.get(k.lower()) in('powered','burst','braced','closeQuarters','reload','scatter','pummel'))
        img=next((srd_img(v,None) for kw,v in WIMG if kw.lower() in name.lower() and srd_img(v,None)),None)
        if ranged: img='icons/weapons/guns/gun-blunderbuss-gold.webp' if re.search(r'Rifle|Cannon|Gun|Shotgun|Scatter|Carbine|Laser$',name) else 'icons/weapons/guns/gun-purple.webp'
        img=img or 'icons/weapons/swords/greatsword-guard.webp'
        sysd={**phys(money(cost),weight(wt)),'description':{'value':f'<p><em>{H.escape(dmg)}; {H.escape(pr)}; Mastery: {mast}</em></p>'+extra,'chat':''},'source':dict(SRC_HB),
            'type':{'value':typ,'baseItem':''},'damage':{'base':dmgpart(n,d,[dt]),'versatile':dmgpart(ver[0],ver[1],[dt]) if ver else dmgpart(None,None,[])},
            'range':rng if (ranged or 'thr' in P) else {'value':None,'long':None,'units':'ft','reach':10 if 'rch' in P else None},'properties':P,'mastery':mast.lower() if mast.lower() in MASTERY else '',
            'uses':uses,'magicalBonus':None,'proficient':None,'armor':{'value':None},'hp':{'value':None,'max':None,'dt':None,'conditions':''},'ammunition':{},'activities':acts,'identifier':ident(name)}
        write('items',f'weapons/{ident(fn)}/{ident(name)}.yml',{'_id':_id,'name':name,'type':'weapon','img':img,'system':sysd,'effects':[],'folder':Fw[fn],'sort':0})
        count['weapon']=count.get('weapon',0)+1
    # ---- armor
    at=None
    for r in ET['152.0']['rows']:
        if r[0].startswith('►'):
            at={'►Light':'light','►Medium':'medium','►Heavy':'heavy','►Shield':'shield'}[r[0].split()[0]]; continue
        name,ac,strn,stealth,wt,cost=[c.strip() for c in r[:6]]
        m=re.search(r'\+?(\d+)',ac); val=int(m.group(1))
        dex=None if at=='light' else (2 if at=='medium' else 0 if at=='heavy' else None)
        ms=re.search(r'(\d+)',strn)
        _id=mkid('armor:'+name)
        img={'light':srd_img('leather-armor','icons/equipment/chest/breastplate-collared-steel.webp'),'medium':srd_img('breastplate','icons/equipment/chest/breastplate-banded-steel.webp'),'heavy':srd_img('plate-armor','icons/equipment/chest/breastplate-rivited-red.webp'),'shield':srd_img('shield','icons/equipment/shield/targe-copper-eye.webp')}[at]
        d0=[x for x in desc if x['sec']=='amod']
        sysd={**phys(money(cost),weight(wt)),'description':{'value':f'<p><em>AC {H.escape(ac)}</em></p>','chat':''},'source':dict(SRC_HB),'type':{'value':at,'baseItem':''},
            'armor':{'value':val,'magicalBonus':None,'dex':dex},'strength':int(ms.group(1)) if ms else None,'properties':['stealthDisadvantage'] if 'Disadvantage' in stealth else [],
            'uses':{'max':'','spent':0,'recovery':[]},'hp':{'value':None,'max':None,'dt':None,'conditions':''},'speed':{'value':None,'conditions':''},'proficient':None,'activities':{},'identifier':ident(name)}
        write('items',f'armor/{ident(name)}.yml',{'_id':_id,'name':name,'type':'equipment','img':img,'system':sysd,'effects':[],'folder':F['Armor'],'sort':0})
        count['armor']=count.get('armor',0)+1
    # ---- gear tables (weight)
    gw={}
    for k in ('154.0','154.1','154.2'):
        for r in ET[k]['rows']:
            if r and r[0]: gw[norm(r[0])]=(r[1] if len(r)>1 else '',r[2] if len(r)>2 else '')
    CONSUM=re.compile(r'Acid Vial|Antidote|Healing Stim|Med Pack|Toxin, Simple|Ration Pouch|Explosives|Spell Chip|Power Cell|Fuel Oil|Gas Canister|Thermasene|Fragrance|Pigment|Repair Parts|Grav Spikes|Steel Bearings')
    CONT=re.compile(r'^(Bag|Belt Pack|Bin|Bottle|Briefcase|Footlocker|Rucksack|Storage Drum|Utility Jug|Vial, Glass|Canteen|Magazine)$|Pack$')
    CLOTH=re.compile(r'Clothes|Trench Coat|Enviro Suit|Disguise|Breath Mask|Night Vision')
    for x in desc:
        if x['sec'] not in('wmod','amod','tools','gear'): continue
        m=re.match(r'^(.*?)\s*\((.*)\)\s*$',x['head']); name=(m.group(1) if m else x['head']).strip(); ct=m.group(2) if m else ''
        if re.search(r'per Month|^Free$',ct) or name in('Squalid',): continue
        if name.startswith('Spell Chip'): name='Spell Chip'
        price=money(ct); text=x['body'].text(); html=x['body'].html()
        wt,c2=gw.get(norm(name),('',''))
        if not price and c2: price=money(c2)
        w=weight(x['meta'].get('Weight') or wt)
        _id=mkid('item:'+name)
        sec=x['sec']
        if sec in('wmod','amod'):
            sysd={**phys(price,w),'description':{'value':html,'chat':''},'source':dict(SRC_HB),'type':{'value':'gear','subtype':''},'properties':[],'identifier':ident(name)}
            write('items',f'modules/{ident(name)}.yml',{'_id':_id,'name':name+(' (Weapon Module)' if sec=='wmod' else ' (Armor Module)'),'type':'loot','img':'icons/svg/upgrade.svg' if False else srd_img('tinkers-tools','icons/tools/smithing/horseshoe-steel-blue.webp'),'system':sysd,'effects':[],'folder':F['Weapon & Armor Modules'],'sort':0})
            count['module']=count.get('module',0)+1; continue
        img=srd_img(ALIAS.get(name,ident(name)),None)
        if sec=='tools':
            meta=x['meta']; ab=[ABL[w2] for w2 in ABL if w2 in meta.get('Ability','').lower()]
            acts={}
            for i,clause in enumerate(re.findall(r'([^,()]+?(?:\([^)]*\))?[^,()]*?)\s*\((?:[A-Za-z]+ )?DC (\d+)\)',meta.get('Utilize',''))):
                nm=clause[0].strip().lstrip('or ').strip(); nm=nm[:1].upper()+nm[1:]
                a=act('check',_id+f':u{i}',nm[:60],check={'ability':ab[0] if ab else '','associated':[],'dc':{'calculation':'','formula':clause[1]}}); acts[a['_id']]=a
            mhtml=''.join(f'<p><strong>{k}:</strong> {H.escape(v)}</p>' for k,v in meta.items())
            tt='art' if 'Tools' in name and name not in('Bypass Tools','Navigation Tools') or 'Supplies' in name or 'Utensils' in name else ('game' if 'Game' in name else 'music' if 'Musician' in name else '')
            sysd={**phys(price,w),'description':{'value':mhtml+html,'chat':''},'source':dict(SRC_HB),'type':{'value':tt,'baseItem':''},'ability':ab[0] if ab else '','chatFlavor':'','proficient':None,'properties':[],'bonus':'','uses':{'max':'','spent':0,'recovery':[]},'activities':acts,'identifier':ident(name)}
            write('items',f'tools/{ident(name)}.yml',{'_id':_id,'name':name,'type':'tool','img':img or 'icons/tools/hand/pickaxe-steel-white.webp','system':sysd,'effects':[],'folder':F['Tools'],'sort':0})
            count['tool']=count.get('tool',0)+1; continue
        vt=next((v for k,v in VARIANT_TABLES.items() if name.startswith(k)),None)
        if vt: html+=table_html(vt)
        if name=='Ammunition':
            for nm,qty,cst,wt2,im in (('Bullets',20,100,1,'icons/weapons/ammunition/bullets-cartridge-shell-gray.webp'),('Shells',10,100,1,'icons/weapons/ammunition/shot-round-lead.webp')):
                sysd={**phys(cst,wt2/qty),'description':{'value':html,'chat':''},'source':dict(SRC_HB),'type':{'value':'ammo','subtype':''},'uses':{'max':'','spent':0,'recovery':[],'autoDestroy':False},'properties':[],'damage':{'base':dmgpart(None,None,[]),'replace':False},'magicalBonus':None,'activities':{},'identifier':ident(nm)}
                sysd['quantity']=qty; sysd['price']={'value':cst,'denomination':'gn'}
                write('items',f'ammunition/{ident(nm)}.yml',{'_id':mkid('item:'+nm),'name':nm,'type':'consumable','img':im,'system':sysd,'effects':[],'folder':F['Ammunition'],'sort':0})
                count['ammo']=count.get('ammo',0)+1
            continue
        dc='dex' if re.search(r'DC 8 plus your Dexterity',text) else 'spellcasting'
        if CONSUM.search(name):
            if name=='Healing Stim' and 'potion-of-healing' in SRDI:
                acts=json.loads(json.dumps(SRDI['potion-of-healing']['system']['activities']))
                for a in acts.values():
                    if isinstance(a.get('description'),dict): a['description']['value']=''
            else:
                a=build_activity(text,_id+':a',dc_ability=dc,consume_uses=True); acts={a['_id']:a} if a else {}
            sub='potion' if name in('Healing Stim','Antidote','Med Pack') else 'poison' if 'Toxin' in name else 'scroll' if name=='Spell Chip' else 'food' if 'Ration' in name else 'trinket'
            sysd={**phys(price,w),'description':{'value':html,'chat':''},'source':dict(SRC_HB),'type':{'value':sub,'subtype':''},'uses':{'max':'1','spent':0,'recovery':[],'autoDestroy':True},'properties':[],'damage':{'base':dmgpart(None,None,[]),'replace':False},'magicalBonus':None,'activities':acts,'identifier':ident(name)}
            typ='consumable'
        elif CONT.search(name):
            sysd={**phys(price,w),'description':{'value':html,'chat':''},'source':dict(SRC_HB),'capacity':{'count':None,'volume':{'units':'cubicFoot'},'weight':{'units':'lb'}},'currency':{},'properties':[],'identifier':ident(name)}
            typ='container'; img=img or 'icons/containers/bags/pack-engraved-leather-tan.webp'
        elif CLOTH.search(name):
            a=build_activity(text,_id+':a',dc_ability=dc,consume_uses=False)
            sysd={**phys(price,w),'description':{'value':html,'chat':''},'source':dict(SRC_HB),'type':{'value':'clothing','baseItem':''},'armor':{'value':None,'dex':None,'magicalBonus':None},'properties':[],'uses':uses_of(text),'activities':{a['_id']:a} if a else {},'identifier':ident(name)}
            typ='equipment'; img=img or 'icons/equipment/back/cloak-hooded-blue.webp'
        else:
            u=uses_of(text); a=build_activity(text,_id+':a',dc_ability=dc,consume_uses=bool(u['max']))
            if a or u['max']:
                sysd={**phys(price,w),'description':{'value':html,'chat':''},'source':dict(SRC_HB),'type':{'value':'trinket','baseItem':''},'armor':{'value':None,'dex':None,'magicalBonus':None},'properties':[],'uses':u,'activities':{a['_id']:a} if a else {},'identifier':ident(name)}
                typ='equipment'
            else:
                sysd={**phys(price,w),'description':{'value':html,'chat':''},'source':dict(SRC_HB),'type':{'value':'gear','subtype':''},'properties':[],'identifier':ident(name)}
                typ='loot'
        img=img or ('icons/tools/navigation/map-chart-tan.webp' if typ=='loot' else 'icons/containers/bags/case-leather-tan.webp')
        write('items',f'gear/{ident(name)}.yml',{'_id':_id,'name':name,'type':typ,'img':img,'system':sysd,'effects':[],'folder':F['Outrunning Gear'],'sort':0})
        count[typ]=count.get(typ,0)+1
    print(count)
if __name__=='__main__': main()
