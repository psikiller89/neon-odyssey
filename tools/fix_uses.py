import sys,yaml,glob,os; sys.path.insert(0,'.')
from common import OUT
U={'Deploy Turret':'max(1, @abilities.int.mod)','Symbiotic Carnage':'max(1, floor(@prof / 2))','Inescapable Hunt':'1','Chrono Control':'1','Roaring Devastation':'1','Reconstitution':'1'}
n=0
for f in glob.glob(os.path.join(OUT,'features','**','*.yml'),recursive=True)+glob.glob(os.path.join(OUT,'origins','**','*.yml'),recursive=True):
    d=yaml.safe_load(open(f))
    if not isinstance(d,dict) or d.get('name') not in U or d.get('type')!='feat': continue
    u=d['system'].setdefault('uses',{'spent':0,'recovery':[],'max':''})
    if u.get('max'): continue
    u['max']=U[d['name']]; u['recovery']=[{'period':'lr','type':'recoverAll'}]; u['spent']=0
    for a in (d['system'].get('activities') or {}).values():
        c=a.setdefault('consumption',{'targets':[],'scaling':{'allowed':False,'max':''},'spellSlot':True})
        if not c.get('targets'): c['targets']=[{'type':'itemUses','target':'','value':'1','scaling':{'mode':'','formula':''}}]
    yaml.safe_dump(d,open(f,'w'),sort_keys=False,allow_unicode=True,width=200); n+=1; print('uses',d['name'])
print('uses fixed',n)
