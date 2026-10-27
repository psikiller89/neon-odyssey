import sys,yaml,copy,os,glob; sys.path.insert(0,'.')
from common import OUT, stats
from autoact import mkid
O=os.path.join(OUT,'origins')
def eff(iid,name,changes): 
    eid=mkid(iid+':eff'); return {'_id':eid,'name':name,'img':None,'type':'base','system':{'changes':[]},'changes':changes,'statuses':[],'transfer':True,'disabled':False,
      'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},'origin':None,'tint':'#ffffff','sort':0,'flags':{},'description':'','showIcon':1,'start':None,'folder':None,'_stats':stats(),'_key':f'!items.effects!{iid}.{eid}'}
def ch(k,mode,v): return {'key':k,'mode':mode,'value':str(v),'priority':None}
L={'laika':('Laika Lineage',[
  ('Confidant','You have Advantage on Intelligence, Wisdom, and Charisma saving throws.','You and the ally you help each gain a number of Temporary Hit Points equal to three times your Proficiency Bonus.',[]),
  ('Guardian','When a creature damages you or your allies, you have Advantage on the next attack roll you make against that creature before the end of your next turn.','The next time you or the ally you help take damage within 1 minute, the target gains Resistance against that damage.',[]),
  ('Seeker','Your Speed increases to 35 feet.','You and the ally you help each have Advantage on the next ability check or attack roll either of you make within the next minute.',[ch('system.attributes.movement.walk',4,35)])]),
 'saurian':('Saurian Lineage',[
  ('Deepfin','Natural Weapon: Bite or Slam. You have Resistance to Cold damage and a Swim Speed equal to your Speed. In addition, you can hold your breath for a number of hours equal to your Constitution modifier (minimum of 1).',None,[ch('system.traits.dr.value',2,'cold'),ch('system.attributes.movement.swim',4,'@attributes.movement.walk')]),
  ('Quickclaw','Natural Weapon: Bite or Claw. You have proficiency in the Stealth skill, and while you are Lightly Obscured, you can hide while in an enemy’s line of sight.',None,[ch('system.skills.ste.value',4,1)]),
  ('Rockhide','Natural Weapon: Slam or Gore. You have a +1 bonus to AC; your Hit Point maximum increases by 1, and by 1 again each time you gain a level.',None,[ch('system.attributes.ac.bonus',2,'+1'),ch('system.attributes.hp.bonuses.level',2,'+1')]),
  ('Sharptooth','Natural Weapon: Bite. You can make a bite attack as a Bonus Action. When you hit a creature with your bite, you can deal extra damage equal to your Proficiency Bonus and regain a number of Hit Points equal to your Constitution modifier plus your Proficiency Bonus. Once you deal this extra damage, you can’t do so again until you finish a Short or Long Rest.',None,[]),
  ('Skywing','Natural Weapon: Claw. You have a Fly Speed equal to your Speed while you aren’t wearing Medium or Heavy armor.',None,[ch('system.attributes.movement.fly',4,'@attributes.movement.walk')])])}
for sp,(tname,opts) in L.items():
    tf=os.path.join(O,'species-traits',sp,tname.lower().replace(' ','-')+'.yml'); base=yaml.safe_load(open(tf))
    pool=[]
    for n,trait,pack,changes in opts:
        d=copy.deepcopy(base); iid=mkid(f'lineage:{sp}:{n}'); d['_id']=iid; d['_key']=f'!items!{iid}'; d['name']=f'{tname}: {n}'
        html=f'<p>{trait}</p>'+(f'<p><strong>Pack Minded (character level 3).</strong> {pack}</p>' if pack else '')
        d['system']['description']['value']=html; d['system']['activities']={}; d['system']['uses']={'max':'','spent':0,'recovery':[]}
        d['system']['identifier']=f'{sp}-lineage-{n.lower()}'; d['effects']=[eff(iid,d['name'],changes)] if changes else []
        if n=='Sharptooth':
            d['system']['uses']={'max':'1','spent':0,'recovery':[{'period':'sr','type':'recoverAll'}]}
        yaml.safe_dump(d,open(os.path.join(O,'species-traits',sp,f'lineage-{n.lower()}.yml'),'w'),sort_keys=False,allow_unicode=True,width=200)
        pool.append({'uuid':f'Compendium.neon-odyssey.origins.Item.{iid}'})
    sf=os.path.join(O,'species',sp+'.yml'); s=yaml.safe_load(open(sf)); adv=s['system']['advancement']
    aid=mkid(f'lineage-adv:{sp}')
    adv[aid]={'_id':aid,'type':'ItemChoice','configuration':{'choices':{'0':{'count':1,'replacement':False}},'allowDrops':False,'type':'feat','pool':pool,'restriction':{'type':'race','subtype':'','list':[]}},'value':{},'level':0,'title':tname,'hint':'Choose your lineage.'}
    yaml.safe_dump(s,open(sf,'w'),sort_keys=False,allow_unicode=True,width=200); print(sp,len(pool))
