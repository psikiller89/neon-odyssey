import os, re, json, yaml, unicodedata, shutil
from autoact import mkid
MOD='neon-odyssey'
OUT=os.path.expanduser('~/work/neon-odyssey/packs/_source')
SRD=json.load(open(os.path.expanduser('~/work/srd_spells24.json')))
O=json.load(open(os.path.expanduser('~/work/build/outline.json')))
SCHOOLS={'abjuration':'abj','conjuration':'con','divination':'div','enchantment':'enc','evocation':'evo','illusion':'ill','necromancy':'nec','transmutation':'trs'}
SRC_HB={'custom':'','book':'Neon Odyssey: Outrunner’s Handbook','page':'','license':'','rules':'2024','revision':1}
SRC_OD={'custom':'','book':'Neon Odyssey: Overdrive Expansion','page':'','license':'','rules':'2024','revision':1}
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s.replace('’',"'")).lower())
def ident(s): return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',s.replace('’','')).lower())).strip('-')
def uuid(pack,_id,doc='Item'): return f'Compendium.{MOD}.{pack}.{doc}.{_id}'
def phb_guess(name):
    s=re.sub(r'[^A-Za-z0-9]','',''.join(w[:1].upper()+w[1:] for w in re.split(r'[\s/-]+',name.replace('’',"'")) ))
    s=re.sub(r'[^A-Za-z0-9]','',' '.join(name.replace('’',"'").split()).replace(' ',''))
    return ('phbspl'+s)[:16].ljust(16,'0')
def stats():
    return {'coreVersion':'14.360','systemId':'dnd5e','systemVersion':'6.0.6','createdTime':None,'modifiedTime':None,'lastModifiedBy':None,'duplicateSource':None,'exportSource':None,'compendiumSource':None}
def write(pack, rel, doc, kind='items'):
    doc.setdefault('_stats',stats()); doc.setdefault('flags',{}); doc.setdefault('ownership',{'default':0})
    doc['_key']=f"!{kind}!{doc['_id']}"
    for e in doc.get('effects',[]) or []:
        e['_key']=f"!items.effects!{doc['_id']}.{e['_id']}"
    p=os.path.join(OUT,pack,rel); os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,'w') as f: yaml.safe_dump(doc,f,sort_keys=False,allow_unicode=True,width=200)
def folder(pack, rel, name, parent=None, sort=0, typ='Item'):
    _id=mkid(f'folder:{pack}:{rel}')
    d={'name':name,'sorting':'a','folder':parent,'type':typ,'_id':_id,'description':'','sort':sort,'color':None,'flags':{},'_stats':stats(),'_key':f'!folders!{_id}'}
    p=os.path.join(OUT,pack,rel,'_folder.yml'); os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,'w') as f: yaml.safe_dump(d,f,sort_keys=False,allow_unicode=True)
    return _id
def reset(pack):
    p=os.path.join(OUT,pack)
    if os.path.exists(p): shutil.rmtree(p)
    os.makedirs(p)
# Name->spell resolution
NEW={s['name']:s for s in O['spells']}
def spell_id(name): return mkid('spell:'+name)
def resolve_spell(name):
    """returns (uuid or None, level, school, kind)"""
    n=re.sub(r'\*','',name).strip()
    m=re.match(r'^(.*?)\s*\((.+)\)$',n)
    cands=[n]+([m.group(1).strip(),m.group(2).strip()] if m else [])
    for c in cands:
        for k,v in NEW.items():
            if norm(k)==norm(c): return uuid('spells',spell_id(k)),v['level'],SCHOOLS.get((v['school'] or '').lower(),''),'new'
    for c in cands[::-1]:
        for k,v in SRD.items():
            if norm(k)==norm(c): return v['uuid'],v['level'],v['school'],'srd'
    base=cands[-1]
    return f'Compendium.dnd-players-handbook.spells.Item.{phb_guess(base)}',None,None,'phb'
