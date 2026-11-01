import sys,os,copy,yaml; sys.path.insert(0,'.')
from common import OUT,uuid,stats
from autoact import mkid
def L(p): return yaml.safe_load(open(os.path.join(OUT,p)))
def D(p,d): yaml.safe_dump(d,open(os.path.join(OUT,p),'w'),sort_keys=False,allow_unicode=True,width=200)
VIS={'level':{'min':None,'max':None},'identifier':'','requireAttunement':False,'requireIdentification':False,'requireMagic':False}
def act(d,tag,typ,name,activation='action',cond='',cons=None,rng=None,target=None,effects=(),**extra):
    i=mkid(d['_id']+':fg:'+tag)
    a={'_id':i,'type':typ,'name':name,'img':'','sort':0,'activation':{'type':activation,'value':None,'override':False,'condition':cond},
       'consumption':{'scaling':{'allowed':False,'max':''},'spellSlot':False,'targets':cons or []},'description':{'chatFlavor':''},
       'duration':{'units':'inst','concentration':False,'override':False,'value':'','special':''},
       'effects':[{'_id':e,'riders':{'activity':[],'effect':[],'item':[]}} for e in effects],
       'range':rng or {'units':'self','override':False,'special':''},
       'target':target or {'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'','type':'self'},'override':False,'prompt':False},
       'uses':{'spent':0,'recovery':[],'max':''},'flags':{},'visibility':copy.deepcopy(VIS),'behaviors':[]}
    a.update(extra); return i,a
def uses(n,tgt=''): return [{'type':'itemUses','value':str(n),'target':tgt,'scaling':{}}]
def dpart(n,f,types,custom=None,bonus=''):
    return {'number':n,'denomination':f,'bonus':bonus,'types':list(types),'custom':{'enabled':bool(custom),'formula':custom or ''},'scaling':{'mode':'','number':None,'formula':''}}
def ft(n,override=True): return {'value':str(n),'units':'ft','special':'','override':override}
def one(kind='creature'): return {'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'1','type':kind},'override':False,'prompt':False}
def area(typ,size,width=''): return {'template':{'contiguous':False,'units':'ft','type':typ,'size':str(size),'width':str(width),'count':'','stationary':False},'affects':{'choice':True,'count':'','type':'creature'},'override':False,'prompt':True}
def attack(kind,cls,ability=''): return {'ability':ability,'bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':kind,'classification':cls}}

# ---------- Weapon Protocols ----------
P='features/soldier/commando/weapon-protocols-3.yml'; d=L(P); s=d['system']
s['uses']={'max':'min(6, floor((@classes.soldier.levels + 3) / 4) + 1)','spent':0,'recovery':[{'period':'sr','type':'recoverAll'},{'period':'lr','type':'recoverAll'}]}
T10='floor(min(@classes.soldier.levels, 10) / 10)'; MOD='max(@abilities.str.mod, @abilities.dex.mod)'
A=[]
i,a=act(d,'plasma','damage','Plasma Charge','bonus',cons=uses(1),target=one()); a['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(None,None,['lightning'],f'(1 + {T10})d8 + {MOD}')]}
a['description']['chatFlavor']='Move up to half your Speed; once during this movement, deal this damage to a creature you move within 5 feet of (2d8 and no Opportunity Attacks from Soldier level 10).'; A.append((i,a))
i,a=act(d,'resolve','utility','Resolve Breaker','bonus',cons=uses(1),target=one()); a['roll']={'formula':f'1d(6 + 2 * {T10})','name':'Penalty die','prompt':False,'visible':True}
a['description']['chatFlavor']='Make an attack with the weapon. On a hit, the target subtracts this die from its next attack roll or saving throw before the end of your next turn.'; A.append((i,a))
i,a=act(d,'resolve10','damage','Resolve Breaker: Extra Force','special',target=one()); a['damage']={'critical':{'allow':True,'bonus':''},'parts':[dpart(1,8,['force'])]}
a['visibility']['identifier']='soldier'; a['visibility']['level']['min']=10; A.append((i,a))
i,a=act(d,'rocket','save','Rocket Launch','bonus',cons=uses(1),rng=ft(120),target=area('sphere',f'5 + 10 * {T10}'))
a['save']={'ability':['dex'],'dc':{'calculation':'','formula':f'8 + {MOD} + @prof'}}; a['damage']={'onSave':'half','parts':[dpart(None,None,['fire'],f'(2 + {T10})d6')]}; A.append((i,a))
i,a=act(d,'suppress','damage','Suppressive Fire','bonus',cons=uses(1),rng=ft(120),target=area('cube',f'10 + 10 * {T10}'))
a['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(None,None,['lightning'],f'1d(8 + 2 * {T10})')]}
a['duration']={'units':'turn','value':'1','concentration':False,'override':False,'special':'Until the start of your next turn'}
a['description']['chatFlavor']='Creatures in the Cube have Disadvantage on attack rolls. A creature takes this damage for every 5 feet it moves into or within the Cube.'; A.append((i,a))
s['activities']={i:a for i,a in A}; D(P,d)

# ---------- Warzone Supremacy ----------
P='features/soldier/class-features/warzone-supremacy-20.yml'; d=L(P)
i,a=act(d,'dread','utility','Dreadnought','reaction',cond='When you are hit by an attack roll and take damage',cons=uses(1,'feat:frontline-rally'))
a['roll']={'formula':'1d10 + @classes.soldier.levels','name':'Damage reduced','prompt':False,'visible':True}
a['description']['chatFlavor']='Reduce the damage by the rolled amount. If you reduce it to 0, the attack misses you instead.'
d['system']['activities']={i:a}; D(P,d)

# ---------- Saurian natural weapon (as a weapon) + Sharptooth Feeding Bite ----------
SA='origins/species-traits/saurian/'
nw=L(SA+'natural-weapon.yml'); tmpl=L('origins/species-traits/zorbrak/scything-claws-weapon.yml')
w=copy.deepcopy(tmpl); w['_id']=nw['_id']; w['name']='Natural Weapon'; w['img']=nw['img']; w['folder']=nw['folder']; w['_key']=f"!items!{nw['_id']}"
w['system']['description']=nw['system']['description']; w['system']['identifier']='saurian-natural-weapon'; w['system']['source']=nw['system']['source']
w['system']['damage']['base'].update({'number':1,'denomination':6,'types':['piercing','slashing','bludgeoning']}); w['system']['properties']=[]
aid=mkid(nw['_id']+':fg:nwatk'); old=next(iter(w['system']['activities'].values())); old['_id']=aid; w['system']['activities']={aid:old}
w['_stats']=stats(); D(SA+'natural-weapon.yml',w)
P=SA+'lineage-sharptooth.yml'; d=L(P); s=d['system']
s['uses']={'max':'1','spent':0,'recovery':[{'period':'sr','type':'recoverAll'},{'period':'lr','type':'recoverAll'}]}
A=[]
i,a=act(d,'bite','attack','Bite (Bonus Action)','bonus',rng={'units':'ft','value':'5','special':'','override':True},target=one())
a['attack']=attack('melee','unarmed','str'); a['damage']={'critical':{'bonus':''},'includeBase':False,'parts':[dpart(1,6,['piercing'],bonus='@mod')]}; A.append((i,a))
i,a=act(d,'feeddmg','damage','Feeding Bite: Extra Damage','special',cond='When you hit a creature with your bite',cons=uses(1),target=one())
a['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(None,None,['piercing'],'@prof')]}; A.append((i,a))
i,a=act(d,'feedheal','heal','Feeding Bite: Regain Hit Points','special',cond='After dealing Feeding Bite extra damage')
a['healing']=dpart(None,None,['healing'],'@abilities.con.mod + @prof'); A.append((i,a))
s['activities']={i:a for i,a in A}; D(P,d)

# ---------- Rivet Turret ----------
P='bestiary/summons/rivet-turret.yml'; d=L(P); sy=d['system']
sy['attributes']['ac']={'flat':17,'calc':'natural'}; sy['attributes']['hp'].update({'value':5,'max':5})
sy['attributes']['movement'].update({'walk':'0','fly':'60','hover':True})
sy['traits']['size']='sm'; sy['traits'].setdefault('dr',{})['value']=['necrotic']; sy['traits'].setdefault('di',{})['value']=['poison','psychic']
sy['details']['type']={'value':'construct','subtype':'Object','custom':''}
sy['details']['biography']['value']=('<p>Small Object created by the Riveter Machinist\u2019s Deploy Turret feature. Hit Points: 5 \u00d7 your Machinist level '
  '(casting Mending on the turret restores 2d6 Hit Points to it). It collapses into scrap at 0 Hit Points, after 1 hour, or if you dismiss it as a Magic action.</p>')
ICON={'Activate Turret':'i-robot-cyan','Flash Charge':'i-crosshairs-pink','Rivet Burst':'i-gun-orange','Plasma Arc':'i-bolt-lightning-cyan','Relocate':'i-gear-teal'}
def item(name,desc,acts,effects=(),activation='action'):
    iid=mkid(d['_id']+':fgitem:'+name)
    return {'_id':iid,'name':name,'type':'feat','img':f"modules/neon-odyssey/icons/neon/{ICON[name]}.webp",'effects':list(effects),'sort':0,
      'system':{'description':{'value':f'<p>{desc}</p>','chat':''},'type':{'value':'monster','subtype':''},'uses':{'max':'','spent':0,'recovery':[]},
        'activation':{'type':activation,'value':None,'condition':''},'activities':{i:a for i,a in acts},'properties':[],'requirements':'','identifier':name.lower().replace(' ','-')},
      '_key':f"!actors.items!{d['_id']}.{iid}",'_stats':stats()}
it=[]
dummy={'_id':d['_id']}
it.append(item('Activate Turret','Requires you to be within 60 feet of the turret. When you create the turret, or as a Bonus Action on your subsequent turns, you order the turret to use Flash Charge, Rivet Burst, Plasma Arc, or Relocate.',[],activation='bonus'))
fx=mkid(d['_id']+':fg:blindfx')
blind={'_id':fx,'name':'Flash Charge: Blinded','img':'systems/dnd5e/icons/svg/statuses/blinded.svg','type':'base','system':{'changes':[]},'disabled':False,'transfer':False,
  'duration':{'value':1,'units':'rounds','expiry':'turnStart','expired':False},'description':'<p>Blinded until the start of the turret creator\u2019s next turn.</p>','tint':'#ffffff',
  'statuses':['blinded'],'sort':0,'flags':{},'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats()}
dd={'_id':mkid(d['_id']+':fgitem:Flash Charge')}
i,a=act(dd,'flash','save','Flash Charge',rng=ft(60),target=one(),effects=[fx]); a['save']={'ability':['con'],'dc':{'calculation':'spellcasting','formula':''}}; a['damage']={'onSave':'none','parts':[]}
fl=item('Flash Charge','The turret fires a disorienting charge at a creature within 60 feet of it. The target must succeed on a Constitution saving throw against your spell save DC or have the Blinded condition until the start of your next turn.',[(i,a)])
blind['_key']=f"!actors.items.effects!{d['_id']}.{fl['_id']}.{fx}"; fl['effects']=[blind]; it.append(fl)
dd={'_id':mkid(d['_id']+':fgitem:Rivet Burst')}
i,a=act(dd,'rivet','attack','Rivet Burst',rng=ft(120),target=one()); a['attack']=attack('ranged','spell'); a['damage']={'critical':{'bonus':''},'includeBase':False,'parts':[dpart(2,6,['piercing'])]}
it.append(item('Rivet Burst','The turret fires a stream of rivets. Ranged spell attack against one creature or object within 120 feet of it. On a hit, the target takes 2d6 Piercing damage, and the next attack roll it makes before the start of your next turn has Disadvantage.',[(i,a)]))
dd={'_id':mkid(d['_id']+':fgitem:Plasma Arc')}
i,a=act(dd,'arc','save','Plasma Arc',target=area('line',30,5)); a['save']={'ability':['dex'],'dc':{'calculation':'spellcasting','formula':''}}; a['damage']={'onSave':'half','parts':[dpart(2,8,['lightning'])]}
it.append(item('Plasma Arc','The turret unleashes a 30-foot-long, 5-foot-wide Line of plasma. Each creature in that area makes a Dexterity saving throw against your spell save DC, taking 2d8 Lightning damage on a failed save or half as much on a success. Flammable objects in the Line that aren\u2019t worn or carried start burning.',[(i,a)]))
dd={'_id':mkid(d['_id']+':fgitem:Relocate')}
i,a=act(dd,'relocate','utility','Relocate')
it.append(item('Relocate','The turret flies up to 60 feet to an unoccupied space that you can see.',[(i,a)]))
d['items']=it; D(P,d)
P='features/machinist/riveter/deploy-turret-3.yml'; d=L(P)
for a in d['system']['activities'].values():
    if a['type']=='summon': a['bonuses']['hp']='5 * @classes.machinist.levels - 5'; a['activation']={'type':'bonus','value':None,'override':False,'condition':''}
D(P,d)
print('fix_gaps done')
