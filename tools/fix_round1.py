import sys,os,copy,yaml; sys.path.insert(0,'.')
from common import OUT,stats
from autoact import mkid
def L(p): return yaml.safe_load(open(os.path.join(OUT,p)))
def D(p,d): yaml.safe_dump(d,open(os.path.join(OUT,p),'w'),sort_keys=False,allow_unicode=True,width=200)
def chg(k,v,t,pr=None): return {'key':k,'value':str(v),'priority':pr,'type':t,'phase':'initial','_id':mkid(f'r1:{k}:{v}')}
def eff(d,name,changes,tag,transfer=False,disabled=False,statuses=(),desc='',duration=None):
    eid=mkid(d['_id']+':r1:'+tag)
    return {'_id':eid,'name':name,'img':d.get('img'),'type':'base','system':{'changes':changes},'disabled':disabled,'transfer':transfer,
      'duration':duration or {'value':None,'units':'seconds','expiry':None,'expired':False},'description':desc,'tint':'#ffffff','statuses':list(statuses),'sort':0,'flags':{},
      'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"}
VIS={'level':{'min':None,'max':None},'identifier':'','requireAttunement':False,'requireIdentification':False,'requireMagic':False}
def act(d,tag,typ,name,activation='action',cond='',cons=None,rng=None,target=None,effects=(),flavor='',minlvl=None,cls=None,**extra):
    i=mkid(d['_id']+':r1act:'+tag)
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
F='features/'
SL='@classes.soldier.levels'; MOD='max(@abilities.str.mod, @abilities.dex.mod)'; DC=f'8 + {MOD} + @prof'
SC10=f'(1 + min(1, floor({SL} / 10)))d8'

# ================= SOLDIER base =================
p=F+'soldier/class-features/adrenaline-rush-2.yml'; d=L(p); d['system']['uses']['recovery']=rec('sr','lr'); D(p,d)
p=F+'soldier/class-features/no-surrender-9.yml'; d=L(p)
setacts(d,[act(d,'reroll','utility','Reroll Failed Save','special','When you fail a saving throw',uses(1),roll=roll(f'1d20 + {SL}','Reroll (add your save modifier)'),flavor='Reroll the failed saving throw with a bonus equal to your Soldier level; you must use the new roll.')]); D(p,d)
p=F+'soldier/class-features/adaptive-arsenal-9.yml'; d=L(p)
for e in d['effects']: e['name']='Adaptive Arsenal'
D(p,d)

# ================= EXOMECH =================
p=F+'soldier/exomech/bonded-exosuit-3.yml'; d=L(p)
e1=eff(d,'Piloting Exosuit',[chg('system.traits.size','lg','override',20),chg('system.abilities.str.check.roll.mode',1,'add'),chg('system.abilities.str.save.roll.mode',1,'add')],'pilot',
       desc='<p>Hulking Form: Large, Advantage on Strength checks and saving throws, Unarmed Strikes deal 1d8 Bludgeoning.</p>')
d['effects']=[e1]
i1,a1=act(d,'pilot','utility','Enter / Exit Exosuit','special','Spend movement equal to half your Speed',effects=[e1['_id']],flavor='Apply Piloting Exosuit when you enter; delete it from the Effects tab when you exit.')
i2,a2=act(d,'slam','attack','Exosuit Unarmed Strike','action',rng={'units':'ft','value':'5','special':'','override':True},target=one())
a2['attack']={'ability':'str','bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':'melee','classification':'unarmed'}}
a2['damage']={'critical':{'bonus':''},'includeBase':False,'parts':[dpart(1,8,['bludgeoning'],bonus='@mod')]}
setacts(d,[(i1,a1),(i2,a2)]); D(p,d)

p=F+'soldier/exomech/specialized-chassis-3.yml'; d=L(p); setuses(d,f'max(1, {MOD})','lr')
ec=eff(d,'Comet Chassis',[chg('system.attributes.movement.walk',10,'add'),chg('flags.dnd5e.weaponCriticalThreshold',19,'downgrade')],'comet',transfer=True,disabled=True,
       desc='<p>Turn on while piloting a Comet exosuit: +10 ft Speed (Rocket Booster) and Critical Hits on 19-20 (Meteor Matrix, installed melee weapons).</p>')
d['effects']=[ec]
A=[act(d,'evade','utility','Bastion: Evasion Circuits (Dodge)','bonus',cons=uses(1),flavor='Take the Dodge action.'),
   act(d,'threat','utility','Bastion: Threat Attractor','special','When you hit a creature with an attack roll',target=one(),flavor='The marked target has Disadvantage on attack rolls against targets other than you until the start of your next turn.')]
i,a=act(d,'momentum','damage','Comet: Momentum Amplifier','special','Once per turn, hit with an installed melee weapon or Unarmed Strike',target=one()); a['damage']={'critical':{'allow':True,'bonus':''},'parts':[dpart(None,None,['force'],SC10)]}; A.append((i,a))
i,a=act(d,'battery','damage','Mortar: Plasma Battery','special','Once per turn, hit with an installed ranged weapon; another target within 15 ft',target=one()); a['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(None,None,['lightning'],SC10)]}; A.append((i,a))
setacts(d,A); D(p,d)

p=F+'soldier/exomech/experimental-systems-7.yml'; d=L(p); setuses(d,f'max(1, {MOD})','lr')
A=[act(d,'screen','utility','Bastion: Defensive Screen','special','When you use Evasion Circuits',uses(1),flavor='You and allies in a 10-foot Emanation have Half Cover until the start of your next turn.'),
   act(d,'rush','utility','Comet: Rocket Rush','bonus',cons=uses(1),flavor='Move up to your Speed without provoking Opportunity Attacks. Your next melee hit this turn can also apply Push or Topple.')]
i,a=act(d,'rockets','save','Mortar: Micro Rockets','special','Replace one attack of the Attack action',uses(1),target=area('cone',30))
a['save']={'ability':['dex'],'dc':{'calculation':'','formula':DC}}; a['damage']={'onSave':'half','parts':[dpart(4,6,['fire'])]}; A.append((i,a))
setacts(d,A); D(p,d)

p=F+'soldier/exomech/mobile-frame-10.yml'; d=L(p); setuses(d,1,'sr','lr')
e=eff(d,'Compression Form',[chg('system.traits.size','med','override',40)],'compress',duration=mins(1)); d['effects']=[e]
setacts(d,[act(d,'compress','utility','Compression Form','bonus',cons=uses(1),effects=[e['_id']],duration={'units':'minute','value':'1','concentration':False,'override':False,'special':''}),
           act(d,'jets','utility','Thruster Jets','special',flavor='Expend 10 feet of movement to jump up to 30 feet.')]); D(p,d)

p=F+'soldier/exomech/perfected-exosuit-15.yml'; d=L(p); setuses(d,1,'sr','lr')
setacts(d,[act(d,'crit','utility','Mortar: Force Critical Hit','special','When you hit with an attack roll',uses(1),flavor='The hit becomes a Critical Hit.')]); D(p,d)

p=F+'soldier/exomech/battle-assault-18.yml'; d=L(p); setuses(d,1,'lr')
e=eff(d,'Battle Assault',[],'assault',duration=turn(),desc='<p>Until the end of the turn, your hits deal maximum damage. At the end of your turn you gain 4 Exhaustion levels, which vanish at the end of your next turn or when you expend a Frontline Rally use.</p>'); d['effects']=[e]
setacts(d,[act(d,'assault','utility','Battle Assault','bonus',cons=uses(1),effects=[e['_id']])]); D(p,d)

# ================= COMMANDO =================
p=F+'soldier/commando/advanced-arsenal-10.yml'; d=L(p); d['system']['activities']={}; D(p,d)
p=F+'soldier/commando/armor-protocols-7.yml'; d=L(p)
i,a=act(d,'shield','heal','Energy Shield','special','When you don registered armor or finish a Short or Long Rest'); a['healing']=heal(f'1d8 + ceil({SL} / 2)','temphp')
setacts(d,[(i,a)]); D(p,d)
p=F+'soldier/commando/army-of-one-15.yml'; d=L(p)
d['effects']=[eff(d,'Unbreakable',[chg('system.traits.ci.value','frightened','add')],'unbreak',transfer=True)]
setacts(d,[act(d,'fervor','utility','Glorious Fervor','reaction','An enemy within 10 ft of you drops to 0 Hit Points',uses(-1,'feat:weapon-protocols'),flavor='Regain one expended use of Weapon Protocols.'),
           act(d,'pain','utility','Ignore Pain','special','When you activate Frontline Rally with a Bonus Action',flavor='Gain Resistance to one damage type of your choice until the start of your next turn.')]); D(p,d)
p=F+'soldier/commando/endless-war-18.yml'; d=L(p)
d['effects']=[eff(d,'Death Denied',[chg('system.attributes.death.roll.mode',1,'add')],'death',transfer=True)]; D(p,d)

# ================= NANOMEDIC =================
NM='feat:nanite-medicine'
p=F+'soldier/nanomedic/nanite-medicine-3.yml'; d=L(p); setuses(d,f'5 * {SL}','lr')
def pool(tag,name,typ,minlvl=None):
    i,a=act(d,tag,'heal',name,'action','Or in place of an attack',uses(1),rng=ft(f'30 + 30 * min(1, floor({SL} / 10))'),target=one(),minlvl=minlvl,cls='soldier')
    a['consumption']['scaling']={'allowed':True,'max':'@item.uses.value'}
    h=heal('1',typ); h['scaling']={'mode':'whole','number':None,'formula':'1'}; a['healing']=h
    a['description']['chatFlavor']='Scale the use up to spend more Hit Points from the cluster (1 point = 1 Hit Point).'
    return i,a
A=[pool('heal','Nanite Medicine: Heal','healing'),pool('stim','Nano-Stim: Temporary Hit Points','temphp',7),
   act(d,'poison','utility','Cure Poisoned (5 HP)','action',cons=uses(5),rng=ft(30),target=one(),flavor='Remove the Poisoned condition.'),
   act(d,'cureall','utility','Cure-All (5 HP)','special',cons=uses(5),rng=ft(30),target=one(),minlvl=7,cls='soldier',flavor='Remove Blinded, Deafened or Frightened.'),
   act(d,'triage','utility','Trauma Triage (5 HP)','special',cons=uses(5),rng=ft(60),target=one(),minlvl=10,cls='soldier',flavor='Remove Charmed, Paralyzed or Stunned.'),
   act(d,'linger','utility','Lingering Nanites','special','At the start of the target\u2019s next turn',minlvl=7,cls='soldier',flavor='The target can expend and roll one Hit Point Die and regain that many Hit Points.'),
   act(d,'sustain','utility','Sustaining Swarm (+5 HP)','special','When you expend an Adrenaline Rush use',uses(-5),minlvl=10,cls='soldier')]
i,a=act(d,'replen','utility','Rapid Replenishment','special','When you roll Initiative',[{'type':'hitDice','value':'1','target':'smallest','scaling':{}},{'type':'itemUses','value':'-5','target':'','scaling':{}}],minlvl=18,cls='soldier',
        flavor='Each Hit Point Die expended restores 5 Hit Points to the cluster. Use it once per die.'); A.append((i,a))
d['effects']=[]; setacts(d,A); D(p,d)
p=F+'soldier/nanomedic/battlefield-resuscitation-15.yml'; d=L(p); setuses(d,1,'lr')
i,a=act(d,'revivify','cast','Revivify','action',cons=uses(1))
a['spell']={'uuid':'Compendium.dnd5e.spells24.Item.phbsplRevivify00','challenge':{'override':True,'attack':None,'save':None},'properties':[],'spellbook':False,'ability':'wis','level':3}
i2,a2=act(d,'range','utility','Extend Range to 60 ft (Adrenaline Rush)','special',cons=uses(1,'feat:adrenaline-rush'))
setacts(d,[(i,a),(i2,a2)]); D(p,d)

# ================= TROOPER =================
p='classes/soldier/trooper.yml'; d=L(p); adv=d['system']['advancement']
def scale(ident,title,typ,sc):
    rid=mkid('trooper:'+ident); adv[rid]={'_id':rid,'type':'ScaleValue','level':0,'title':title,'hint':'','icon':None,'classRestriction':'','flags':{},
      'configuration':{'identifier':ident,'type':typ,'distance':{'units':''},'scale':sc},'value':{}}
scale('die','Tactical Die','dice',{'3':{'number':None,'faces':6},'10':{'number':None,'faces':8},'18':{'number':None,'faces':10}})
scale('dice','Tactical Dice','number',{'3':{'value':4},'7':{'value':5},'15':{'value':6}})
rid=mkid('trooper:negotiator'); adv[rid]={'_id':rid,'type':'Trait','level':3,'title':'Negotiator','hint':'','icon':None,'classRestriction':'','flags':{},
  'configuration':{'mode':'default','allowReplacements':True,'grants':[],'choices':[{'count':1,'pool':['skills:dec','skills:ins','skills:itm','skills:per']}]},'value':{'chosen':[]}}
D(p,d)
TD='@scale.trooper.die'; TL='feat:tactical-leader'
def tac(d,tag,name,flavor,activation='bonus',cond='',minlvl=None,r=True,target=None,n=1,src=TL):
    i,a=act(d,tag,'utility',name,activation,cond,uses(n,src),rng=ft(30),target=target or one('ally'),flavor=flavor,minlvl=minlvl,cls='soldier')
    if r: a['roll']=roll(TD,'Tactical Die')
    return i,a
p=F+'soldier/trooper/tactical-leader-3.yml'; d=L(p); setuses(d,'@scale.trooper.dice','sr','lr')
A=[tac(d,'adv','Advance','The ally can take a Reaction to move up to its Speed, adding the die to its AC against Opportunity Attacks this turn.',target=one('ally'),src=''),
   tac(d,'focus','Focus Fire','One ally adds the die to one attack roll, the other adds it to one damage roll, before the end of its next turn.',target=one('ally','2'),r=False,src=''),
   tac(d,'push','Push Through','Add the die to the ability check that uses a skill proficiency.','reaction','You or an ally within 30 ft makes a skill check',src='')]
i,a=act(d,'hold','heal','Hold Position','bonus',cons=uses(1),rng=ft(30),target=one('ally','2')); a['healing']=heal(f'{TD} + {TD}','temphp'); A.insert(2,(i,a))
setacts(d,A); D(p,d)
p=F+'soldier/trooper/squad-rapport-3.yml'; d=L(p)
setacts(d,[act(d,'help','utility','Facilitator: Help','bonus',flavor='Take the Help action.')]); D(p,d)
p=F+'soldier/trooper/decisive-action-7.yml'; d=L(p)
setacts(d,[tac(d,'morale','Bolster Morale','The target repeats the save against Charmed, Frightened or Stunned (DC 15 Wisdom if none), adding the die.'),
           tac(d,'counter','Counterattack','Reduce the damage by the number rolled. The next time the ally is attacked before the end of its next turn, it can react to attack the attacker with Advantage.','reaction','An ally within 30 ft takes damage'),
           tac(d,'medevac','Medevac','The target adds the number rolled to its AC and Death Saving Throws until the start of your next turn and regains an extra die of Hit Points the first time it heals.'),
           tac(d,'vault','Vault Over','The ally can boost a jump by the die.')]); D(p,d)
p=F+'soldier/trooper/tactical-commander-10.yml'; d=L(p)
setacts(d,[tac(d,'bombard','Bombard','One ally adds a die to an attack roll; one creature subtracts a die from a Dexterity save forced by another ally.',target=one('ally','2')),
           tac(d,'secure','Secure the Area','For 1 minute, one ally adds a die to Search checks and gains 10 ft Blindsight; the other adds a die to Initiative and Dexterity saves.','bonus','Or when you roll Initiative',target=one('ally','2'))]); D(p,d)
p=F+'soldier/trooper/lead-from-the-front-15.yml'; d=L(p)
setacts(d,[act(d,'regain','utility','Regain Tactical Die (Hit Die)','special','When you have no Tactical Dice left',[{'type':'hitDice','value':'1','target':'smallest','scaling':{}},{'type':'itemUses','value':'-1','target':TL,'scaling':{}}]),
           tac(d,'divert','Create Diversion','When one chosen ally deals damage before your next turn, the other can react to Hide, adding the die to Stealth.',target=one('ally','2')),
           tac(d,'cut','Cut Them Off','For 1 minute, the allies add the die to Opportunity Attacks; a hit reduces the target\u2019s Speed to 0.',target=one('ally','2'))]); D(p,d)
print('round1 soldier ok')

# ================= CRYPTIST =================
SPDC={'calculation':'spellcasting','formula':''}; SM='max(1, @attributes.spell.mod)'
def cast(d,tag,name,uuid,lvl,activation='action',cond='',cons=None):
    i,a=act(d,tag,'cast',name,activation,cond,cons)
    a['spell']={'uuid':uuid,'challenge':{'override':False},'properties':['vocal','somatic'],'spellbook':False,'ability':'','level':lvl}
    a['target']['prompt']=True; return i,a
P24='Compendium.dnd5e.spells24.Item.'; PNO='Compendium.neon-odyssey.spells.Item.'
def sv(a,abil,parts,on='none'):
    a['save']={'ability':[abil],'dc':dict(SPDC)}; a['damage']={'onSave':on,'parts':parts}
C=F+'cryptist/'
p=C+'cacophonous/invoke-cacophony-3.yml'; d=L(p); pe=next(e['_id'] for e in d['effects'] if 'poisoned' in e.get('statuses',[]))
R10=area('radius',10)
i1,a1=act(d,'entropy','damage','Entropy','reaction','You damage an enemy (or an enemy within 10 ft dies)',uses(1),target=R10,flavor='Targets\u2019 Speed is reduced by 10 feet until the end of their next turn.')
a1['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(1,6,['cold'])]}
i2,a2=act(d,'instinct','save','Instinct','reaction','You damage an enemy (or an enemy within 10 ft dies)',uses(1),target=R10,effects=[pe]); sv(a2,'con',[dpart(None,None,['acid'],SM)])
i3,a3=act(d,'progress','damage','Progress','reaction','You damage an enemy (or an enemy within 10 ft dies)',uses(1),target=R10,flavor='Targets can\u2019t take Reactions until the start of your next turn.')
a3['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(1,8,['lightning'])]}
i4,a4=act(d,'thrill','save','Thrill','reaction','You damage an enemy (or an enemy within 10 ft dies)',uses(1),target=R10,flavor='Failed targets must use a Reaction to move up to half their Speed in a direction you choose. Allies take no damage.'); sv(a4,'wis',[dpart(1,6,['psychic'])])
setacts(d,[(i1,a1),(i2,a2),(i3,a3),(i4,a4)]); D(p,d)
p=C+'cacophonous/mark-of-discord-6.yml'; d=L(p); setuses(d,1,'sr','lr')
e=eff(d,'Mark of Discord',[],'mark',duration=mins(1),desc='<p>Cursed: subtract 1d4 from D20 Tests and take 2d8 damage (discordant tone type) at the start of each turn.</p>'); d['effects']=[e]
i,a=act(d,'mark','save','Mark of Discord','action',cons=uses(1),rng=ft(60),target=one(),effects=[e['_id']],flavor='The use is only spent if the target fails; restore it on a success.'); a['save']={'ability':['wis'],'dc':dict(SPDC)}
a['duration']={'units':'minute','value':'1','concentration':False,'override':False,'special':''}
i2,a2=act(d,'markdmg','damage','Mark of Discord: Start of Turn','special','Start of the cursed creature\u2019s turn',target=one()); a2['damage']={'critical':{'allow':False,'bonus':''},'parts':[dpart(2,8,['cold','acid','lightning','psychic'])]}
setacts(d,[(i,a),(i2,a2)]); D(p,d)
p=C+'cacophonous/spreading-corruption-10.yml'; d=L(p); setuses(d,1,'lr')
d['effects']=[eff(d,f'Resistance: {t.title()} ({n})',[chg('system.traits.dr.value',t,'add')],'res'+t,transfer=True,disabled=True,desc='<p>Turn on the one for your discordant tone.</p>') for n,t in [('Entropy','cold'),('Instinct','acid'),('Progress','lightning'),('Thrill','psychic')]]
setacts(d,[cast(d,'hex','Hex (Reaction, free)',P24+'phbsplHex0000000',1,'reaction','A creature you can see within 90 ft damages you',uses(1))]); D(p,d)
p=C+'cacophonous/cacophonous-crescendo-14.yml'; d=L(p); setuses(d,1,'lr'); fe=next(e for e in d['effects'] if 'frightened' in e.get('statuses',[]))
asc=eff(d,'Discordant Ascension',[chg('system.attributes.ac.bonus','+2','add'),chg('system.traits.di.value','necrotic','add'),chg('system.details.type.value','fiend','override')],'asc',duration=mins(1),
        desc='<p>Fiend, +2 AC, Immunity to Necrotic and your tone\u2019s damage type (add it in Traits), change damage to Necrotic or your tone type ignoring Resistance.</p>')
d['effects']=[fe,asc]
i3,a3=act(d,'aura','save','Ascension: Terrifying Presence','special','An enemy starts its turn within 30 ft of you',target=one(),effects=[fe['_id']]); a3['save']={'ability':['wis'],'dc':dict(SPDC)}
setacts(d,[cast(d,'breach','Cacophony Breach: Summon Discordant',PNO+'Pyw3Re6DMQ9GdzsU',6,cons=uses(1)),
           act(d,'ascend','utility','Discordant Ascension','bonus',cons=uses(1),effects=[asc['_id']],duration={'units':'minute','value':'1','concentration':False,'override':False,'special':''}),(i3,a3)]); D(p,d)

p=C+'deepsworn/sign-of-annihilation-3.yml'; d=L(p); setuses(d,1,'lr')
e=eff(d,'Sign of Annihilation: -1 AC',[chg('system.attributes.ac.bonus','-1','add')],'ac',desc='<p>Apply once per failed save (max 5). Ends when the creature succeeds.</p>'); d['effects']=[e]
i,a=act(d,'save','save','Sign of Annihilation (start of turn)','special','Start of each turn of a creature cursed by your Hex',target=one(),effects=[e['_id']]); a['save']={'ability':['con'],'dc':dict(SPDC)}
i2,a2=act(d,'pen','utility','Consuming Annihilation (-1d6 saves)','special','The affected creature makes a saving throw',target=one(),minlvl=10,cls='cryptist',roll=roll('1d6','Subtract from save'))
setacts(d,[cast(d,'hex','Hex (free)',P24+'phbsplHex0000000',1,'bonus',cons=uses(1)),(i,a),(i2,a2)]); D(p,d)
p=C+'deepsworn/devour-the-metaphysical-6.yml'; d=L(p)
for a in d['system']['activities'].values(): a['activation'].update({'type':'special','condition':'You end a spell with Counterspell or Dispel Magic'}); a['name']='Devour the Metaphysical'
D(p,d)
for f in ['deepsworn/unraveled-mind-10.yml','deepsworn/consuming-annihilation-10.yml']:
    d=L(C+f); d['system']['activities']={}; D(C+f,d)
p=C+'deepsworn/inevitable-oblivion-14.yml'; d=L(p); setuses(d,1,'lr')
i,a=act(d,'lash','save','Inevitable Oblivion (per lash)','action',cons=uses(1),rng=ft(60),target=one('creature','4'),flavor='Up to four lashes; each lash that strikes a creature adds this damage. Expend a level 6+ Eldritch Revelation to use it again (+2d8 per level above 6 on one lash).')
sv(a,'dex',[dpart(2,8,['force'],bonus='10')]); setacts(d,[(i,a)]); D(p,d)

p=C+'shadowtongue/silent-proxy-6.yml'; d=L(p); setuses(d,1,'lr')
setacts(d,[cast(d,'animate','Animate Dead (free)',P24+'phbsplAnimateDea',3,cons=uses(1)),act(d,'senses','utility','Proxy Senses','bonus',flavor='See and hear through one of your Undead until the start of your next turn. Once per Short or Long Rest you can cast a level 1+ spell from its space.')]); D(p,d)
p=C+'shadowtongue/spoken-severance-6.yml'; d=L(p); setuses(d,1,'lr')
setacts(d,[cast(d,'silent','Summon Silent (Reaction, free)',PNO+'8o4oYaFouhUAfANQ',3,'reaction','A non-Undead creature within 30 ft dies',uses(1))]); D(p,d)
p=C+'shadowtongue/whispered-influence-14.yml'; d=L(p); setuses(d,1,'lr')
setacts(d,[cast(d,'mass','Mass Suggestion (free)',P24+'phbsplMassSugges',6,cons=uses(1))]); D(p,d)
print('round1 cryptist ok')

# ================= DISCIPLE =================
import glob as _g
_m=open(os.path.expanduser('~/work/dnd5e/dnd5e.mjs')).read()
SEN='system.attributes.senses.ranges.' if 'senses.ranges.' in _m else 'system.attributes.senses.'
def spid(n):
    f=[x for x in _g.glob(os.path.expanduser('~/work/dnd5e/packs/_source/spells24/**/*.yml'),recursive=True) if yaml.safe_load(open(x))['name']==n][0]
    return P24+yaml.safe_load(open(f))['_id']
ESS='feat:channeled-essence'; DIE='@scale.disciple.die'; FC='@scale.disciple.die.faces'; DS=f'(8 + @abilities.wis.mod + @prof)'
def dmgact(d,tag,name,formula,types,activation='special',cond='',cons=None,**kw):
    i,a=act(d,tag,'damage',name,activation,cond,cons,target=one(),**kw); a['damage']={'critical':{'allow':True,'bonus':''},'parts':[dpart(None,None,types,formula)]}; return i,a
M=F+'disciple/'
p=M+'godhand/star-gauntlet-3.yml'; d=L(p)
i,a=act(d,'blast','attack','Radiant Blast','action','Replaces an Unarmed Strike',rng={'units':'ft','value':'60','special':'120 ft from Disciple level 6','override':True},target=one())
a['attack']={'ability':'dex','bonus':'','critical':{'threshold':None},'flat':False,'type':{'value':'ranged','classification':'unarmed'}}
a['damage']={'critical':{'bonus':''},'includeBase':False,'parts':[dpart(None,None,['radiant'],f'{DIE} + @abilities.dex.mod')]}
i2,a2=act(d,'blastb','attack','Radiant Blast (Bonus Action)','bonus',rng=a['range'],target=one()); a2['attack']=a['attack']; a2['damage']=copy.deepcopy(a['damage'])
setacts(d,[(i,a),(i2,a2)]); D(p,d)
p=M+'godhand/divine-resonance-3.yml'; d=L(p)
setacts(d,[act(d,'beacon','utility','Resonance: Beacon','special','Once per turn on a hit',target=one(),roll=roll('1d4','Add to the next missed attack'),flavor='The next attack roll that misses the target before the end of your next turn adds 1d4.'),
           act(d,'chron','utility','Resonance: Chronicle','special','Once per turn on a hit',target=one(),flavor='Push the target up to 10 feet away from you.'),
           act(d,'fount','utility','Resonance: Fountain','special','Once per turn on a hit',target=one(),roll=roll(DIE,'Damage reduction'),flavor='The next time the target deals damage before the start of your next turn, reduce it by this roll.'),
           act(d,'tower','utility','Resonance: Tower','special','Once per turn on a hit',target=one(),flavor='The target has Disadvantage on its next attack roll before the end of your next turn.')]); D(p,d)
p=M+'godhand/astral-radiance-6.yml'; d=L(p)
i,a=act(d,'wave','save','Astral Wave','action',cons=uses(2,ESS),target=area('line',60)); a['target']['template']['width']='10'
a['save']={'ability':['dex'],'dc':{'calculation':'','formula':DS}}; a['damage']={'onSave':'half','parts':[dpart(None,None,['radiant'],f'3d{FC}')]}
setacts(d,[(i,a)]); D(p,d)
p=M+'godhand/stellar-flash-11.yml'; d=L(p)
setacts(d,[act(d,'flash','utility','Stellar Flash (Flowing Step)','bonus',cons=uses(1,ESS),flavor='Dash; teleport up to your Speed, then shed Dim Light in a 30-ft Emanation and apply Divine Resonance to creatures of your choice there.')]); D(p,d)
p=M+'godhand/hand-of-god-17.yml'; d=L(p)
e=eff(d,'Hand of God',[],'flare',duration=mins(1),desc='<p>Blazing Hand, Corona (Bright Light 30 ft), Ensouled Strikes cost no Essence Points.</p>'); d['effects']=[e]
setacts(d,[act(d,'flare','utility','Hand of God','action',cons=uses(3,ESS),effects=[e['_id']],duration={'units':'minute','value':'1','concentration':False,'override':False,'special':''}),
           dmgact(d,'blaze','Blazing Hand',f'1d{FC}',['radiant'],cond='Once per turn on a hit while flaring')]); D(p,d)

p=M+'ghostframe/infiltration-and-elimination-3.yml'; d=L(p)
setacts(d,[act(d,'hide','utility','Infiltration Mode: Hide','bonus',flavor='Take the Hide action.'),
           dmgact(d,'live','Livewire Strike',f'2d{FC}',['lightning'],cond='Once per turn on a hit with an Unarmed Strike or Powered weapon',cons=uses(1,ESS))]); D(p,d)
p=M+'ghostframe/machine-within-3.yml'; d=L(p)
d['effects']=[eff(d,'Sensory Upgrade',[chg(SEN+'darkvision',60,'add')],'dv',transfer=True)]; D(p,d)
p=M+'ghostframe/synthetic-supremacy-6.yml'; d=L(p); setuses(d,1,'sr','lr')
ca=eff(d,'Cyber Assassin',[chg('flags.dnd5e.weaponCriticalThreshold',19,'downgrade')],'cyber',duration=mins(10),desc='<p>Power Cell weapons need no charges and score Critical Hits on 19-20.</p>')
d['effects']=[ca,eff(d,'Shielded Core',[chg('system.traits.dr.value','lightning','add')],'core',transfer=True)]
setacts(d,[act(d,'cyber','utility','Cyber Assassin','special','Start of your turn',uses(1,ESS),effects=[ca['_id']],duration={'units':'minute','value':'10','concentration':False,'override':False,'special':''}),
           act(d,'drain','utility','Power Drain','bonus',cons=uses(1),roll=roll('1d8','Essence Points regained'),flavor='Destroy a fully charged Power Cell; restore the rolled Essence Points on Channeled Essence.')]); D(p,d)
p=M+'ghostframe/augment-overcharge-11.yml'; d=L(p)
d['effects']=[eff(d,'Augment Overcharge',[chg(SEN+'blindsight',10,'add')],'bs',transfer=True),eff(d,'Augment Overcharge (Cyber Assassin)',[chg(SEN+'blindsight',60,'upgrade')],'bs60',transfer=True,disabled=True,desc='<p>Turn on while Cyber Assassin is active.</p>')]; D(p,d)
p=M+'ghostframe/machine-soul-17.yml'; d=L(p); inv=next(e for e in d['effects'] if 'invisible' in e.get('statuses',[]))
inv['duration']=rnd(1); d['effects']=[inv,eff(d,'Cutting Edge Sensors',[chg(SEN+'truesight',60,'upgrade')],'ts',transfer=True,disabled=True,desc='<p>Turn on while Cyber Assassin is active.</p>')]
setacts(d,[act(d,'camo','utility','Active Camouflage','bonus',effects=[inv['_id']]),dmgact(d,'conduit','Core Conduit',f'1d{FC}',['lightning'],cond='Once per turn on a hit while Cyber Assassin is active')]); D(p,d)

p=M+'anomaly/glitch-in-the-hypergrid-3.yml'; d=L(p)
setacts(d,[act(d,'push','utility','Gridwarped Strike: Push','special','Once per turn on a hit',target=one(),flavor='Push the target up to 10 feet away from you.')]); D(p,d)
p=M+'anomaly/reality-override-6.yml'; d=L(p)
setacts(d,[cast(d,'see','See the Simulation: See Invisibility',spid('See Invisibility'),2,cons=uses(1,ESS)),
           act(d,'breach','utility','Grid Breach','bonus',cons=uses(1,ESS),rng=ft(60),flavor='Teleport up to 60 feet to an unoccupied space you can see.')]); D(p,d)
p=M+'anomaly/rewrite-trajectory-11.yml'; d=L(p); setuses(d,'max(1, @abilities.wis.mod)','lr')
e=eff(d,'Rewrite Trajectory',[],'cover',duration=rnd(1),desc='<p>Three-Quarters Cover (+5 AC) against ranged attacks until the start of your next turn.</p>'); d['effects']=[e]
setacts(d,[act(d,'rewrite','utility','Rewrite Trajectory','special','When you use Centered Deflection against a ranged attack',uses(1),effects=[e['_id']])]); D(p,d)
p=M+'anomaly/impossible-no-more-17.yml'; d=L(p)
e=eff(d,'Impossible No More',[chg('system.attributes.movement.fly','@attributes.movement.walk','upgrade'),chg('system.attributes.movement.hover','true','override')],'form',duration=mins(1),
      desc='<p>Bullet Time (10-ft Emanation: ranged attacks have Disadvantage, Resistance to ranged weapon damage), Fly Speed and hover, Overclock.</p>'); d['effects']=[e]
setacts(d,[act(d,'form','utility','Impossible No More','action',cons=uses(3,ESS),effects=[e['_id']],duration={'units':'minute','value':'1','concentration':False,'override':False,'special':''}),
           act(d,'over','utility','Overclock (4 Unarmed Strikes)','bonus',cons=uses(1,ESS),flavor='Use Ensouled Strikes and make four Unarmed Strikes instead of three.')]); D(p,d)
print('round1 disciple ok')

# ---- Cacophonous Spells: fixed Cacophony grants + tone choice ----
_sp={}
for f in _g.glob(os.path.expanduser('~/work/dnd5e/packs/_source/spells24/**/*.yml'),recursive=True):
    x=yaml.safe_load(open(f)); _sp.setdefault(x['name'],P24+x['_id'])
for f in _g.glob(os.path.join(OUT,'spells/**/*.yml'),recursive=True):
    x=yaml.safe_load(open(f)); _sp[x['name']]=PNO+x['_id']
def su(n):
    for k in (n,"Melf's "+n,"Otiluke's "+n,"Tasha's "+n):
        if k in _sp: return {'uuid':_sp[k],'optional':False,'sort':0}
    raise KeyError(n)
p=C+'cacophonous/cacophonous-spells-3.yml'; d=L(p)
SPC={'ability':[],'uses':{'max':'','per':'','requireSlot':False},'method':'pact','prepared':2}
CAC={3:['Bane','Malignant Spray'],5:['Summon Lesser Discordant'],7:['Dimension Door'],9:['Forceful Majesty']}
TONE={3:['Dissonant Whispers','Silence','Acid Arrow','Ray of Sickness','Command','Power Sag','Hideous Laughter','Mirror Image'],
      5:['Slow','Haste','Raking Shot','Hypnotic Pattern'],7:['Phantasmal Killer','Vitriolic Sphere','Resilient Sphere','Confusion'],
      9:['Antilife Shell','Insect Plague','Wall of Force','Mislead']}
adv={}
for lv in (3,5,7,9):
    g=mkid(f'cacspells:g{lv}'); adv[g]={'_id':g,'type':'ItemGrant','configuration':{'items':[su(n) for n in CAC[lv]],'optional':False,'spell':SPC,'sorting':'m'},'value':{},'level':lv,'title':'Cacophony Spells','hint':''}
    c=mkid(f'cacspells:c{lv}'); adv[c]={'_id':c,'type':'ItemChoice','level':lv,'title':'Discordant Tone Spells',
      'hint':'Pick the spells of your discordant tone (Entropy, Instinct, Progress or Thrill).',
      'configuration':{'choices':{str(lv):{'count':2 if lv==3 else 1,'replacement':False}},'allowDrops':False,'pool':[su(n) for n in TONE[lv]],
                       'restriction':{'type':'','subtype':'','level':'','list':[]},'spell':SPC,'type':'spell'},'value':{}}
d['system']['advancement']=adv; D(p,d)
print('round1 cacophonous spells ok')

# ---- Deepsworn Spells: Hex missing at level 3 ----
p=C+'deepsworn/deepsworn-spells-3.yml'; d=L(p)
for a in d['system']['advancement'].values():
    if a['level']==3 and not any(i['uuid']==su('Hex')['uuid'] for i in a['configuration']['items']):
        a['configuration']['items'].append(su('Hex'))
D(p,d); print('round1 deepsworn hex ok', su('Hex')['uuid'])

# ---- Godhand: Religion proficiency, Godhand's Reach 120 ft ----
p=G+'godhand/divine-resonance-3.yml' if 'G' in dir() else None
p=OUT+'/features/disciple/godhand/divine-resonance-3.yml'; d=L(p)
adv=d['system'].setdefault('advancement',{})
t=mkid('godhand:religion')
adv[t]={'_id':t,'type':'Trait','level':3,'title':'Divine Resonance: Religion','hint':'Religion proficiency (another skill if you already have it).',
        'configuration':{'mode':'default','allowReplacements':True,'grants':['skills:rel'],'choices':[]},'value':{}}
D(p,d)
p=OUT+'/features/disciple/godhand/star-gauntlet-3.yml'; d=L(p)
for a in d['system']['activities'].values():
    a['range']['value']='60 + 60 * min(1, floor(@classes.disciple.levels / 6))'
D(p,d); print('round1 godhand ok')

# ---- Ghostframe Machine Within: SIGNAL, Tech Interface ----
p=OUT+'/features/disciple/ghostframe/machine-within-3.yml'; d=L(p)
adv=d['system'].setdefault('advancement',{})
for tag,title,cfg in [('lang','Synthetic Speech',{'mode':'default','allowReplacements':False,'grants':['languages:neonOdyssey:signal'],'choices':[]}),
                      ('skill','Tech Interface',{'mode':'default','allowReplacements':False,'grants':[],'choices':[{'count':1,'pool':['skills:cmp','skills:tec']}]})]:
    i=mkid('ghostframe:mw:'+tag); adv[i]={'_id':i,'type':'Trait','level':3,'title':title,'hint':'','configuration':cfg,'value':{}}
B='max(1, @abilities.wis.mod)'
d['effects']=[e for e in d['effects'] if e['name']!='Tech Interface']+[eff(d,'Tech Interface',
    [chg('system.skills.cmp.bonuses.check',B,'override'),chg('system.skills.tec.bonuses.check',B,'override')],'techint',transfer=True)]
D(p,d); print('round1 ghostframe ok')
