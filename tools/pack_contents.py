import sys,glob,yaml,re,os,copy; sys.path.insert(0,'.')
from common import OUT
from autoact import mkid
IT=os.path.join(OUT,'items')
docs={}
for f in glob.glob(IT+'/**/*.yml',recursive=True):
    if f.endswith('_folder.yml') or '/pack-contents/' in f: continue
    d=yaml.safe_load(open(f)); docs[d['name'].lower()]=d
def find(n):
    n=n.strip().lower().rstrip('.')
    for k in (n, n.rstrip('s'), n[:-2] if n.endswith('es') else n, re.sub(r'ies$','y',n)):
        if k in docs: return docs[k]
    return None
os.makedirs(IT+'/pack-contents',exist_ok=True)
fid=mkid('folder:items:pack-contents')
yaml.safe_dump({'_id':fid,'name':'Pack Contents','type':'Item','folder':None,'sorting':'a','sort':999999,'color':None,'flags':{},'description':'','_key':f'!folders!{fid}'},open(IT+'/pack-contents/_folder.yml','w'),sort_keys=False)
miss=[];made=0
for d in list(docs.values()):
    if d['type']!='container': continue
    txt=re.sub('<[^>]+>',' ',d['system']['description']['value'])
    m=re.search(r'contains the following items:\s*([^.]+(?:\.\d[^.]*)*)\.',txt)
    if not m: continue
    for part in re.split(r',\s*|\s+and\s+',m.group(1)):
        part=part.strip(); mq=re.match(r'(\d+)\s+(.*)',part); q,nm=(int(mq.group(1)),mq.group(2)) if mq else (1,part)
        src=find(nm) or find(re.sub(r'\s*\(.*\)','',nm))
        if not src: miss.append((d['name'],nm)); continue
        c=copy.deepcopy(src); cid=mkid(d['_id']+':'+src['_id']); c['_id']=cid; c['folder']=fid
        c['system']['container']=d['_id']; c['system']['quantity']=q; c['_key']=f'!items!{cid}'
        for e in c.get('effects') or []: e['_key']=f"!items.effects!{cid}.{e['_id']}"
        yaml.safe_dump(c,open(f"{IT}/pack-contents/{re.sub('[^a-z0-9]+','-',d['name'].lower())}--{re.sub('[^a-z0-9]+','-',src['name'].lower())}.yml",'w'),sort_keys=False,allow_unicode=True,width=200); made+=1
print('content items',made,'missing',miss)
