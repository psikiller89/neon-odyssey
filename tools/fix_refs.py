import sys,yaml,glob,os,re,json; sys.path.insert(0,'.')
from common import OUT
def slug(t): return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',(t or '').lower())).strip('-')
FIXED={'6FTnn7DjW37STeW6':'rages','wMwMS7RC49lh1hp2':'unarmored-movement','FksFWNV4X4lTFlvO':'favored-enemy'}
SV={}
for f in glob.glob('/home/ubuntu/work/dnd5e/packs/_source/classes24/*/*.yml'):
    d=yaml.safe_load(open(f)); adv=(d.get('system') or {}).get('advancement') or []
    for a in (adv.values() if isinstance(adv,dict) else adv):
        if isinstance(a,dict) and a.get('type')=='ScaleValue': SV[a['_id']]=a['configuration'].get('identifier') or FIXED.get(a['_id']) or slug(a.get('title'))
files=[f for f in glob.glob(os.path.join(OUT,'classes','**','*.yml'),recursive=True)+glob.glob(os.path.join(OUT,'features','**','*.yml'),recursive=True) if not f.endswith('_folder.yml')]
def cdir(f): return os.path.relpath(f,OUT).split(os.sep)[1]
docs={f:yaml.safe_load(open(f)) for f in files}
src={}
for f,d in docs.items():
    s=(d.get('flags') or {}).get('neon-odyssey',{}).get('srcIdentifier'); new=(d.get('system') or {}).get('identifier')
    if s and new and s!=new: src.setdefault(s,[]).append((cdir(f),new))
ours={(d.get('system') or {}).get('identifier') for d in docs.values()}
nsv=nref=0
for f,d in docs.items():
    adv=(d.get('system') or {}).get('advancement') or {}
    for a in (adv.values() if isinstance(adv,dict) else adv):
        if a.get('type')=='ScaleValue' and not a['configuration'].get('identifier'):
            a['configuration']['identifier']=SV.get(a['_id']) or slug(a.get('title')); nsv+=1
    s0=json.dumps(d,ensure_ascii=False); s=s0
    for o,lst in src.items():
        if o in ours: continue
        new=next((n for c,n in lst if c==cdir(f)),lst[0][1])
        s=re.sub(r'(feat:)'+re.escape(o)+r'\b',r'\g<1>'+new,s); s=s.replace(f'@scale.{o}.',f'@scale.{new}.')
    s=re.sub(r'@scale\.juggernaut\.rage(?![-\w])','@scale.juggernaut.rages',s)
    if s!=s0 or nsv:
        if s!=s0: nref+=1; d=json.loads(s)
        yaml.safe_dump(d,open(f,'w'),sort_keys=False,allow_unicode=True,width=200)
print('scale ids set',nsv,'files with refs fixed',nref)
