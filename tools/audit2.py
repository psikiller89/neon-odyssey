import json,glob,re,collections
docs=[(f.split('/')[5],f,json.load(open(f))) for f in glob.glob('/home/ubuntu/work/verify/**/*.json',recursive=True)]
byid={d['_id']:d for p,f,d in docs}
R=collections.defaultdict(list)
def txt(d): return re.sub(r'<[^>]+>',' ',(d.get('system',{}).get('description') or {}).get('value','') or '')
def acts(d): return list((d.get('system',{}).get('activities') or {}).values())
def advs(d):
    a=d.get('system',{}).get('advancement') or {}; return list(a.values()) if isinstance(a,dict) else a
def uid(u): return u.split('.')[-1]
# ---- A. class/subclass grants
granted={}
for p,f,d in docs:
    if d.get('type') in('class','subclass'):
        lv=collections.Counter(a['type'] for a in advs(d))
        if d['type']=='class':
            for need in ('HitPoints','Subclass'):
                if not lv[need]: R['class-missing-'+need].append(d['name'])
            asi=sorted(a.get('level') for a in advs(d) if a['type']=='AbilityScoreImprovement')
            if asi and asi[:4]!=[4,8,12,16]: R['class-asi-levels'].append(f"{d['name']}:{asi}")
            if not d['system'].get('hd',{}).get('denomination'): R['class-no-hd'].append(d['name'])
        for a in advs(d):
            if a['type']=='ItemGrant':
                for it in a['configuration'].get('items',[]): granted.setdefault(uid(it['uuid']),[]).append((d['name'],a.get('level')))
for p,f,d in docs:
    if p=='features' and d.get('type')=='feat' and d['system'].get('type',{}).get('subtype') in (None,'',) and d['system'].get('type',{}).get('value')=='class':
        lvl=d['system'].get('prerequisites',{}).get('level')
        g=granted.get(d['_id'])
        if not g: R['feature-not-granted'].append(f"{f.split('/')[6]}/{d['name']}")
        elif lvl and all(l!=lvl for _,l in g): R['feature-level-mismatch'].append(f"{d['name']} prereq {lvl} granted {g}")
# ---- B. features
ACTRE=r'\b(As a Bonus Action|as a Bonus Action|As a Reaction|take a Reaction|As a Magic action|as a Magic action|As an action|you can take a Bonus Action|Bonus Action to)\b'
for p,f,d in docs:
    if d.get('type')!='feat' or p not in('features','origins'): continue
    t=txt(d); s=d['system']; a=acts(d)
    if re.search(ACTRE,t) and not a: R['feat-action-no-activity'].append(d['name'])
    if re.search(r'until you finish a (Short|Long) Rest|number of times equal to|once per (Short|Long) Rest|regain all expended uses|you can use this (feature|trait) (once|twice|a number)',t,re.I) and not (s.get('uses') or {}).get('max') and not any((x.get('uses') or {}).get('max') for x in a) and not any((x.get('consumption') or {}).get('targets') for x in a):
        R['feat-limited-no-uses'].append(d['name'])
    if re.search(r'Resistance to (\w+) damage|you have Resistance',t) and not d.get('effects') and 'Reaction' not in t and 'until' not in t: R['feat-resist-no-effect?'].append(d['name'])
    if re.search(r'your (Speed|walking speed) increases by|you have a (Fly|Climb|Swim) Speed|gain a (Fly|Climb|Swim) Speed',t) and not d.get('effects'): R['feat-speed-no-effect?'].append(d['name'])
    if re.search(r'Hit Point maximum increases',t) and not d.get('effects') and not any(x['type']=='HitPoints' for x in advs(d)): R['feat-hpmax-no-effect?'].append(d['name'])
    if re.search(r'gain proficiency|you gain proficiency in|You have Expertise|you gain Expertise',t,re.I) and not advs(d) and not d.get('effects'): R['feat-prof-no-advancement?'].append(d['name'])
    for x in a:
        if x['type']=='save' and not x.get('damage',{}).get('parts') and not x.get('effects') and re.search(r'\d+d\d+',t): R['feat-save-nodmg'].append(d['name'])
# ---- C. spells
for p,f,d in docs:
    if d.get('type')!='spell' or p!='spells': continue
    t=txt(d); s=d['system']; a=acts(d)
    if not a: R['spell-no-activity'].append(d['name'])
    dice=re.findall(r'(\d+)d(\d+)',t)
    has_dmg=any(x.get('damage',{}).get('parts') or x.get('healing',{}).get('number') or x.get('healing',{}).get('custom',{}).get('formula') for x in a)
    if re.search(r'\d+d\d+ \w+ damage',t) and not has_dmg: R['spell-dmg-text-no-dmg'].append(d['name'])
    if re.search(r'\bConcentration\b',json.dumps(s.get('duration',{}))+' '+ (s.get('_dur','')),re.I) and 'concentration' not in s.get('properties',[]): R['spell-conc'].append(d['name'])
    if not s.get('activation',{}).get('type') and not any(x.get('activation',{}).get('type') for x in a): R['spell-no-activation'].append(d['name'])
    if re.search(r'(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw',t,re.I) and not any(x['type']=='save' for x in a): R['spell-save-text-no-save'].append(d['name'])
    if re.search(r'(melee|ranged) spell attack',t,re.I) and not any(x['type']=='attack' for x in a): R['spell-attack-text-no-attack'].append(d['name'])
    if s.get('level',0)>0 and re.search(r'Using a Higher-Level Spell Slot',t) and not any(any((pp.get('scaling') or {}).get('mode') for pp in x.get('damage',{}).get('parts',[])) or (x.get('healing',{}).get('scaling') or {}).get('mode') for x in a) and re.search(r'increases by \d+d\d+',t): R['spell-no-upcast-scaling'].append(d['name'])
    if s.get('level')==0 and re.search(r'Cantrip Upgrade',t) and not any(any((pp.get('scaling') or {}).get('mode') for pp in x.get('damage',{}).get('parts',[])) for x in a) and has_dmg: R['cantrip-no-scaling'].append(d['name'])
# ---- D. items
for p,f,d in docs:
    if p!='items' or 'system' not in d: continue
    s=d['system']; ty=d['type']
    if ty=='weapon' and not s.get('damage',{}).get('base',{}).get('denomination') and 'module' not in d['name'].lower(): R['weapon-no-dmg'].append(d['name'])
    if ty=='equipment' and s.get('type',{}).get('value') in('light','medium','heavy','shield') and not s.get('armor',{}).get('value'): R['armor-no-ac'].append(d['name'])
    if ty=='consumable' and not acts(d): R['consumable-no-activity'].append(d['name'])
    pr=s.get('price',{}).get('value')
    if not pr and ty not in('container',) : R['item-no-price'].append(d['name'])
    if not d.get('img') or d['img'].startswith('icons/svg/item-bag'): R['item-generic-img'].append(d['name'])
# ---- E/F actors
for p,f,d in docs:
    if d.get('type') in('npc',):
        s=d['system']; at=s['attributes']
        if not at.get('hp',{}).get('max'): R['npc-no-hp'].append(d['name'])
        if not (at.get('ac',{}).get('flat') or at.get('ac',{}).get('calc') not in ('flat',None)): R['npc-no-ac'].append(d['name'])
        if s['details'].get('cr') is None: R['npc-no-cr'].append(d['name'])
        if not s['details'].get('type',{}).get('value'): R['npc-no-type'].append(d['name'])
        if all(v.get('value')==10 for v in s['abilities'].values()): R['npc-default-abilities'].append(d['name'])
        if not d.get('items'): R['npc-no-items'].append(d['name'])
        if not any(acts(i) for i in d.get('items',[])): R['npc-no-activities'].append(d['name'])
        mv=at.get('movement',{}); 
        if not any(isinstance(v,(int,float)) and v>0 for v in mv.values()): R['npc-no-speed'].append(d['name'])
        if 'mystery-man' in (d.get('img') or ''): R['npc-no-art'].append(d['name'])
        for i in d.get('items',[]):
            t=txt(i)
            if re.search(r'(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw: DC',t) and not any(x['type']=='save' for x in acts(i)): R['npc-save-text-no-save'].append(f"{d['name']}>{i['name']}")
            if re.search(r'Recharge \d',i['name']+t) and not (i['system'].get('uses') or {}).get('max'): R['npc-recharge-no-uses'].append(f"{d['name']}>{i['name']}")
    if d.get('type')=='race':
        s=d['system']
        if not s.get('movement',{}).get('walk') and not any(a['type']=='Size' for a in advs(d)): R['species-no-speed'].append(d['name'])
        if not any(a['type']=='Size' for a in advs(d)): R['species-no-size'].append(d['name'])
for k,v in sorted(R.items()):
    print(f"## {k} ({len(v)}): "+'; '.join(map(str,v[:40])))
