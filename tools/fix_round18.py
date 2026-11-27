#!/usr/bin/env python3
"""Round 18: starship combat (Starship Maneuvers stunts, Focus/Reset Shields)."""
import os,copy
exec(''.join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'fix_round7.py')).readlines()[:81]))
def chk(d,tag,name,dc,cond=''):
    return act(d,tag,'check',name,activation='special',cond=cond,check={'ability':'dex','associated':[],'dc':{'calculation':'','formula':str(dc) if dc else ''}})
DESC=('<p>Starships move on a hex grid (1 hex = 500 ft in atmosphere, 1,500 ft in space) and facing matters. Open the <strong>Helm</strong> from the token HUD (ship wheel icon) to move the ship.</p>'
 '<p><strong>Simple Maneuvers.</strong> <em>Forward</em>: up to Speed; on later turns the ship keeps going the same number of hexes unless the pilot changes course. <em>Reverse</em>: 1 hex backward for all of its Speed. <em>Turn</em>: 1 hex of movement to turn 60°, after moving at least 1 hex forward; or all movement to pivot to any facing. <em>Side Slip</em>: diagonally forward 1 hex for 2 hexes of movement, needing 1 hex forward before the next slip. <em>Loop</em>: 12 hexes, ending 1 hex behind its start, same facing. <em>Landing and Docking</em>: at a Speed of 1 hex or less.</p>'
 '<p><strong>Stunts</strong> (one per move, vehicle Dexterity check): <em>Tight Turn</em> turns in place for free (DC 10 for 60°, 15 for 120°, 20 for 180°). <em>Hard Loop</em> (DC 25) ends 1 hex behind, same facing, for free. <em>Wingover</em> (DC 20) ends 1 hex behind facing the opposite way, for free. <em>Pursuit</em>: move into the enemy\'s space from its left, right or rear arc; it makes a vehicle Dexterity save against your check or you shadow it, moving with it and firing one front weapon as a Reaction; two pursuers have Advantage on attacks against it. <em>Skimming Run</em> (DC 10 Gargantuan, 20 Huge, 25 Large target): off sensors and untargetable by that target until the end of your next turn; fail by more than 5 and you crash. <em>Fast Landing</em> (DC 15): fail by more than 5 and you crash.</p>'
 '<p><em>From the Neon Odyssey Pre-Launch playtest starship rules; the current playtest says new starship rules will follow.</em></p>')
for p in ['bestiary/vehicles/interceptor.yml','bestiary/vehicles/superiority-fighter.yml']:
    d=L(p); aid=d['_id']
    d['items']=[i for i in d['items'] if i['name']!='Starship Maneuvers']
    base=copy.deepcopy(next(i for i in d['items'] if i['name']=='Sensors'))
    iid=mkid(aid+':r18:maneuvers'); base.update({'_id':iid,'name':'Starship Maneuvers','img':'icons/svg/wing.svg','_key':f'!actors.items!{aid}.{iid}'})
    base['system']['description']['value']=DESC; base['effects']=[]
    m={'_id':iid}
    acts=[chk(m,'tt1','Tight Turn 60° (DC 10)',10),chk(m,'tt2','Tight Turn 120° (DC 15)',15),chk(m,'tt3','Tight Turn 180° (DC 20)',20),
          chk(m,'hl','Hard Loop (DC 25)',25),chk(m,'wo','Wingover (DC 20)',20),chk(m,'pu','Pursuit (vs. target\'s vehicle Dex save)',None),
          chk(m,'sk1','Skimming Run: Gargantuan (DC 10)',10),chk(m,'sk2','Skimming Run: Huge (DC 20)',20),chk(m,'sk3','Skimming Run: Large (DC 25)',25),
          chk(m,'fl','Fast Landing (DC 15)',15)]
    base['system']['activities']={i:a for i,a in acts}
    d['items'].append(base)
    sh=next(i for i in d['items'] if i['name']=='Shields')
    for a in sh['system']['activities'].values():
        if a['type']=='heal': a['healing']['custom']['formula']='@flags.neon-odyssey.shieldMax'
    sh['system']['activities']={k:v for k,v in sh['system']['activities'].items() if not v['flags'].get('neon-odyssey')}
    for tag,name,mode in [('fs','Focus Shields','focus'),('rs','Reset Shields','reset')]:
        i,a=act(sh,tag,'utility',name,activation='action'); a['flags']={'neon-odyssey':{'shields':mode}}; sh['system']['activities'][i]=a
    v=sh['system']['description']['value']
    if 'Focus Shields' not in v:
        sh['system']['description']['value']=v+'<p><strong>Focus Shields</strong> (Utilize action): double the current and maximum Shield Points and put them on one fire arc; the other three arcs aren\'t protected. <strong>Reset Shields</strong> (Utilize action): halve the focused Shield Points and cover all arcs again; the maximum returns to normal.</p>'
    D(p,d); print('ok',d['name'])
# dnd5e 6 drops vehicle movement.fly/walk etc. (no migration for vehicles): store them in movement.speeds too.
import glob
for f in sorted(glob.glob(os.path.join(OUT,'bestiary/vehicles/*.yml'))):
    p=os.path.relpath(f,OUT); d=L(p)
    if 'system' not in d: continue
    mv=d['system']['attributes']['movement']
    sp=mv.setdefault('speeds',{})
    for k in ['walk','burrow','climb','fly','swim']:
        if mv.get(k): sp[k]=str(mv[k])
    D(p,d); print('speeds',d['name'],sp)
