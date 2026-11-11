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
# ================= ROUND 8: VEHICLES =================
VD='bestiary/vehicles/'; CPB='@flags.neon-odyssey.crewPB'
def vitem(aid,base,name,desc,acts=(),effects=(),uses=None):
    it=copy.deepcopy(base); iid=mkid(f'r8v:{aid}:{name}'); it['_id']=iid; it['_key']=f'!actors.items!{aid}.{iid}'; it['name']=name
    it['system']['type']={'value':'vehicle','subtype':''}; it['system']['description']={'value':desc,'chat':''}; it['system']['activities']={}
    it['system']['uses']={'max':'','spent':0,'recovery':[]}; it['effects']=list(effects); it['system']['identifier']=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
    d={'_id':iid}
    for spec in acts:
        i,a=spec(d) if callable(spec) else spec; it['system']['activities'][i]=a
    if uses: it['system']['uses']=uses
    for e in it['effects']: e['_key']=f'!actors.items.effects!{aid}.{iid}.{e["_id"]}'
    return it,d
def u(d,tag,name,act_='action',cond='',flavor=''): return act(d,tag,'utility',name,act_,cond,flavor=flavor)
def wpn(d,tag,name,kind,abil,dice,typ,rng,flatbonus=None,cons=None):
    i,a=act(d,tag,'attack',name,'action','',cons,rng=rng,target=one())
    atk(a,kind,'weapon',abil,[dpart(dice[0],dice[1],[typ],None,'@mod' if flatbonus is None else str(flatbonus))]); a['attack']['bonus']=CPB
    return i,a
def chk(d,tag,name,abil,skill=None,dc=None,flavor=''):
    i,a=act(d,tag,'check',name,'action','',flavor=flavor); a['check']={'ability':abil,'associated':[skill] if skill else [],'dc':{'calculation':'','formula':str(dc) if dc else ''}}; return i,a
def react(name,cond,flavor): return lambda d: act(d,'r','utility',name,'reaction',cond,flavor=flavor)
def controls(name='Controls',extra=()):
    def f(aid,base):
        return vitem(aid,base,name,'<p>Drive or pilot the vehicle (requires 1 crew). The driver can use its movement to move the vehicle up to its Speed, and its action to make the vehicle Dash, Disengage, Dodge or Hide, or Attack with weapons operated from the Controls.</p>',
          [lambda d: u(d,'eng','Start / Stop Engine','bonus'),lambda d: u(d,'dash','Dash'),lambda d: u(d,'dis','Disengage'),lambda d: u(d,'dodge','Dodge'),lambda d: u(d,'hide','Hide')]+list(extra))[0]
    return f
def stunt(d): return chk(d,'stunt','Stunt (DC 10)','dex',None,10,'Fail by 5 or more: the bike and riders become Prone and stop.')
def comms(aid,base):
    return vitem(aid,base,'Signal Intercept','<p>Operate the vehicle’s communications and sensors (requires 1 crew).</p>',
      [lambda d: chk(d,'jam','Jam Comms','cha','cmp',None,'Record the total: enemy vehicles within 1 mile must beat it on a vehicle Charisma save to communicate.'),
       lambda d: chk(d,'mal','Malware Strike','int','cmp',None,'Target vehicle with Int makes a vehicle Int save vs your total or has Disadvantage on checks, attacks or saves (your choice) for 1 minute.'),
       lambda d: chk(d,'srch','Sensors: Search','wis','cmp'),lambda d: chk(d,'scan','Sensors: Scan (DC 10, Advantage)','wis','cmp',10)])[0]
SV=[('Speeder','speeder.yml'),('Racing Bike','racing-bike.yml'),('Cruising Bike','cruising-bike.yml'),('Cargo Hauler','cargo-hauler.yml'),('Defense Airspeeder','defense-airspeeder.yml'),('Armored Enforcement Walker','armored-enforcement-walker.yml')]
for name,fn in SV:
    p=VD+fn; A=L(p); aid=A['_id']; base=copy.deepcopy(A['items'][0]); old={i['name']:i for i in A['items']}
    keep=lambda n: (lambda it: (it.update({'system':{**it['system'],'type':{'value':'vehicle','subtype':''}}}) or it))(copy.deepcopy(old[n]))
    items=[]
    cls='lightMech' if 'Walker' in name else 'lightPlanetary'
    A.setdefault('flags',{}).setdefault('neon-odyssey',{})['vehicleClass']=cls
    for n in ['Prone Deficiency','Jump','Cargo Bay','Servo-Assist Targeting']:
        if n in old: items.append(keep(n))
    if 'Stunt' in old:
        it,_=vitem(aid,base,'Stunt',old['Stunt']['system']['description']['value'],[stunt]); items.append(it)
    if name=='Cargo Hauler':
        it,_=vitem(aid,base,'Towing','<p>The hauler can tow 25,000 lb. of weight using its Mag Cable or a hitched trailer. While towing weight beyond its Cargo Capacity, it has Advantage on Strength saving throws and Disadvantage on Dexterity saving throws.</p>'); items.append(it)
        items.append(controls()(aid,base))
        ce={'_id':mkid(f'r8v:{aid}:magfx'),'name':'Mag Cable Attached','img':base.get('img'),'type':'base','system':{'changes':[]},'disabled':False,'transfer':False,'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},
            'description':'<p>Can’t move beyond the cable length. An attached creature or driver can use an action for a DC 15 vehicle Strength save to detach.</p>','tint':'#ffffff','statuses':[],'sort':0,'flags':{},'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats()}
        def mag(d):
            i,a=act(d,'mag','attack','Mag Cable','action','Requires open Cargo Bay',rng={'units':'ft','value':'15','override':False,'special':''},target=one(),effects=[ce['_id']])
            atk(a,'melee','weapon','str',[]); a['attack']['bonus']=CPB; return i,a
        it,_=vitem(aid,base,'Mag Cable',old['Mag Cable']['system']['description']['value'],[mag,lambda d: u(d,'ret','Retract / Extend / Detach Cable','bonus')],effects=[ce]); items.append(it)
    elif name=='Armored Enforcement Walker':
        pr={'_id':mkid(f'r8v:{aid}:prone'),'name':'Prone','img':base.get('img'),'type':'base','system':{'changes':[]},'disabled':False,'transfer':False,'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},'description':'<p>Large or smaller targets only.</p>','tint':'#ffffff','statuses':['prone'],'sort':0,'flags':{},'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats()}
        nr={'_id':mkid(f'r8v:{aid}:norx'),'name':'No Reactions','img':base.get('img'),'type':'base','system':{'changes':[]},'disabled':False,'transfer':False,'duration':rnd(1),'description':'<p>Can’t take Reactions until the end of the walker’s next turn.</p>','tint':'#ffffff','statuses':[],'sort':0,'flags':{},'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats()}
        def crush(d):
            i,a=wpn(d,'crush','Crushing Strike','melee','str',(1,8),'bludgeoning',{'units':'ft','value':'5','override':False,'special':''}); a['effects']=[RID(pr)]; return i,a
        def frag(d):
            i,a=act(d,'frag','save','Frag Grenade','action','',[{'type':'activityUses','value':'1','target':'','scaling':{}}],rng=ft(150),target=area('sphere',20)); svdc(a,'dex',{'calculation':'','formula':'15'}); dmg(a,[dpart(4,6,['piercing'])],'half')
            a['uses']={'spent':0,'recovery':[],'max':'4'}; return i,a
        def smoke(d):
            i,a=act(d,'smoke','utility','Smoke Grenade','action','',[{'type':'activityUses','value':'1','target':'','scaling':{}}],rng=ft(150),target=area('sphere',20),flavor='Heavily Obscured for 1 minute or until strong wind disperses it.')
            a['uses']={'spent':0,'recovery':[],'max':'4'}; return i,a
        items.append(controls()(aid,base))
        for nm,spec,ef in [('Crushing Strike',crush,[pr]),('Repeating Lasers',lambda d: wpn(d,'las','Repeating Lasers','ranged','str',(2,10),'radiant',{'units':'ft','value':'200','long':'800','override':False,'special':''}),[])]:
            it,_=vitem(aid,base,nm,old[nm]['system']['description']['value'],[spec],effects=ef); items.append(it)
        it,_=vitem(aid,base,'Grenade Launcher','<p>Fire a grenade at a point within 150 feet. Frag Grenade (4): DC 15 Dex save, 20-ft-radius Sphere, 4d6 Piercing (half on success). Smoke Grenade (4): 20-ft-radius Sphere of smoke, Heavily Obscured for 1 minute.</p>',[frag,smoke]); items.append(it)
        def supp(d):
            i,a=act(d,'supp','save','Assault Suppression','reaction','The walker is hit by a melee attack roll (requires pilot)',target=one(),effects=[nr['_id']]); svdc(a,'dex',{'calculation':'','formula':'14'}); dmg(a,[dpart(2,8,['lightning'])],'half'); return i,a
        it,_=vitem(aid,base,'Assault Suppression',old['Assault Suppression']['system']['description']['value'],[supp],effects=[nr]); items.append(it)
    elif name=='Defense Airspeeder':
        items.append(controls(extra=[lambda d: wpn(d,'lmg','Light Machine Guns','ranged','dex',(2,10),'piercing',{'units':'ft','value':'200','long':'800','override':False,'special':''})])(aid,base))
        it,_=vitem(aid,base,'Light Machine Guns',old['Light Machine Guns']['system']['description']['value'],[lambda d: wpn(d,'lmg','Light Machine Guns','ranged','dex',(2,10),'piercing',{'units':'ft','value':'200','long':'800','override':False,'special':''})]); items.append(it)
        items.append(comms(aid,base))
    else:
        items.append(controls()(aid,base))
    for rn,cond in [('Agile Dodge','The driver makes a vehicle Dexterity saving throw while the bike can move'),('Stabilize','The driver makes a vehicle Strength or Constitution saving throw'),('Juke','The driver makes a vehicle Dexterity saving throw')]:
        if rn in old:
            it,_=vitem(aid,base,rn,old[rn]['system']['description']['value'],[react(rn,cond,'The driver has Advantage on the triggering save.')]); items.append(it)
    A['items']=items; D(p,A)
# ---- starfighters from the old playtest
src=L(VD+'speeder.yml'); 
for name,cls,tok in [('Superiority Fighter','standardStarfighter',None),('Interceptor','lightStarfighter',None)]:
    A=copy.deepcopy(src); aid=mkid('vehicle:'+name); A['_id']=aid; A['_key']=f'!actors!{aid}'; A['name']=name; s=A['system']; base=copy.deepcopy(src['items'][0])
    sup=name=='Superiority Fighter'
    s['details']['type']='space'; s['traits']['size']='tiny'; s['identifier']=re.sub(r'[^a-z0-9]+','-',name.lower())
    for k,v in zip(['str','dex','con','int','wis','cha'],[16,16,14,10,14,10] if sup else [14,18,12,10,10,10]): s['abilities'][k]['value']=v
    s['attributes']['ac']={'flat':22 if sup else 23,'calc':'flat','motionless':'19 while stationary'}
    s['attributes']['hp'].update(value=90 if sup else 50,max=90 if sup else 50,temp=30,tempmax=0,dt=20 if sup else 15,mt=30 if sup else 20)
    s['attributes']['movement']={'units':'ft','hover':True,'ignoredDifficultTerrain':[],'fly':5000 if sup else 6000,'walk':0}
    s['attributes']['travel']={'units':'mph','paces':{},'speeds':{'air':900 if sup else 1100},'time':24}
    s['attributes']['capacity']={'creature':'2' if sup else '1','cargo':{'value':0.1 if sup else 0.05,'units':'tn'}}
    s['details']['biography']={'value':f"<p>{'Superiority fighters are larger, all-around vessels: close dogfights, long-range torpedo support against bulkier craft, and robust sensors for patrol or scouting.' if sup else 'Interceptors are fast, agile starfighters for fast strikes against fighters, weapon emplacements or ground vehicles, and ideal for destroying incoming missiles and torpedoes.'}</p><p><strong>Class</strong> {'Standard' if sup else 'Light'} Starfighter (Tiny Starship). <strong>Crew</strong> {'1–2' if sup else '1'}. <strong>Initiative</strong> {'+3' if sup else '+4'} plus PB. <strong>Power Dice</strong> {'4d6' if sup else '3d6'}. <strong>SP</strong> 30 (Damage Threshold {20 if sup else 15}) — Shield Points are the Temporary HP. <strong>Speed</strong> Fly {10 if sup else 12} hexes (500 ft per hex in atmosphere). <strong>Sensors</strong> 50 hexes; Passive Perception {12 if sup else 10} plus crew’s PB.</p><p><em>From the earlier Neon Odyssey playtest (starship rules).</em></p>",'public':''}
    A.setdefault('flags',{})['neon-odyssey']={'vehicleClass':cls,'shieldMax':30}
    H=lambda n:{'units':'ft','value':str(n*500),'long':str(n*2000),'override':False,'special':f'{n}/{n*4} hexes'}
    items=[]
    dis={'_id':mkid(f'r8v:{aid}:dis'),'name':'Torpedo/Missile Hit','img':base.get('img'),'type':'base','system':{'changes':[]},'disabled':False,'transfer':False,'duration':rnd(1),'description':'<p>Disadvantage on '+('D20 Tests' if sup else 'attack rolls')+' until the start of the starfighter’s next turn.</p>','tint':'#ffffff','statuses':[],'sort':0,'flags':{},'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats()}
    def missile(d,sup=sup,dis=dis):
        i,a=act(d,'msl','attack','Pulse Torpedo' if sup else 'Flare Missile','action','',[{'type':'activityUses','value':'1','target':'','scaling':{}}],rng=H(5),target=one(),effects=[dis['_id']])
        atk(a,'ranged','weapon','none',[dpart(9 if sup else 6,10,['thunder' if sup else 'fire'],None,'')]); a['attack']['flat']=True; a['attack']['bonus']='8' if sup else '12'; a['uses']={'spent':0,'recovery':[],'max':'2' if sup else '4'}; return i,a
    gun=lambda d,sup=sup: wpn(d,'gun','Laser Cannons' if sup else 'Burst Cannon','ranged','dex',(5 if sup else 4,10),'radiant',H(5),4)
    items.append(controls()(aid,base))
    it,_=vitem(aid,base,'Laser Cannons' if sup else 'Burst Cannon','<p>Martial Weapon, Front. Ranged Attack Roll: +'+('3' if sup else '4')+' plus crew’s PB, range 5/20 hexes. Hit: '+('5d10 + 4' if sup else '4d10 + 4')+' Radiant damage.</p>',[gun]); items.append(it)
    it,_=vitem(aid,base,'Pulse Torpedo' if sup else 'Flare Missile','<p>Front; '+('2' if sup else '4')+' missiles. Fires at a target on its sensors; when it enters the target’s space it attacks. Miss: it keeps tracking and can attack again on the starfighter’s next turn.</p>',[missile],effects=[dis]); items.append(it)
    it,_=vitem(aid,base,'Sensors','<p>Operate the starfighter’s sensors (requires 1 crew).</p>'+('<p><strong>Sensor Sweep.</strong> While the sensors aren’t Passive, the starfighter has Blindsight 5 hexes.</p>' if sup else ''),[lambda d: chk(d,'srch','Sensors: Search','wis','cmp'),lambda d: chk(d,'scan','Sensors: Scan (DC 10, Advantage)','wis','cmp',10)]); items.append(it)
    it,_=vitem(aid,base,'Shields','<p>Shield Points (30) are tracked as Temporary Hit Points and absorb damage first. They have their own Damage Threshold. After 1 minute without taking damage they return to maximum.</p>',[lambda d: (lambda ia: (ia[1].__setitem__('healing',heal('30','temphp')), ia)[1])(act(d,'shr','heal','Restore Shield Points','special','1 minute without taking damage'))]); items.append(it)
    if not sup:
        it,_=vitem(aid,base,'Fine Targeting','<p>The Burst Cannon can target creatures and objects that are Huge or smaller.</p>'); items.append(it)
        it,_=vitem(aid,base,'Jink','<p>Trigger: the starfighter is hit by an attack roll from its front fire arc. Response: +5 AC against that attack.</p>',[react('Jink','Hit by an attack roll originating in the front fire arc','The pilot adds +5 to AC against that attack.')]); items.append(it)
    A['items']=items; A['prototypeToken']['name']=name; A['prototypeToken']['width']=1; A['prototypeToken']['height']=1
    D(VD+s['identifier']+'.yml',A)
print('round8 vehicles done')
# ---- per-vehicle art
import glob as _g
for f in _g.glob(os.path.join(OUT,VD,'*.yml')):
    if f.endswith('_folder.yml'): continue
    A=yaml.safe_load(open(f)); k=A['system'].get('identifier') or os.path.basename(f)[:-4]
    if os.path.exists(f'/home/ubuntu/work/neon-odyssey/icons/vehicles/{k}.webp'):
        A['img']=f'modules/neon-odyssey/icons/vehicles/{k}.webp'; A['prototypeToken']['texture']['src']=f'modules/neon-odyssey/icons/vehicles/{k}-token.webp'
        yaml.safe_dump(A,open(f,'w'),sort_keys=False,allow_unicode=True,width=200)
print('round8 art done')
