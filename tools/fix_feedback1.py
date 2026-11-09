import sys,os,copy,yaml; sys.path.insert(0,'.')
from common import OUT,stats
from autoact import mkid
def L(p): return yaml.safe_load(open(os.path.join(OUT,p)))
def D(p,d): yaml.safe_dump(d,open(os.path.join(OUT,p),'w'),sort_keys=False,allow_unicode=True,width=200)
def chg(k,v,t,pr=None): return {'key':k,'value':str(v),'priority':pr,'type':t,'phase':'initial','_id':mkid(f"r3:{k}:{v}")}
def eff(d,name,changes,tag,transfer=False,disabled=False,statuses=(),desc='',duration=None):
    eid=mkid(d['_id']+':r3:'+tag)
    return {'_id':eid,'name':name,'img':d.get('img'),'type':'base','system':{'changes':changes},'disabled':disabled,'transfer':transfer,
      'duration':duration or {'value':None,'units':'seconds','expiry':None,'expired':False},'description':desc,'tint':'#ffffff','statuses':list(statuses),'sort':0,'flags':{},
      'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"}
VIS={'level':{'min':None,'max':None},'identifier':'','requireAttunement':False,'requireIdentification':False,'requireMagic':False}
def act(d,tag,typ,name,activation='action',cond='',cons=None,rng=None,target=None,effects=(),flavor='',minlvl=None,cls=None,**extra):
    i=mkid(d['_id']+':r3act:'+tag)
    a={'_id':i,'type':typ,'name':name,'img':'','sort':0,'activation':{'type':activation,'value':None,'override':False,'condition':cond},
       'consumption':{'scaling':{'allowed':False,'max':''},'spellSlot':False,'targets':cons or []},'description':{'chatFlavor':flavor},
       'duration':{'units':'inst','concentration':False,'override':False,'value':'','special':''},
       'effects':[{'_id':e,'riders':{'activity':[],'effect':[],'item':[]}} for e in effects],
       'range':rng or {'units':'self','override':False,'special':''},
       'target':target or {'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'','type':'self'},'override':False,'prompt':False},
       'uses':{'spent':0,'recovery':[],'max':''},'flags':{},'visibility':copy.deepcopy(VIS),'behaviors':[]}
    if minlvl: a['visibility']['identifier']=cls; a['visibility']['level']['min']=minlvl
    a.update(extra); return i,a
def uses(n,tgt=''): return [{'type':'itemUses','value':str(n),'target':tgt,'scaling':{}}]
def dpart(n,f,types,custom=None,bonus=''):
    return {'number':n,'denomination':f,'bonus':bonus,'types':list(types),'custom':{'enabled':bool(custom),'formula':custom or ''},'scaling':{'mode':'','number':None,'formula':''}}
def ft(n): return {'value':str(n),'units':'ft','special':'','override':False}
def one(kind='creature',count='1'): return {'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':count,'type':kind},'override':False,'prompt':False}
def area(typ,size): return {'template':{'contiguous':False,'units':'ft','type':typ,'size':str(size),'width':'','count':'','stationary':False},'affects':{'choice':True,'count':'','type':'creature'},'override':False,'prompt':True}
def roll(f,name): return {'formula':f,'name':name,'prompt':False,'visible':True}
def heal(f,t='healing'): return dpart(None,None,[t],f)
def setacts(d,pairs): d['system']['activities']={i:a for i,a in pairs}
def rec(*p): return [{'period':x,'type':'recoverAll'} for x in p]
def setuses(d,mx,*p): d['system']['uses']={'max':str(mx),'spent':0,'recovery':rec(*p)}
def rnd(n=1): return {'units':'rounds','value':str(n),'expiry':None,'expired':False}
def turn(): return {'units':'turns','value':'1','expiry':'turnEnd','expired':False}
def mins(n): return {'value':n*60,'units':'seconds','expiry':None,'expired':False}
SPDC={'calculation':'spellcasting','formula':''}
P24='Compendium.dnd5e.spells24.Item.'; PNO='Compendium.neon-odyssey.spells.Item.'
def cast(d,tag,name,uuid,lvl,activation='action',cond='',cons=None):
    i,a=act(d,tag,'cast',name,activation,cond,cons)
    a['spell']={'uuid':uuid,'challenge':{'override':False},'properties':['vocal','somatic'],'spellbook':False,'ability':'','level':lvl}
    a['target']['prompt']=True; return i,a
def svdc(a,abil,dc): a['save']={'ability':[abil],'dc':dc}
def dmg(a,parts,on=None):
    a['damage']={'critical':{'allow':False,'bonus':''},'parts':parts}
    if on: a['damage']['onSave']=on
def line(l,w): return {'template':{'contiguous':False,'units':'ft','type':'line','size':str(l),'width':str(w),'count':'','stationary':False},'affects':{'choice':True,'count':'','type':'creature'},'override':False,'prompt':True}
def maxlvl(a,cls,n): a['visibility']['identifier']=cls; a['visibility']['level']['max']=n
def noacteff(d,names):
    keep=[e for e in d.get('effects',[]) if e['name'] not in names]; ids={e['_id'] for e in keep}; d['effects']=keep
    for a in d['system'].get('activities',{}).values(): a['effects']=[x for x in a.get('effects',[]) if x['_id'] in ids]
def MIN(lvl): return {'units':'minute','value':str(lvl),'concentration':False,'override':False,'special':''}
JL='@classes.juggernaut.levels'; SG='@scale.juggernaut.rage-damage'; STRDC={'calculation':'str','formula':''}
OL='@classes.oracle.levels'; CC='feat:cosmic-conduit'; SU='feat:surge'
import re
RID=lambda e:{'_id':e['_id'],'riders':{'activity':[],'effect':[],'item':[]}}
# ================= FEEDBACK 1: Surge, Mythic Presence, Glory of Agathos =================
J='features/juggernaut/'
def spc(c): return {'type':'special','value':None,'override':False,'condition':c}
p=J+'class-features/surge-1.yml'; d=L(p)
for e in d['effects']:
    if e['name']=='Surge': e['transfer']=False; e['disabled']=False; e['duration']=mins(10)
    else: e['duration']=mins(10)
a=next(iter(d['system']['activities'].values())); a['name']='Activate Surge'
a['description']={'chatFlavor':'Choose three Resistances in the Surge window; the Surge effects are applied to you automatically.'}; D(p,d)
p=J+'eternal/call-the-power-3.yml'; d=L(p)
mp=eff(d,'Mythic Presence',[chg('system.bonuses.abilities.save','+1d4','add')],'mythic',duration=mins(10),desc='<p>Add 1d4 to saving throws while within 10 feet of the Eternal Juggernaut.</p>')
gp=eff(d,'Glorious Presence',[chg('system.bonuses.abilities.save','+1d4','add')],'glorious',duration=mins(10),desc='<p>Add 1d4 to saving throws while within 30 feet of the Eternal Juggernaut. An ally that starts its turn in the Emanation adds the Juggernaut\u2019s Surge Damage bonus to its damage rolls until the start of its next turn.</p>')
d['effects']=[e for e in d['effects'] if e['name'] not in ('Mythic Presence','Glorious Presence')]+[mp,gp]
i1,a1=act(d,'mythic','utility','Mythic Presence','special','While your Surge is active (10-ft Emanation)',effects=[mp['_id']],duration=MIN(10)); maxlvl(a1,'juggernaut',13)
i2,a2=act(d,'glorious','utility','Glorious Presence','special','While your Surge is active (30-ft Emanation)',effects=[gp['_id']],duration=MIN(10),minlvl=14,cls='juggernaut')
d['system']['activities'].update({i1:a1,i2:a2}); D(p,d)
C='origins/species-traits/cygnian/'
FL='Spend Heroic Inspiration to use it again without a Long Rest.'
def opt(fn):
    p=C+fn+'.yml'; d=L(p); setuses(d,1,'lr'); return p,d
p,d=opt('beacon'); be=eff(d,'Beacon',[],'beacon',duration=mins(1),desc='<p>For 1 minute, when you miss with an attack roll, you can take a Reaction to reroll the d20 and use the new roll.</p>'); d['effects']=[be]
setacts(d,[act(d,'beacon','utility','Beacon','bonus','',uses(1),effects=[be['_id']],duration=MIN(1),flavor=FL),
  act(d,'beaconr','utility','Beacon: Reroll','reaction','You miss with an attack roll while Beacon is active',roll=roll('1d20','Reroll'))]); D(p,d)
p,d=opt('chronicle')
ch=[eff(d,f'Chronicle: {n}',[chg(f'system.abilities.{k}.bonuses.save','@prof','add')],'chr'+k,duration=mins(1)) for k,n in [('str','Strength'),('dex','Dexterity'),('con','Constitution'),('int','Intelligence'),('wis','Wisdom'),('cha','Charisma')]]
d['effects']=ch
setacts(d,[act(d,'chron','utility','Chronicle (pick an ability)','bonus','',uses(1),effects=[e['_id'] for e in ch],duration=MIN(1),flavor=FL)]); D(p,d)
p,d=opt('fountain')
i3,a3=act(d,'fountain','heal','Fountain','bonus','Touch a creature',uses(1),ft(5),one('ally'),flavor=FL)
a3['healing']={'number':None,'denomination':None,'bonus':'','types':['temphp'],'custom':{'enabled':True,'formula':'(@prof)d6'},'scaling':{'mode':'','number':None,'formula':''}}
d['effects']=[]; setacts(d,[(i3,a3)]); D(p,d)
p,d=opt('tower'); to=eff(d,'Tower',[],'tower',duration=mins(1),desc='<p>For 1 minute, when you take damage, you can take a Reaction to reduce the damage by 1d12 + your Proficiency Bonus.</p>'); d['effects']=[to]
setacts(d,[act(d,'tower','utility','Tower','bonus','',uses(1),effects=[to['_id']],duration=MIN(1),flavor=FL),
  act(d,'towerr','utility','Tower: Reduce Damage','reaction','You take damage while Tower is active',roll=roll('1d12 + @prof','Damage reduced'))]); D(p,d)
p=C+'glory-of-agathos.yml'; d=L(p); d['effects']=[]; d['system']['activities']={}; d['system']['uses']={'max':'','spent':0,'recovery':[]}; D(p,d)
OPTS={L(C+f+'.yml')['_id'] for f in ('beacon','chronicle','fountain','tower')}
p='origins/species/cygnian.yml'; d=L(p); adv=d['system']['advancement']
g=next(a for a in adv.values() if a['type']=='ItemGrant')
g['configuration']['items']=[x for x in g['configuration']['items'] if x['uuid'].split('.')[-1] not in OPTS]
cid=mkid('cygnian:glorychoice')
adv[cid]={'_id':cid,'type':'ItemChoice','level':0,'title':'Glory of Agathos','hint':'Choose your triad: Beacon, Chronicle, Fountain or Tower.',
  'configuration':{'choices':{'0':{'count':1,'replacement':False}},'allowDrops':False,
    'pool':[{'uuid':'Compendium.neon-odyssey.origins.Item.'+L(C+f+'.yml')['_id']} for f in ('beacon','chronicle','fountain','tower')],
    'restriction':{'type':'','subtype':'','level':'','list':[]},'type':'feat'},'value':{}}
D(p,d)

# effect names: book renames
for fp,new in [('features/juggernaut/class-features/amplified-reflexes-2.yml','Amplified Reflexes'),('features/juggernaut/class-features/driving-momentum-5.yml','Driving Momentum'),
               ('features/juggernaut/class-features/hardened-form-1.yml','Hardened Form'),('features/juggernaut/class-features/heightened-awareness-7.yml','Heightened Awareness'),
               ('features/disciple/class-features/balanced-guard-1.yml','Balanced Guard')]:
    d=L(fp)
    for e in d.get('effects',[]):
        if e['name'] in ('Danger Sense','Fast Movement','Unarmored Defense','Feral Instinct'): e['name']=new
    D(fp,d)
print('feedback1 done')
