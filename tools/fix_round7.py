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
def actuse(a,n=1,*per):
    a['uses']={'spent':0,'recovery':rec(*per),'max':str(n)}
    a['consumption']['targets']=[{'type':'activityUses','value':'1','target':'','scaling':{}}]
def grant(tag,lvl,title,uuids):
    i=mkid('r4grant:'+tag); return i,{'_id':i,'type':'ItemGrant','configuration':{'items':[{'uuid':u,'optional':False,'sort':0} for u in uuids],'optional':False,'spell':None},'value':{},'level':lvl,'title':title,'hint':'','icon':None,'classRestriction':'','flags':{}}
def trait(tag,lvl,title,grants=(),choices=(),mode='default'):
    i=mkid('r4trait:'+tag); return i,{'_id':i,'type':'Trait','level':lvl,'title':title,'hint':'','icon':None,'classRestriction':'','flags':{},
      'configuration':{'mode':mode,'allowReplacements':False,'grants':list(grants),'choices':list(choices)},'value':{}}
def spc(c): return {'type':'special','value':None,'override':False,'condition':c}
def first(d): return next(iter(d['system']['activities'].values()))
def noadv(d,typ): d['system']['advancement']={k:v for k,v in d['system']['advancement'].items() if v.get('type')!=typ}
def atk(a,kind,cls,ability,parts):
    a['attack']={'ability':ability,'bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':kind,'classification':cls}}
    a['damage']={'critical':{'bonus':''},'includeBase':False,'parts':parts}
BPS=['bludgeoning','piercing','slashing']
def newfeat(src,path,name,desc,ident):
    d=L(src); i=mkid('r5feat:'+name); d['_id']=i; d['_key']='!items!'+i; d['name']=name; d['system']['description']['value']=desc
    d['system']['identifier']=ident; d['system']['activities']={}; d['effects']=[]; d['system']['uses']={'max':'','spent':0,'recovery':[]}; D(path,d); return 'Compendium.neon-odyssey.features.Item.'+i
def resist(d,types,label,tag):
    return [eff(d,f'{label}: {t.title()}',[chg('system.traits.dr.value',t,'add')],tag+t,transfer=True,disabled=True,desc='<p>Turn on the type you chose.</p>') for t in types]
# ================= ROUND 7: Gridrunner tools/Hyperpad/Override, Virus Malware, Gorgonite =================
FU='Compendium.neon-odyssey.features.Item.'; IU='Compendium.neon-odyssey.items.Item.'
def iu(): return [{'type':'itemUses','value':'1','target':'','scaling':{}}]
# ---- tools: give Neon tool items dnd5e base keys
for fn,typ,key in [('bypass-tools','','bypass'),('electronics-tools','art','electronics'),('spiking-deck','','spiking')]:
    p='items/tools/'+fn+'.yml'; d=L(p); d['system']['type']={'value':typ,'baseItem':key}; d['system']['proficient']=None; D(p,d)
# ---- Hyperpad item
d=L('items/tools/spiking-deck.yml'); hid=mkid('r7:hyperpad'); d['_id']=hid; d['_key']='!items!'+hid; d['name']='Hyperpad'
d['system']['identifier']='hyperpad'; d['system']['type']={'value':'','baseItem':'spiking'}
d['system']['description']['value']='<p>An extremely advanced portable computer continuously linked to the Hypergrid. It is the Gridrunner’s spellbook and Spellcasting Focus: Gridrunners must use their hyperpad to cast spells.</p><p>From Gridrunner level 2 (Grid Spiker), the hyperpad also functions as a Spiking Deck and as the tool you chose for Grid Spiker.</p>'
d['system']['weight']={'value':2,'units':'lb'}; d['system']['price']={'value':0,'denomination':'gn'}
D('items/tools/hyperpad.yml',d); HYPER=IU+hid
# ---- Gridrunner class: Spiking Deck proficiency + Hyperpad and Spiking Deck at level 1
p='classes/gridrunner/gridrunner.yml'; d=L(p); adv=d['system']['advancement']
ti,ta=trait('grtool',1,'Tool Proficiencies',['tool:spiking']); adv[ti]=ta
gi,ga=grant('grgear',1,'Hyperpad and Spiking Deck',[HYPER,IU+'Rt7adqDDyIE4taqD']); adv[gi]=ga; D(p,d)
p='features/gridrunner/class-features/grid-spiker-2.yml'; d=L(p)
ti,ta=trait('gridspiker',2,'Grid Spiker',choices=[{'count':1,'pool':['tool:bypass','tool:art:electronics','tool:forg']}]); d['system']['advancement']={ti:ta}; D(p,d)
# ---- Hypergrid Override: Grid Surf (Plane Shift / Teleport always prepared, one free cast per Long Rest)
p='features/gridrunner/class-features/hypergrid-override-20.yml'; d=L(p)
spc_cfg=copy.deepcopy(next(iter(L('features/enforcer/arbiter/arbiter-spells-3.yml')['system']['advancement'].values()))['configuration']['spell'])
gi,ga=grant('gridsurf',20,'Grid Surf',[P24+'phbsplPlaneShift',P24+'phbsplTeleport00']); ga['configuration']['spell']=spc_cfg; d['system']['advancement']={gi:ga}
setuses(d,1,'lr'); acts=dict(d['system']['activities'])
for tag,nm,u in [('gsps','Grid Surf: Plane Shift','phbsplPlaneShift'),('gstp','Grid Surf: Teleport','phbsplTeleport00')]:
    i,a=cast(d,tag,nm,P24+u,7,cons=iu()); a['spell']['properties']=['vocal','somatic']; acts[i]=a
d['system']['activities']=acts; D(p,d)
# ---- Virus
V='features/gridrunner/virus/'
p=V+'malware-3.yml'; d=L(p)
mw=eff(d,'Malware',[],'malware',statuses=['malware'],duration=mins(1),
  desc='<p>Infected with Malware: subtract 1d6 from the next D20 Test within 1 minute. The effect is removed automatically after that roll.</p>')
d['effects']=[mw]; i,a=act(d,'mw','utility','Malware','bonus','You deal damage to a creature with a spell cast using a spell slot',rng={'units':'ft','value':'','override':False,'special':'The damaged creature'},target=one(),effects=[mw['_id']],duration=MIN(1))
setacts(d,[(i,a)]); D(p,d)
p=V+'junk-data-6.yml'; d=L(p)
for e in d['effects']: e['duration']=turn(); e['duration']['expiry']='turnStart'
a=first(d); a['name']='Junk Data'; a['activation']=spc('When you use Malware'); a['target']=one(); a['damage']['onSave']='none'; D(p,d)
p=V+'contagious-code-10.yml'; d=L(p); noacteff(d,['Unconscious']); a=first(d); a['name']='Contagious Code'; D(p,d)
p=V+'lethal-strain-14.yml'; d=L(p); a=first(d); a['name']='Lethal Strain'; a['range']=ft(100); a['target']=one('creature','2')
a['damage']['parts'][0]['scaling']={'mode':'whole','number':1,'formula':''}; a['consumption']['scaling']={'allowed':True,'max':'10'}; D(p,d)
# ---- Gorgonite: one Gorgon's Gaze item with Beam / Hypnotic / Petrifying buttons
G='origins/species-traits/gorgonite/'
p=G+'gorgons-gaze.yml'; d=L(p)
ch=eff(d,'Charmed',[],'gzch',statuses=['charmed'],duration=mins(1),desc='<p>Charmed by Gorgon’s Gaze. Ends if you or your allies damage it or force it to make a saving throw; it is then immune to your gaze for 24 hours.</p>')
rs=eff(d,'Restrained (Petrifying Gaze)',[],'gzrs',statuses=['restrained'],duration=mins(1),desc='<p>Partially turned to stone. Repeats the Constitution save at the end of each of its turns, ending the effect on a success.</p>')
d['effects']=[ch,rs]; DC={'calculation':'cha','formula':''}; L3=[]
for tag,nm,ab,ef in [('beam','Beam','dex',None),('hyp','Hypnotic','wis',ch),('pet','Petrifying','con',rs)]:
    i,a=act(d,tag,'save',f"Gorgon's Gaze: {nm}",'bonus','',iu(),rng=ft(30),target=one(),effects=[ef['_id']] if ef else ())
    svdc(a,ab,copy.deepcopy(DC))
    if tag=='beam': dmg(a,[dpart(None,None,['necrotic'],'(1 + floor((@details.level + 1) / 6))d6')],'half')
    else: dmg(a,[])
    L3.append((i,a))
setacts(d,L3)
d['system']['description']['value']+='<p><em>Click Beam, Hypnotic or Petrifying to use the gaze. When you add the species you choose Intelligence, Wisdom or Charisma for the save DC.</em></p>'; D(p,d)
p='origins/species/gorgonite.yml'; d=L(p)
for a in d['system']['advancement'].values():
    if a['type']=='ItemGrant': a['configuration']['items']=[x for x in a['configuration']['items'] if not x['uuid'].endswith(('lqNqrPUt1Q3N5ZWB','1nyY0CWQ3FkxRQ5A','dDxDCnR1lxDPPDtM'))]
    if a['type']=='Trait' and a['configuration'].get('choices'): a['configuration']['choices'][0]['pool']=['skills:ins','skills:prc','skills:sur']
D(p,d)
p=G+'toxin-resistant.yml'; d=L(p)
d['effects']=[eff(d,'Toxin Resistant',[chg('system.traits.dr.value','poison','add')],'toxres',transfer=True,desc='<p>Resistance to Poison damage.</p>'),
  eff(d,'Toxin Resistant: Advantage vs Poisoned',[chg('system.abilities.con.save.roll.mode','1','add')],'toxadv',transfer=True,disabled=True,
      desc='<p>Advantage on Constitution saves. Turned on automatically while you are Poisoned (to end it); turn it on yourself when saving to avoid being Poisoned.</p>')]
D(p,d)
print('round7 done')
