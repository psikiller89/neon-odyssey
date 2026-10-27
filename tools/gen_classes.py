import sys, re, json, copy, os, glob, yaml; sys.path.insert(0,'.')
from common import *
from autoact import *
from startequip import build as build_se
from renames import BASE, R, COMMON, OPTION_SUBTYPE, srd_for
SRC24=os.path.expanduser('~/work/dnd5e/packs/_source/classes24')
T=json.load(open('tables.json')); SRD_IDS={v['uuid'].split('.')[-1] for v in SRD.values()}; SUBSP=json.load(open('subspells.json'))
SKILL={'acrobatics':'acr','animal handling':'ani','arcana':'arc','athletics':'ath','deception':'dec','history':'his','insight':'ins','intimidation':'itm','investigation':'inv','medicine':'med','nature':'nat','perception':'prc','performance':'prf','persuasion':'per','religion':'rel','sleight of hand':'slt','stealth':'ste','survival':'sur','computers':'cmp','technology':'tec'}
ABL={'strength':'str','dexterity':'dex','constitution':'con','intelligence':'int','wisdom':'wis','charisma':'cha'}
CASTER_ABIL={'Cryptist':'cha','Enforcer':'cha','Esper':'cha','Gridrunner':'int','Icon':'cha','Machinist':'int','Oracle':'wis','Primalist':'wis','Tracer':'wis','Disciple':'wis','Juggernaut':'str','Scoundrel':'dex','Soldier':'str'}
CORE_PAGE={'Cryptist':18,'Disciple':29,'Enforcer':36,'Esper':44,'Gridrunner':53,'Icon':63,'Juggernaut':71,'Machinist':77,'Oracle':88,'Primalist':96,'Scoundrel':108,'Soldier':114,'Tracer':120}
OPTION_FEATURE={'Esoteric Secrets':'Esoteric Secrets','Psi Shaping':'Psi Shaping','Hypertech Schematics':'Hypertech Schematics'}
SKIP=re.compile(r'^(Ability Score Improvement|Epic Boon|\w+ Subclass)$')
def load(p): return yaml.safe_load(open(p))
def advl(a): return list(a.values()) if isinstance(a,dict) else list(a or [])
def advd(l): return {a['_id']:a for a in l}
def core_traits(cls):
    t=T[f'{CORE_PAGE[cls]}.0']['rows']
    return {r[0].replace('\n',' ').strip():(r[1] or '').replace('\n',' ').strip() for r in t if r and r[0]}
def core_html(cls,ct):
    rows=''.join(f'<tr><th scope="row"><p>{k}</p></th><td><p>{v}</p></td></tr>' for k,v in ct.items())
    return f'<h3>Core {cls} Traits</h3><table class="core-class-traits"><tbody>{rows}</tbody></table>'
def trait_adv(seed,title,grants=(),choices=(),restr='primary'):
    return {'_id':mkid(seed),'type':'Trait','configuration':{'mode':'default','allowReplacements':False,'grants':list(grants),'choices':list(choices)},'value':{'chosen':[]},'level':1,'title':title,'hint':'','classRestriction':restr}
def parse_saves(cls,s):
    grants=[];choices=[]
    for w,k in ABL.items():
        if w in s.lower(): grants.append('saves:'+k)
    if 'Primary Ability' in s: choices=[{'count':1,'pool':['saves:int','saves:cha']}]
    return grants,choices
def parse_skills(s):
    m=re.match(r'Choose (?:any )?(\d+)',s); n=int(m.group(1)) if m else 2
    if 'any' in s.lower(): return [{'count':n,'pool':['skills:*']}]
    pool=[ 'skills:'+SKILL[k] for k in SKILL if re.search(r'\b'+k+r'\b',s.lower())]
    return [{'count':n,'pool':pool}]
def hd_of(ct):
    m=re.search(r'D(\d+)',ct.get('Hit Point Die','D8'),re.I); return 'd'+m.group(1)
def dc_abil(cls,text):
    m=re.search(r'DC (?:equals|is) 8 plus your (\w+) modifier',text)
    if m and m.group(1).lower() in ABL: return ABL[m.group(1).lower()]
    return 'spellcasting' if cls in('Cryptist','Enforcer','Esper','Gridrunner','Icon','Machinist','Oracle','Primalist','Tracer') or 'spell save DC' in text else CASTER_ABIL[cls]
def new_feat(name,html,text,*,level,req,seed,cls,src,subtype='',prereq_items=(),repeatable=False,img='icons/svg/upgrade.svg'):
    uses=uses_of(text)
    a=build_activity(text,seed+':a',dc_ability=dc_abil(cls,text),consume_uses=bool(uses['max']))
    _id=mkid(seed)
    adv={}
    if re.search(r'(always have|you know|you learn|gain|can cast)[^.]*\b(spell|cantrip)',text):
        names=[]
        for em in re.findall(r'<em>([^<]+)</em>',html):
            nm=em.strip().rstrip('*')
            u,lv,_,kind=resolve_spell(nm)
            if kind!='phb' and nm not in names and re.search(re.escape(nm)+r'\*?( spell| cantrip|,| and)',text): names.append(nm)
        if names:
            free=bool(re.search(r'without (expending|using) a spell slot',text))
            per='lr' if re.search(r'Long Rest',text) else ('sr' if 'Short Rest' in text else '')
            cfg={'ability':[],'uses':{'max':'1' if free and per else '','per':per if free else '','requireSlot':not free},'method':'spell','prepared':2}
            ga={'_id':mkid(seed+':grant'),'type':'ItemGrant','configuration':{'items':[{'uuid':resolve_spell(n)[0],'optional':False,'sort':0} for n in names],'optional':False,'spell':cfg},'value':{},'level':level or 1,'title':name,'hint':''}
            adv={ga['_id']:ga}
    sysd={'description':{'value':html,'chat':''},'source':dict(src),'uses':uses,'type':{'value':'class','subtype':subtype},
      'prerequisites':{'level':level,'items':list(prereq_items),'repeatable':repeatable},'properties':[],'requirements':req,
      'activities':{a['_id']:a} if a else {},'enchant':{},'identifier':ident(name),'advancement':adv}
    return {'_id':_id,'name':name,'type':'feat','img':img,'system':sysd,'effects':[],'folder':None,'sort':0}
def srd_feat_path(base,stem):
    for p in (f'{SRC24}/{base}/class-features/{stem}.yml',):
        if os.path.exists(p): return p
    return None
def copy_srd(path,name,html,*,base,cid,cls,seed,req,src,option_pool=None):
    d=load(path); old=d['_id']; _id=mkid(seed)
    s=json.dumps(d).replace(f'@scale.{base}.',f'@scale.{cid}.').replace(f'Compendium.dnd5e.classes24.Item.{old}',f'Compendium.{MOD}.features.Item.{_id}')
    s=re.sub(r'Compendium\.dnd-players-handbook\.spells\.Item\.(\w{16})',lambda m: f'Compendium.dnd5e.spells24.Item.{m.group(1)}' if m.group(1) in SRD_IDS else m.group(0),s)
    d=json.loads(s); d['_id']=_id; d['name']=name; d.pop('_key',None); d.pop('_stats',None); d.pop('folder',None)
    sy=d['system']; d.setdefault('flags',{}).setdefault('neon-odyssey',{})['srcIdentifier']=sy.get('identifier') or ''; sy['description']={'value':html,'chat':''}; sy['identifier']=ident(name); sy['requirements']=req; sy['source']=dict(src)
    for e in d.get('effects',[]) or []: e.pop('_stats',None)
    if option_pool is not None:
        for a in advl(sy.get('advancement')):
            if a['type']=='ItemChoice': a['configuration']['pool']=[{'uuid':u} for u in option_pool]; a['configuration'].setdefault('restriction',{})
    if isinstance(sy.get('advancement'),list): sy['advancement']=advd(sy['advancement'])
    for a in (sy.get('activities') or {}).values():
        if isinstance(a.get('description'),dict) and a['description'].get('value'): a['description']['value']=''
    return d
def spells_feature(name,html,text,rows,*,level,req,seed,src,method='spell'):
    f=new_feat(name,html,'',level=level,req=req,seed=seed,cls='Cryptist',src=src,img='icons/sundries/books/book-embossed-bound-purple.webp')
    f['system']['activities']={}
    adv={}
    for r in rows:
        items=[]
        for sp in r['spells']:
            u,_,_,kind=resolve_spell(sp); items.append({'uuid':u,'optional':kind=='phb','sort':0})
        if not items: continue
        a={'_id':mkid(f"{seed}:sp{r['level']}"),'type':'ItemGrant','configuration':{'items':items,'optional':False,'spell':{'ability':[],'uses':{'max':'','per':'','requireSlot':False},'method':method,'prepared':2},'sorting':'m'},'value':{},'level':r['level'],'title':name,'hint':''}
        adv[a['_id']]=a
    f['system']['advancement']=adv
    return f
def grant(seed,level,uuids,title):
    return {'_id':mkid(seed),'type':'ItemGrant','configuration':{'items':[{'uuid':u,'optional':False,'sort':0} for u in uuids],'optional':False,'spell':None},'value':{},'level':level,'title':title,'hint':''}
def subspell_rows(name):
    k=name.replace(' Spells','')
    return SUBSP.get(k,{}).get('rows')
def main():
    reset('classes'); reset('features')
    report=[]
    for ci,(cls,C) in enumerate(O['classes'].items()):
        base=BASE[cls]; cid=ident(cls)
        cfold=folder('classes',cid,cls,sort=ci*100)
        ffold=folder('features',cid,cls,sort=ci*100)
        ff_cls=folder('features',f'{cid}/class-features','Class Features',parent=ffold,sort=1)
        # options
        opt_uuids={}
        for oi,(oname,opts) in enumerate(C['options'].items()):
            of=folder('features',f'{cid}/{ident(oname)}',f'{oname} Options',parent=ffold,sort=10+oi)
            ids={o['name']:mkid(f'opt:{cls}:{o["name"]}') for o in opts}
            opt_uuids[oname]=[uuid('features',ids[o['name']]) for o in opts]
            for o in opts:
                pr=o.get('prereq') or ''
                m=re.search(r'Level (\d+)\+',pr); lvl=int(m.group(1)) if m else None
                items=[uuid('features',ids[n]) for n in ids if n!=o['name'] and n in pr]
                d=new_feat(o['name'],(f'<p><em>{pr}</em></p>' if pr else '')+o['html'],o['text'],level=lvl,req=cls,seed=f'opt:{cls}:{o["name"]}',cls=cls,src=SRC_HB,subtype=OPTION_SUBTYPE.get(oname,''),prereq_items=items,repeatable='more than once' in o['text'])
                d['folder']=of; write('features',f'{cid}/{ident(oname)}/{ident(o["name"])}.yml',d)
        # class features
        feats_by_level={}
        for f in C['features']:
            if SKIP.match(f['name']): continue
            seed=f'feat:{cls}:{f["name"]}:{f["level"]}'
            stem=srd_for(cls,f['name']) if base else None
            path=srd_feat_path(base,stem) if stem else None
            pool=opt_uuids.get(OPTION_FEATURE.get(f['name'],''),None)
            rows=subspell_rows(f['name']) if f['name'].endswith('Spells') else None
            if rows: d=spells_feature(f['name'],f['html'],f['text'],rows,level=f['level'],req=cls,seed=seed,src=SRC_HB,method='pact' if cls=='Cryptist' else 'spell')
            elif path: d=copy_srd(path,f['name'],f['html'],base=base,cid=cid,cls=cls,seed=seed,req=cls,src=SRC_HB,option_pool=pool)
            else: d=new_feat(f['name'],f['html'],f['text'],level=f['level'],req=cls,seed=seed,cls=cls,src=SRC_HB)
            d['folder']=ff_cls; d['system'].setdefault('prerequisites',{})['level']=f['level']
            write('features',f'{cid}/class-features/{ident(f["name"])}-{f["level"]}.yml',d)
            feats_by_level.setdefault(f['level'],[]).append(uuid('features',d['_id']))
            report.append((cls,f['name'],'srd:'+stem if path else ('spells' if rows else 'new'),len(d['system'].get('activities',{}))))
        # class item
        ct=core_traits(cls)
        if base: cd=load(f'{SRC24}/{base}/{base}.yml')
        else: cd=load(f'{SRC24}/wizard/wizard.yml')
        sbase=base or 'wizard'
        adv=[]
        for a in advl(cd['system']['advancement']):
            if a['type']=='ItemGrant': continue
            if a['type']=='Trait':
                g=a['configuration'].get('grants',[])+[x for c in a['configuration'].get('choices',[]) for x in c.get('pool',[])]
                if a.get('level',1)==1 and a.get('classRestriction')!='secondary' and any(x.startswith(('saves:','skills:')) for x in g): continue
                if base is None and any(x.startswith(('weapon:','armor:','tool:','skills:')) for x in g): continue
                if cls in ('Scoundrel','Primalist','Icon','Gridrunner') and any(x.startswith('tool:') for x in g): continue
            if a['type']=='ItemChoice' and cls=='Cryptist' and 'Eldritch' in (a.get('title') or ''):
                a['title']='Esoteric Secrets'; a['configuration']['pool']=[{'uuid':u} for u in opt_uuids['Esoteric Secrets']]
                a['configuration']['restriction']={'type':'class','subtype':'esotericSecret','list':[]}
            if a['type']=='ScaleValue' and a['configuration'].get('identifier')=='invocations-known': a['configuration']['identifier']='secrets-known'; a['title']='Esoteric Secrets Known'
            if base is None and a['type']=='ScaleValue': continue
            adv.append(a)
        g,c=parse_saves(cls,ct.get('Saving Throw Proficiencies',''))
        adv.append(trait_adv(f'tr:sv:{cls}','Saving Throw Proficiencies',g,c))
        adv.append(trait_adv(f'tr:sk:{cls}','Skill Proficiencies',[],parse_skills(ct.get('Skill Proficiencies',''))))
        if base is None:
            adv.append(trait_adv(f'tr:wp:{cls}','Weapon Proficiencies',['weapon:sim']))
            adv.append(trait_adv(f'tr:ar:{cls}','Armor Training',['armor:lgt','armor:med','armor:shl']))
            def sv(idn,title,col):
                sc={}; prev=None
                for i,v in enumerate(col):
                    v=v.strip()
                    if v in('—','') : continue
                    if v!=prev: sc[str(i+1)]={'value':int(v)}; prev=v
                return {'_id':mkid(f'sv:{cls}:{idn}'),'type':'ScaleValue','configuration':{'identifier':idn,'type':'number','distance':{'units':''},'scale':sc},'value':{},'title':title,'hint':''}
            cols=list(zip(*T['78.0']['rows']))
            adv.append(sv('schematics','Hypertech Schematics',cols[2])); adv.append(sv('cantrips-known','Cantrips Known',cols[3])); adv.append(sv('max-prepared','Prepared Spells',cols[4]))
            counts={}; prev=0
            for i,v in enumerate(cols[2]):
                v=0 if v.strip() in('—','') else int(v)
                counts[str(i+1)]={'count':(v-prev) or None,'replacement':i>0}; prev=max(prev,v)
            adv.append({'_id':mkid(f'ic:{cls}'),'type':'ItemChoice','configuration':{'choices':counts,'allowDrops':True,'type':'feat','pool':[{'uuid':u} for u in opt_uuids['Hypertech Schematics']],'restriction':{'type':'class','subtype':'hypertechSchematic','list':[]}},'value':{},'title':'Hypertech Schematics','hint':''})
        for L,us in sorted(feats_by_level.items()):
            adv.append(grant(f'ig:{cls}:{L}',L,us,'Class Features'))
        _id=mkid('class:'+cls)
        s=json.dumps(adv)
        if base: s=s.replace(base.capitalize(),cls).replace(f'@scale.{base}.',f'@scale.{cid}.')
        adv=json.loads(s)
        sy=cd['system']
        sy['description']={'value':core_html(cls,ct)+C['intro']['html'],'chat':''}
        sy['source']=dict(SRC_HB); sy['identifier']=cid; sy['startingEquipment']=build_se(ct.get('Starting Equipment',''),f'se:{cls}'); sy['wealth']=''
        sy['hd']={'denomination':hd_of(ct),'spent':0,'additional':''}
        sy['advancement']=advd(adv)
        pa=ct.get('Primary Ability','')
        abil=[ABL[w] for w in ABL if w in pa.lower()]
        if abil: sy['primaryAbility']={'value':abil,'all':' and ' in pa}
        if base is None:
            sy['spellcasting']={'progression':'artificer','ability':'int','preparation':{'formula':f'@scale.{cid}.max-prepared'}}
        elif sy['spellcasting'].get('progression','none')!='none':
            sy['spellcasting']['preparation']['formula']=sy['spellcasting']['preparation']['formula'].replace(f'.{base}.',f'.{cid}.')
            sy['spellcasting']['ability']=CASTER_ABIL[cls]
        cdoc={'_id':_id,'name':cls,'type':'class','img':f'modules/{MOD}/icons/classes/{cid}.png','system':sy,'effects':[],'folder':cfold,'sort':0,'flags':{}}
        write('classes',f'{cid}/{cid}.yml',cdoc)
        # subclasses
        subs=[(s,SRC_HB) for s in C['subclasses']]+[(s,SRC_OD) for s in O['overdrive'] if s['class']==cls]
        for si,(S,src) in enumerate(subs):
            sid=ident(S['name']); sf=folder('features',f'{cid}/{sid}',f'{S["name"]} {cls}',parent=ffold,sort=50+si)
            byl={}
            for f in S['features']:
                seed=f'sfeat:{cls}:{S["name"]}:{f["name"]}:{f["level"]}'
                rows=subspell_rows(f['name']) if f['name'].endswith('Spells') else None
                if rows: d=spells_feature(f['name'],f['html'],f['text'],rows,level=f['level'],req=f'{S["name"]} {cls}',seed=seed,src=src,method='pact' if cls=='Cryptist' else 'spell')
                else: d=new_feat(f['name'],f['html'],f['text'],level=f['level'],req=f'{S["name"]} {cls}',seed=seed,cls=cls,src=src)
                d['folder']=sf; write('features',f'{cid}/{sid}/{ident(f["name"])}-{f["level"]}.yml',d)
                byl.setdefault(f['level'],[]).append(uuid('features',d['_id']))
                report.append((cls+'/'+S['name'],f['name'],'spells' if rows else 'new',len(d['system'].get('activities',{}))))
            sadv=[grant(f'sig:{cls}:{S["name"]}:{L}',L,us,'Subclass Features') for L,us in sorted(byl.items())]
            sdoc={'_id':mkid(f'sub:{cls}:{S["name"]}'),'name':S['name'],'type':'subclass','img':f'modules/{MOD}/icons/subclasses/{sid}.webp',
                'system':{'description':{'value':S['intro']['html'],'chat':''},'source':dict(src),'identifier':sid,'classIdentifier':cid,'advancement':advd(sadv),'spellcasting':{'progression':'none','ability':'','preparation':{'formula':''}}},
                'effects':[],'folder':cfold,'sort':si+1,'flags':{}}
            write('classes',f'{cid}/{sid}.yml',sdoc)
    json.dump(report,open('report.json','w'),indent=0,ensure_ascii=False)
    import collections
    print(collections.Counter(r[2].split(':')[0] for r in report), sum(1 for r in report if r[3]==0),'features w/o activities of',len(report))
if __name__=='__main__': main()
