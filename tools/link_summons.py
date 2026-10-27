import sys,json,glob,yaml,os; sys.path.insert(0,'.')
from common import OUT
from autoact import mkid
S=json.load(open('summon_uuids.json'))
LINKS={'machinist/riveter/deploy-turret-3.yml':['Rivet Turret'],'primalist/class-features/primal-channel-2.yml':['Ambush Form','Battle Form','Swift Form']}
for rel,names in LINKS.items():
    p=os.path.join(OUT,'features',rel)
    if not os.path.exists(p): print('missing',rel); continue
    d=yaml.safe_load(open(p)); _id=d['_id']
    a={'_id':mkid(_id+':summon'),'type':'summon','name':'Summon' if len(names)==1 else 'Primal Form','activation':{'type':'bonus' if 'turret' in rel else 'action','value':None,'condition':'','override':False},
       'consumption':{'targets':[{'type':'itemUses','value':'1','target':'','scaling':{}}] if d['system'].get('uses',{}).get('max') else [],'scaling':{'allowed':False,'max':''},'spellSlot':True},
       'description':{'chatFlavor':''},'duration':{'units':'inst','override':False},'range':{'override':False,'units':'self'},'target':{'override':False,'prompt':False},'effects':[],'uses':{'spent':0,'recovery':[],'max':''},'sort':0,
       'bonuses':{'ac':'','hd':'','hp':'','attackDamage':'','saveDamage':'','healing':''},'match':{'attacks':True,'proficiency':True,'saves':True,'ability':''},
       'profiles':[{'_id':mkid(_id+n),'count':'1','cr':'','level':{'min':None,'max':None},'name':n,'uuid':S[n]} for n in names if n in S],'summon':{'mode':'','prompt':True},'creatureSizes':[],'creatureTypes':[]}
    d['system'].setdefault('activities',{})[a['_id']]=a
    yaml.safe_dump(d,open(p,'w'),sort_keys=False,allow_unicode=True,width=200); print('linked',rel)
