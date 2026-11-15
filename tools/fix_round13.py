#!/usr/bin/env python3
"""Round 13: Esper class + Psychonaut/Riftwalker/Symbiote/Warhead automation per book."""
import os
exec(''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fix_round7.py')).readlines()[:81]))
F='features/esper/'; PSI='feat:psionic-wellspring'; EL='@classes.esper.levels'; MOD='@attributes.spell.mod'
def psi(n=1): return [{'type':'itemUses','value':str(n),'target':PSI,'scaling':{}}]
def selfuse(n=1): return [{'type':'itemUses','value':str(n),'target':'','scaling':{}}]
def restore_psi(d,tag,n): return act(d,tag,'utility',f'Restore Use ({n} Psi Points)','none',cons=psi(n)+selfuse(-1))
def ITEM(p): return L(F+p)
def SAVE(p,d): D(F+p,d)
def scale(tag,ident,title,typ,sc):
    i=mkid('r13scale:'+tag); return i,{'_id':i,'type':'ScaleValue','configuration':{'identifier':ident,'type':typ,'distance':{'units':'ft' if typ=='distance' else ''},'scale':sc},'value':{},'title':title,'hint':'','icon':None,'classRestriction':'','flags':{}}
def save_act(d,tag,name,ab,activation,parts=None,on='half',target=None,rng=None,cons=None,effects=()):
    i,a=act(d,tag,'save',name,activation,cons=cons,rng=rng,target=target,effects=effects); svdc(a,ab,SPDC)
    if parts is not None: dmg(a,parts,on)
    return i,a

# ---------- core ----------
p='class-features/psychic-talent-1.yml'; d=ITEM(p)
d['effects']=[eff(d,'Telepathic Speech',[chg('system.traits.languages.communication.telepathy.value','30','upgrade')],'tele',transfer=True)]
SAVE(p,d)

p='class-features/unbound-psyche-1.yml'; d=ITEM(p)
UP=d['effects'][0]; UP['name']='Unbound Psyche'; UP['duration']=mins(1)
UP['description']='<p>Spell save DC +1 and Advantage on Esper spell attack rolls for 1 minute.</p>'
a=first(d); a['name']='Unleash Psyche'; a['duration']=MIN(1)
d['system']['uses']['max']='2 + @scale.warhead.exploding-power'
SAVE(p,d)

p='class-features/awakened-mind-7.yml'; d=ITEM(p)
e=copy.deepcopy(UP); e['_id']=mkid(d['_id']+':r13:up'); e['_key']=f"!items.effects!{d['_id']}.{e['_id']}"; d['effects']=[e]
setacts(d,[act(d,'up2','utility','Unleash Psyche (2 Psi Points)','bonus','Only when Unbound Psyche has no uses left',cons=psi(2),effects=[e['_id']],duration=MIN(1))])
SAVE(p,d)

p='class-features/psionic-wellspring-2.yml'; d=ITEM(p)
acts=[]
for lvl,cost,minl in [(1,2,2),(2,3,3),(3,5,5),(4,6,7),(5,7,9)]:
    i,a=act(d,f'slot{lvl}','utility',f'Create Level {lvl} Spell Slot ({cost} Psi Points)','bonus',cons=psi(cost)+[{'type':'spellSlots','value':'-1','target':str(lvl),'scaling':{}}],minlvl=minl,cls='esper')
    acts.append((i,a))
i,a=act(d,'conv','utility','Convert Spell Slot to Psi Points','none',cons=[{'type':'spellSlots','value':'1','target':'1','scaling':{'mode':'level','formula':''}},{'type':'itemUses','value':'-1','target':'','scaling':{'mode':'amount','formula':'-1'}}])
a['consumption']['scaling']={'allowed':True,'max':'9'}; acts.append((i,a))
setacts(d,acts); SAVE(p,d)

p='class-features/mental-recovery-5.yml'; d=ITEM(p)
a=first(d); a['activation']={'type':'none','value':None,'override':False,'condition':'When you finish a Short Rest'}
a['consumption']['targets'][1]['value']=f'-floor({EL} / 2)'
SAVE(p,d)

p='class-features/infinite-psyche-20.yml'; d=ITEM(p)
setacts(d,[act(d,'free','utility','Boundless Mind (free Psi Shaping)','none','Once per turn while Unbound Psyche is active')])
SAVE(p,d)

COST={'rapid-psi':2,'sharpened-psi':2}
for f in ['adapted','focused','hidden','lingering','measured','mirrored','potent','rapid','reaching','sharpened']:
    p=f'psi-shaping/{f}-psi.yml'; d=ITEM(p); n=COST.get(f+'-psi',1)
    setacts(d,[act(d,'use','utility',f'{d["name"]} ({n} Psi Point{"s" if n>1 else ""})','none','When you cast a spell',cons=psi(n))])
    SAVE(p,d)

# ---------- Psychonaut ----------
P='psychonaut/'
p=P+'empathic-presence-3.yml'; d=ITEM(p)
e1=eff(d,'Boundless Broadcast',[chg('system.traits.languages.communication.telepathy.value',f'20 * {EL}','upgrade')],'bb',transfer=True)
e2=eff(d,'Fractal Telepathy',[chg('system.skills.inv.roll.mode','1','add'),chg('system.skills.prc.roll.mode','1','add')],'ft',desc='<p>Advantage on Investigation and Perception checks while you concentrate on the telepathic links.</p>')
d['effects']=[e1,e2]
i,a=act(d,'ft','utility','Fractal Telepathy','none',effects=[e2['_id']],duration={'units':'hour','value':'1','concentration':True,'override':False,'special':''})
a['target']=one('creature',f'max(2, {MOD})'); a['range']={'value':'1','units':'mi','special':'','override':False}
setacts(d,[(i,a)]); SAVE(p,d)

p=P+'mind-dive-3.yml'; d=ITEM(p)
i1,a1=act(d,'cp','damage','Crack Psyche','none','When you deal Psychic damage with a spell')
dmg(a1,[dpart(None,None,['psychic'],f'max(0, {MOD})')])
a2=first(d); a2['name']='Thought Reader'; a2['activation']={'type':'none','value':None,'override':False,'condition':'When you cast Detect Thoughts'}
setacts(d,[(i1,a1),(a2['_id'],a2)]); SAVE(p,d)

p=P+'defensive-delusion-6.yml'; d=ITEM(p)
d['effects']=[eff(d,'Defensive Delusion: Psychic Resistance',[chg('system.traits.dr.value','psychic','add')],'dr',transfer=True),
  eff(d,'Defensive Delusion: Advantage vs Charmed/Frightened',[chg(f'system.abilities.{x}.save.roll.mode','1','add') for x in ['str','dex','con','int','wis','cha']],'adv',transfer=True,disabled=True,desc='<p>Turn on while saving to avoid or end Charmed or Frightened.</p>')]
SAVE(p,d)

p=P+'collapse-identity-6.yml'; d=ITEM(p)
setuses(d,1,'lr')
ec=eff(d,'Ego Death: Charmed',[],'ch',statuses=['charmed'],duration=mins(1)); ef=eff(d,'Ego Death: Frightened',[],'fr',statuses=['frightened'],duration=mins(1))
d['effects']=[ec,ef]
i1,a1=save_act(d,'ego','Ego Death','wis','action',target=one(),rng=ft(60),cons=selfuse(),effects=[ec['_id'],ef['_id']])
a1['description']['chatFlavor']='Apply Charmed or Frightened (your choice). The target repeats the save at the end of each of its turns.'
i2,a2=act(d,'ps','utility','Persona Shift (restore Ego Death)','action','End Charmed/Frightened on a creature in telepathic contact, then use Ego Death',cons=selfuse(-1))
setacts(d,[(i1,a1),(i2,a2)]); SAVE(p,d)

p=P+'psycho-synchronicity-14.yml'; d=ITEM(p)
i1,a1=act(d,'bs','utility','Borrow Senses','bonus',target=one(),duration={'units':'round','value':'1','concentration':False,'override':False,'special':'Until the start of your next turn'})
a2=first(d); a2['name']='Transfer Spell'; a2['activation']={'type':'none','value':None,'override':False,'condition':'When you cast a Divination, Enchantment or Illusion spell'}; a2['target']=one()
setacts(d,[(i1,a1),(a2['_id'],a2)]); SAVE(p,d)

p=P+'shatter-mindscape-18.yml'; d=ITEM(p)
a=first(d); a['name']='Shatter Mindscape'; a['activation']={'type':'none','value':None,'override':False,'condition':'When a creature fails a save against your Divination, Enchantment or Illusion spell cast with a slot'}; a['target']=one()
for e in d['effects']: e['duration']=mins(1)
setacts(d,[(a['_id'],a),restore_psi(d,'rs',5)]); SAVE(p,d)

# ---------- Riftwalker ----------
P='riftwalker/'
d=L('classes/esper/riftwalker.yml')
d['system']['advancement']={k:v for k,v in d['system']['advancement'].items() if v['type']!='ScaleValue'}
i,s=scale('rift','rift-walk','Rift Walk','distance',{'3':{'value':10},'6':{'value':20},'14':{'value':30}}); d['system']['advancement'][i]=s
D('classes/esper/riftwalker.yml',d)

p=P+'chronokeeper-3.yml'; d=ITEM(p)
d['effects']=[eff(d,'Chronokeeper: Initiative uses spellcasting ability',[chg('system.attributes.init.ability','cha','override')],'init',transfer=True)]
setacts(d,[act(d,'rr','utility','Reroll Initiative (1 Psi Point)','none','After rolling Initiative, before any turns',cons=psi(1))])
SAVE(p,d)

p=P+'rift-walk-3.yml'; d=ITEM(p)
i,a=act(d,'rw','utility','Rift Walk','none','Once on your turn while Unbound Psyche is active',rng={'value':'@scale.riftwalker.rift-walk','units':'ft','special':'','override':False})
a['description']['chatFlavor']='Teleport up to @scale.riftwalker.rift-walk ft. One creature within 10 ft of your start or end space gets +/- @scale.riftwalker.rift-walk ft Speed until the start of your next turn.'
setacts(d,[(i,a)]); SAVE(p,d)

p=P+'borrowed-time-6.yml'; d=ITEM(p)
noadv(d,'ItemGrant'); setuses(d,1,'lr')
eh=next(e for e in d['effects'] if 'Haste' in e['name']); eh['transfer']=False; eh['name']='Borrowed Time: +1 AC (Haste)'
d['effects']=[eh]
oldheal=first(d); oldheal['name']='Slow: 5 Temp HP per failed save'; oldheal['activation']={'type':'none','value':None,'override':False,'condition':'Use once per target that fails its first save against Slow'}
oldheal['consumption']['targets']=[]; oldheal['healing']=heal('5','temphp'); oldheal['target']=one('self','')
c1=cast(d,'haste','Cast Haste (free)',P24+'phbsplHaste00000',3,cons=selfuse())
c2=cast(d,'slow','Cast Slow (free)',P24+'phbsplSlow000000',3,cons=selfuse())
i3,a3=act(d,'ac','utility','Borrowed Time: +1 AC','none','While concentrating on Haste',effects=[eh['_id']],duration={'units':'minute','value':'1','concentration':False,'override':False,'special':''})
setacts(d,[c1,c2,(i3,a3),(oldheal['_id'],oldheal),restore_psi(d,'rs',5)]); SAVE(p,d)

p=P+'temporal-doorway-14.yml'; d=ITEM(p)
a=first(d); a['name']='Temporal Doorway (enemy enters rift)'; a['activation']={'type':'none','value':None,'override':False,'condition':'When an enemy enters one of your rifts'}; a['target']=one()
a['damage']['onSave']='half'
SAVE(p,d)

p=P+'unwound-future-18.yml'; d=ITEM(p)
i1,a1=save_act(d,'space','Unwound Future: Space','cha','none',[dpart(4,10,['force'])],'none',target=one(),cons=selfuse())
a1['activation']['condition']='When you hit a creature or deal damage to it (once per turn)'
a1['description']['chatFlavor']='On a failed save the target teleports up to 100 ft and its Speed is 0 until the start of your next turn.'
i2,a2=save_act(d,'time','Unwound Future: Time','cha','none',[dpart(10,10,['force'])],'none',target=one(),cons=selfuse())
a2['activation']['condition']=a1['activation']['condition']
a2['description']['chatFlavor']='On a failed save the target vanishes until the start of your next turn.'
setacts(d,[(i1,a1),(i2,a2),restore_psi(d,'rs',9)]); SAVE(p,d)

# ---------- Symbiote ----------
P='symbiote/'
d=L('classes/esper/symbiote.yml')
d['system']['advancement']={k:v for k,v in d['system']['advancement'].items() if v['type']!='ScaleValue'}
i,s=scale('shred','shred','Symbiotic Shred','dice',{'3':{'number':1,'faces':8},'18':{'number':2,'faces':8}}); d['system']['advancement'][i]=s
D('classes/esper/symbiote.yml',d)

def shred(d,tag,name,activation,cons=None,cond=''):
    i,a=act(d,tag,'attack',name,activation,cond,cons=cons,rng={'value':'10','units':'ft','special':'','override':False},target=one())
    atk(a,'melee','unarmed','spellcasting',[dpart(None,None,['psychic'],'@scale.symbiote.shred + @mod')]); return i,a
p=P+'abyssal-parasite-3.yml'; d=ITEM(p)
setuses(d,1,'lr')
em=d['effects'][0]; em['name']='Living Carapace: +2 AC (Mage Armor)'; em['transfer']=True; em['disabled']=True; em['description']='<p>Turn on while you are under Mage Armor.</p>'
eh=eff(d,'Living Carapace: Hit Points',[chg('system.attributes.hp.bonuses.overall',EL,'add')],'hp',transfer=True)
d['effects']=[em,eh]
i2,a2=rollact_=act(d,'bm','utility','Bonded Mind (+5 to Concentration save)','reaction','When you fail a save to maintain Concentration',cons=selfuse())
a2['description']['chatFlavor']='Add 5 to the Concentration save. Regain on a Long Rest or when you cast a level 1+ spell with a slot.'
setacts(d,[shred(d,'shred','Symbiotic Shred','action'),(i2,a2)]); SAVE(p,d)

p=P+'hungering-host-3.yml'; d=ITEM(p)
i1,a1=act(d,'cp','utility','Consume Pain','reaction','When you take damage',cons=[{'type':'itemUses','value':'1','target':PSI,'scaling':{'mode':'amount','formula':'1'}}])
a1['consumption']['scaling']={'allowed':True,'max':'@prof'}; a1['roll']=roll('(1 + @scaling)d6','Damage reduced')
setacts(d,[(i1,a1),shred(d,'vr','Void Rend (1 Psi Point)','bonus',cons=psi(1),cond='Advantage if you cast a spell this turn')]); SAVE(p,d)

p=P+'symbiotic-carnage-6.yml'; d=ITEM(p)
i1,a1=act(d,'dmg','damage','Symbiotic Carnage: +1d6 damage','none','Once per turn when you deal damage with an Unarmed Strike')
dmg(a1,[dpart(1,6,['psychic','acid','cold','fire','force','lightning','necrotic','poison','radiant','thunder'])])
i2,a2=act(d,'psi','utility','Symbiotic Carnage: Regain 1 Psi Point','none','Instead of the extra damage',cons=selfuse()+psi(-1))
setacts(d,[(i1,a1),(i2,a2)]); SAVE(p,d)

p=P+'survival-at-all-costs-14.yml'; d=ITEM(p)
setacts(d,[act(d,'eot','utility','End of Turn (expend 5 Psi Points)','none','At the end of your turn while Stunned or Unconscious',cons=psi(5)),
           act(d,'ds','utility','Succeed on Death Save (5 Psi Points)','none','When you fail a Death Saving Throw',cons=psi(5))])
SAVE(p,d)

p=P+'supreme-symbiosis-18.yml'; d=ITEM(p)
d['effects']=[eff(d,'Apex Adaptation',[chg('system.attributes.movement.walk','20','add'),chg('system.attributes.movement.climb','50','upgrade'),chg('system.attributes.movement.swim','50','upgrade')],'apex',transfer=True,desc='<p>Speed +20 ft; Climb and Swim Speed 50 ft (equal to a 30 ft base Speed + 20).</p>')]
setacts(d,[act(d,'liq','utility','Apex Adaptation: Walk on Liquid (1 Psi Point)','none',cons=psi(1),duration={'units':'round','value':'1','concentration':False,'override':False,'special':''})])
SAVE(p,d)

# ---------- Warhead ----------
P='warhead/'
d=L('classes/esper/warhead.yml')
d['system']['advancement']={k:v for k,v in d['system']['advancement'].items() if v['type']!='ScaleValue'}
i,s=scale('exp','exploding-power','Exploding Power','number',{'14':{'value':1}}); d['system']['advancement'][i]=s
D('classes/esper/warhead.yml',d)

p=P+'volatile-mind-3.yml'; d=ITEM(p)
i1,a1=act(d,'dp','damage','Destructive Psi','none','When you deal Force damage with a spell (one target)',target=one()); dmg(a1,[dpart(None,None,['force'],f'max(0, {MOD})')])
a2=first(d); a2['name']='Destructive Psi: Spread (1 Psi Point)'; a2['activation']={'type':'none','value':None,'override':False,'condition':'A creature within 20 ft of a target that took Force damage'}
a2['consumption']['targets']=psi(1); a2['target']=one()
setacts(d,[(i1,a1),(a2['_id'],a2)]); SAVE(p,d)

p=P+'unstable-detonation-6.yml'; d=ITEM(p)
a=first(d); a['name']='Unstable Detonation'; a['target']=area('radius',20); a['damage']['onSave']='none'
a['description']['chatFlavor']='Failed save: also pushed up to 10 ft away from you.'
SAVE(p,d)

p=P+'critical-mass-14.yml'; d=ITEM(p)
d['effects']=[]; SAVE(p,d)

p=P+'go-nuclear-18.yml'; d=ITEM(p)
d['effects']=[]; a=first(d); a['name']='Go Nuclear'; a['effects']=[]; a['target']=area('radius',30); a['damage']['onSave']='half'
a['duration']=MIN(1); a['description']['chatFlavor']='Creatures entering or starting their turn in the emanation save; on a fail they are also pushed 10 ft.'
setacts(d,[(a['_id'],a),restore_psi(d,'rs',5)]); SAVE(p,d)
print('round13 ok')

# Unbound Psyche / Awakened Mind advantage condition must target the Esper class, not the D&D sorcerer.
for p in ('class-features/unbound-psyche-1.yml','class-features/awakened-mind-7.yml'):
    fp=os.path.join(OUT,F+p)
    t=open(fp).read().replace('\\"v\\": \\"sorcerer\\"','\\"v\\": \\"esper\\"'); open(fp,'w').write(t)
print('round13 sorcerer->esper ok')
