import sys,yaml,glob,os; sys.path.insert(0,'.')
from common import OUT, stats
from autoact import mkid
def chg(key,val,typ): return {'key':key,'value':str(val),'priority':None,'type':typ,'phase':'initial','_id':mkid(f'ac:{key}:{val}')}
FIX={'shield-of-the-elements-3.yml':('Shield of the Elements',[chg('system.attributes.ac.calcs','neonShieldOfElements','add')],False),
     'dirty-fighting-3.yml':('Dirty Fighting: Unarmored Defense',[chg('system.attributes.ac.calcs','unarmoredBard','add')],False),
     'thick-hide.yml':('Thick Hide',[chg('system.attributes.ac.bonus','+1','add')],False),
     'upgrade-algorithm-10.yml':('Upgrade Algorithm (Hardlight Armory active)',[chg('system.attributes.ac.bonus','+2','add')],True),
     'borrowed-time-6.yml':('Borrowed Time (concentrating on Haste)',[chg('system.attributes.ac.bonus','+1','add')],True),
     'abyssal-parasite-3.yml':('Abyssal Parasite (under Mage Armor)',[chg('system.attributes.ac.bonus','+2','add')],True)}
n=0
for f in glob.glob(os.path.join(OUT,'features','**','*.yml'),recursive=True):
    b=os.path.basename(f)
    if b not in FIX: continue
    d=yaml.safe_load(open(f)); name,changes,dis=FIX[b]; eid=mkid(d['_id']+':acfx')
    d['effects']=[e for e in (d.get('effects') or []) if e.get('_id')!=eid]+[{'_id':eid,'name':name,'img':d['img'],'type':'base','system':{'changes':changes},
      'disabled':dis,'transfer':True,'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},'description':'','tint':'#ffffff','statuses':[],'sort':0,'flags':{},
      'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"}]
    yaml.safe_dump(d,open(f,'w'),sort_keys=False,allow_unicode=True,width=200); n+=1; print('ac effect',os.path.relpath(f,OUT))
print('ac fixed',n)
