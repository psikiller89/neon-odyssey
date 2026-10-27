import sys,yaml,os,copy,re; sys.path.insert(0,'.')
from common import OUT
from autoact import mkid
F=os.path.join(OUT,'features','machinist','class-features'); P=os.path.join(F,'invention-specialist-1.yml')
def dump(d,p): yaml.safe_dump(d,open(p,'w'),sort_keys=False,allow_unicode=True,width=200)
par=yaml.safe_load(open(P)); html=par['system']['description']['value']
spell_uuid=next(iter(par['system']['advancement'].values()))['configuration']['items'][0]['uuid']
def para(key):
    ps=re.findall(r'<p>.*?</p>',html,re.S); out=[];on=False
    for p in ps:
        t=re.sub('<[^>]+>','',p).strip()
        if re.match(r'(Armory|Hypertech|Robotics)\.',t): on=t.startswith(key+'.')
        if on: out.append(p)
    return ''.join(out) or f'<p>{key}</p>'
def adv(aid,typ,conf,title,val): return {'_id':aid,'type':typ,'configuration':conf,'value':val,'level':1,'title':title,'hint':''}
OPTS={'Armory':lambda i:{(a:=mkid(i+':t')):adv(a,'Trait',{'mode':'default','allowReplacements':False,'grants':['weapon:mar','armor:hvy'],'choices':[]},'Armory Training',{'chosen':[]})},
 'Hypertech':lambda i:{(a:=mkid(i+':c')):adv(a,'ItemChoice',{'allowDrops':True,'choices':{'1':{'count':2,'replacement':False}},'pool':[],'restriction':{'list':['class:machinist'],'level':'0','school':[],'subtype':'','type':''},
        'spell':{'ability':['int'],'method':'spell','uses':{'max':'','per':'','requireSlot':False},'prepared':2},'type':'spell','sorting':'a'},'Hypertech Cantrips',{'added':{},'replaced':{}}),
   (b:=mkid(i+':e')):adv(b,'Trait',{'mode':'expertise','allowReplacements':False,'grants':[],'choices':[{'count':1,'pool':['skills:arc','skills:cmp','skills:inv','skills:tec']}]},'Hypertech Expertise',{'chosen':[]})},
 'Robotics':lambda i:{(a:=mkid(i+':g')):adv(a,'ItemGrant',{'items':[{'uuid':spell_uuid,'optional':False,'sort':0}],'optional':False,
        'spell':{'ability':['int'],'uses':{'max':'','per':'','requireSlot':False},'method':'atwill','prepared':2}},'Autonomous Assistant',{})}}
pool=[]
for k,fn in OPTS.items():
    d=copy.deepcopy(par); i=mkid(par['_id']+':opt:'+k); d['_id']=i; d['_key']=f'!items!{i}'; d['name']=f'Invention Specialist: {k}'
    d['system']['identifier']='invention-specialist-'+k.lower(); d['system']['description']['value']=para(k); d['system']['advancement']=fn(i)
    d['system']['activities']={}; d['effects']=[]; d['sort']=par.get('sort',0)+1
    dump(d,os.path.join(F,f'invention-specialist-{k.lower()}.yml')); pool.append({'uuid':f'Compendium.neon-odyssey.features.Item.{i}','sort':0})
a=mkid(par['_id']+':choice')
par['system']['advancement']={a:{'_id':a,'type':'ItemChoice','configuration':{'choices':{'1':{'count':1,'replacement':False}},'allowDrops':False,'type':'feat','pool':pool,'spell':None,
   'restriction':{'type':'class','subtype':'','list':[],'level':'','school':[]},'sorting':'a'},'value':{'added':{},'replaced':{}},'level':1,'title':'Invention Specialist','hint':'Choose Armory, Hypertech or Robotics.'}}
par['system']['activities']={}
dump(par,P); print('invention specialist options',[p['uuid'][-16:] for p in pool])
