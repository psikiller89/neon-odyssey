import re, glob, yaml, os
from common import *
from autoact import mkid
def item_index():
    idx={}
    for f in glob.glob(os.path.join(OUT,'items','**','*.yml'),recursive=True):
        if f.endswith('_folder.yml'): continue
        d=yaml.safe_load(open(f)); idx[norm(re.sub(r'\s*\((Weapon|Armor) Module\)','',d['name']))]=uuid('items',d['_id'])
    return idx
SING={'bullets':'Bullets','shells':'Shells','power cells':'Power Cell','power cell':'Power Cell','magazines':'Magazine','combat knives':'Combat Knife','ration pouches':'Ration Pouch'}
def resolve(name,idx):
    n=re.sub(r'\s*\(.*?\)','',name).strip()
    for c in (n, SING.get(n.lower(),''), n.rstrip('s'), n[:-2] if n.endswith('es') else ''):
        if c and norm(c) in idx: return idx[norm(c)]
    for k,u in idx.items():
        if norm(n) and (k.startswith(norm(n)) or norm(n).startswith(k)) and len(k)>4: return u
    return None
def build(text, seed):
    idx=item_index(); out=[]; sort=[100000]
    def add(e): e['sort']=sort[0]; sort[0]+=100000; out.append(e); return e
    opts=re.findall(r'\(([A-C])\)\s*(.*?)(?=;?\s*(?:or\s*)?\([A-C]\)|$)',text)
    root=add({'_id':mkid(seed+':or'),'type':'OR','group':'','requiresProficiency':False}) if len(opts)>1 else None
    for letter,body in opts:
        g=add({'_id':mkid(seed+':'+letter),'type':'AND','group':root['_id'] if root else '','requiresProficiency':False})
        for part in re.split(r',\s+(?:and\s+)?|\s+and\s+',body.strip().rstrip(';').rstrip('.')):
            part=part.strip()
            if not part: continue
            m=re.match(r'^\$([\d,]+)',part)
            if m: add({'_id':mkid(seed+letter+part),'type':'currency','key':'gn','count':int(m.group(1).replace(',','')),'group':g['_id'],'requiresProficiency':False}); continue
            m=re.match(r'^(\d+)\s+(.*)$',part); cnt=int(m.group(1)) if m else None; nm=m.group(2) if m else part
            if ' or ' in nm: nm=nm.split(' or ')[0]
            u=resolve(nm,idx)
            if u: add({'_id':mkid(seed+letter+part),'type':'linked','key':u,'count':cnt,'group':g['_id'],'requiresProficiency':False})
    return out
