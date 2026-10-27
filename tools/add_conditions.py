import sys,glob,yaml,re,os; sys.path.insert(0,'.')
from common import OUT, stats
from autoact import mkid
CONDS=['Blinded','Charmed','Deafened','Frightened','Grappled','Incapacitated','Invisible','Paralyzed','Petrified','Poisoned','Prone','Restrained','Stunned','Unconscious']
n=0
for f in glob.glob(os.path.join(OUT,'**','*.yml'),recursive=True):
    if f.endswith('_folder.yml') or '/bestiary/' in f or '/rules/' in f or '/spell-lists/' in f: continue
    d=yaml.safe_load(open(f)); s=d.get('system',{}); acts=s.get('activities') or {}
    if not acts: continue
    txt=re.sub('<[^>]+>',' ',s.get('description',{}).get('value',''))
    found=[c for c in CONDS if re.search(rf'(the|have the|has the|gains? the|give \w+ the) {c} condition',txt)]
    if not found: continue
    effs=d.setdefault('effects',[]) or []; d['effects']=effs; ids=[]
    for c in found:
        eid=mkid(d['_id']+':cond:'+c)
        if not any(e.get('_id')==eid for e in effs):
            effs.append({'_id':eid,'name':c,'img':f'systems/dnd5e/icons/svg/statuses/{c.lower()}.svg','type':'base','system':{'changes':[]},'statuses':[c.lower()],'transfer':False,'disabled':False,
              'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},'origin':None,'tint':'#ffffff','sort':0,'flags':{},'description':'','showIcon':1,'start':None,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"})
        ids.append(eid)
    for a in acts.values():
        if a.get('type') in('save','attack','utility','damage'):
            ex={e['_id'] for e in a.get('effects',[]) or []}
            a['effects']=(a.get('effects') or [])+[{'_id':i,'onSave':False} for i in ids if i not in ex]
    yaml.safe_dump(d,open(f,'w'),sort_keys=False,allow_unicode=True,width=200); n+=1
print('items with condition effects:',n)
