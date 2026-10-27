import json,glob,re,os,collections,yaml
CFG=open('/home/ubuntu/work/dnd5e/module/config.mjs').read()
def keys(name):
    m=re.search(r'^DND5E\.'+re.escape(name)+r' = \{\n(.*?)^\};',CFG,re.S|re.M)
    if not m: return None
    return set(re.findall(r'^  "?([\w-]+)"?:',m.group(1),re.M))
E={k:keys(k) for k in ['damageTypes','healingTypes','abilities','skills','conditionTypes','itemProperties','weaponTypes','armorTypes','consumableTypes','toolTypes','spellSchools','creatureTypes','actorSizes','activityActivationTypes','timePeriods','movementTypes','areaTargetTypes','individualTargetTypes','featureTypes','limitedUsePeriods','spellcasting','distanceUnits','scalarTimePeriods','permanentTimePeriods','specialTimePeriods','rangeTypes','lootTypes','containerTypes','spellProgression','currencies','languages','attackTypes','weaponMasteries','abilityConsumptionTypes','activityConsumptionTypes','miscEquipmentTypes','equipmentTypes']}
print({k:(len(v) if v else v) for k,v in E.items()})
docs=[]
for f in glob.glob('/home/ubuntu/work/verify/**/*.json',recursive=True):
    docs.append((f.split('/')[5],json.load(open(f))))
def allitems():
    for p,d in docs:
        if d.get('type') in('npc','vehicle','character'):
            for i in d.get('items',[]): yield p,d['name'],i
        elif 'system' in d: yield p,None,d
issues=collections.Counter(); ex={}
def bad(k,msg):
    issues[k]+=1; ex.setdefault(k,[]).append(msg)
DMG=E['damageTypes']|E['healingTypes']|{''}
UNITS=(E['distanceUnits'] or set())|(E['rangeTypes'] or set())|{'','ft','mi','self','touch','spec','any','m','km'}
TIME=(E['scalarTimePeriods'] or set())|(E['permanentTimePeriods'] or set())|(E['specialTimePeriods'] or set())|{'','inst','spec','perm','disp','dstr','turn','round','minute','hour','day','month','year'}
CUSTOM_PROPS={'powered','burst','braced','closeQuarters','reload','scatter','pummel'}
REC=(E['limitedUsePeriods'] or set())|{'recharge','turnStart','turnEnd','turn','initiative','encounter'}
for p,owner,i in allitems():
    s=i['system']; n=(owner+'>' if owner else '')+i['name']
    for pr in s.get('properties',[]) or []:
        if pr not in E['itemProperties'] and pr not in CUSTOM_PROPS: bad('prop',f'{n}:{pr}')
    for r in (s.get('uses') or {}).get('recovery',[]) or []:
        if r.get('period') not in REC: bad('recovery',f"{n}:{r.get('period')}")
    if i['type']=='spell':
        if s.get('school') not in E['spellSchools']: bad('school',f"{n}:{s.get('school')}")
    if i['type']=='weapon' and s.get('type',{}).get('value') not in E['weaponTypes']: bad('wtype',f"{n}:{s['type']}")
    if i['type']=='weapon':
        for t in s.get('damage',{}).get('base',{}).get('types',[]): 
            if t not in DMG: bad('dmg',f'{n}:{t}')
        if s.get('mastery') and E['weaponMasteries'] and s['mastery'] not in E['weaponMasteries']: bad('mastery',f"{n}:{s['mastery']}")
    if i['type']=='consumable' and s.get('type',{}).get('value') not in E['consumableTypes']: bad('ctype',f"{n}:{s['type']}")
    if i['type']=='tool' and s.get('type',{}).get('value') not in (E['toolTypes']|{''}): bad('ttype',f"{n}:{s['type']}")
    if i['type']=='feat':
        tv=s.get('type',{}).get('value')
        if tv not in E['featureTypes']: bad('ftype',f'{n}:{tv}')
    for a in (s.get('activities') or {}).values():
        at=(a.get('activation') or {}).get('type','')
        if at not in E['activityActivationTypes']|{''}: bad('activation',f'{n}:{at}')
        du=(a.get('duration') or {}).get('units','')
        if du not in TIME: bad('duration',f'{n}:{du}')
        ru=(a.get('range') or {}).get('units','')
        if ru not in UNITS: bad('range',f'{n}:{ru}')
        tt=((a.get('target') or {}).get('template') or {}).get('type','')
        if tt and tt not in E['areaTargetTypes']: bad('template',f'{n}:{tt}')
        af=((a.get('target') or {}).get('affects') or {}).get('type','')
        if af and af not in E['individualTargetTypes']: bad('affects',f'{n}:{af}')
        for part in (a.get('damage') or {}).get('parts',[]) or []:
            for t in part.get('types',[]): 
                if t not in DMG: bad('dmg',f'{n}:{t}')
            if not part.get('number') and not part.get('custom',{}).get('enabled') and not part.get('bonus'): bad('emptydmg',n)
        if a.get('type')=='save':
            ab=a.get('save',{}).get('ability',[])
            if not ab or any(x not in E['abilities'] for x in ab): bad('saveab',f'{n}:{ab}')
            dc=a.get('save',{}).get('dc',{})
            if not dc.get('calculation') and not dc.get('formula'): bad('savedc',n)
        if a.get('type')=='check':
            if not a.get('check',{}).get('associated') and not a.get('check',{}).get('ability'): bad('check',n)
        if a.get('type')=='heal':
            h=a.get('healing',{})
            if h.get('types') and any(t not in DMG for t in h['types']): bad('heal',n)
        for c in (a.get('consumption') or {}).get('targets',[]) or []:
            if c.get('type') not in (E['activityConsumptionTypes'] or {'itemUses','activityUses','material','hitDice','spellSlots','attribute'}): bad('consume',f"{n}:{c.get('type')}")
            if c.get('type')=='itemUses' and not c.get('target') and not (s.get('uses') or {}).get('max'): bad('consume-nouses',n)
        if a.get('type')=='attack' and not a.get('damage',{}).get('parts') and not a.get('damage',{}).get('includeBase', False) and i['type']!='weapon': bad('attack-nodmg',n)
# advancement checks
S=json.dumps([d for _,d in docs])
dn=set()
for f in glob.glob('/home/ubuntu/work/dnd5e/packs/_source/**/*.yml',recursive=True):
    for m in re.finditer(r'^_id: (\w{16})',open(f).read(),re.M): dn.add(m.group(1))
for pk,t,i in re.findall(r'Compendium\.dnd5e\.([\w-]+)\.(Item|Actor|JournalEntry)\.(\w{16})',S):
    if i not in dn: bad('dnd5e-uuid',f'{pk}.{i}')
scales=set()
for p,d in docs:
    if d.get('type') in('class','subclass'):
        idn=d['system'].get('identifier') or (d['system'].get('classIdentifier'))
        for a in (d['system'].get('advancement') or {}).values():
            if a['type']=='ScaleValue': scales.add(f"{d['system']['identifier']}.{a['configuration']['identifier']}")
for sref in set(re.findall(r'@scale\.([\w-]+\.[\w-]+)',S)):
    if sref not in scales: bad('scale',sref)
for k,v in sorted(issues.items(),key=lambda x:-x[1]): print(k,v,ex[k][:6])
