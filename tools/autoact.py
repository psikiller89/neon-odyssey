import re, hashlib
ABIL={'strength':'str','dexterity':'dex','constitution':'con','intelligence':'int','wisdom':'wis','charisma':'cha'}
DTYPES={'acid','bludgeoning','cold','fire','force','lightning','necrotic','piercing','poison','psychic','radiant','slashing','thunder'}
B62='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
def mkid(seed):
    n=int(hashlib.sha1(seed.encode()).hexdigest(),16); s=''
    for _ in range(16): s+=B62[n%62]; n//=62
    return s
def activation_of(t):
    if re.search(r'\b(as a|take a|use your|using a|use a|your) Reaction\b|\bReaction,? (which|when)\b',t): return 'reaction'
    if re.search(r'\bBonus Action\b',t): return 'bonus'
    if re.search(r'\b(Magic action|take the \w+ action|as an action|Utilize action)\b',t,re.I): return 'action'
    return None
def uses_of(t):
    u=None; rec=[]
    m=re.search(r'(?:a number of times equal to|uses equal to|number of uses equal to) (?:your |the )?([\w ]+?) modifier',t)
    if m and m.group(1).split()[-1].lower() in ABIL: u=f"max(1, @abilities.{ABIL[m.group(1).split()[-1].lower()]}.mod)"
    elif m and 'spellcasting' in m.group(1).lower(): u="max(1, @attributes.spell.mod)"
    elif re.search(r'(a number of times equal to|uses equal to) your Proficiency Bonus',t): u='@prof'
    elif re.search(r'\btwice\b[^.]*\b(Long|Short) Rest',t) or re.search(r'use (it|this feature) twice',t): u='2'
    elif re.search(r'(Once you use this (feature|benefit|ability)|once per (Long|Short) Rest|can’t (use|do) (it|this|so) again until you finish|Once per (Long|Short) Rest)',t,re.I): u='1'
    if u:
        if re.search(r'finish a Short or Long Rest',t): rec=[{'period':'sr','type':'recoverAll'}]
        elif re.search(r'regain (one|1) (expended )?use[^.]*Short Rest',t): rec=[{'period':'lr','type':'recoverAll'},{'period':'sr','type':'formula','formula':'1'}]
        elif re.search(r'Short Rest',t) and not re.search(r'Long Rest',t): rec=[{'period':'sr','type':'recoverAll'}]
        else: rec=[{'period':'lr','type':'recoverAll'}]
        return {'max':u,'spent':0,'recovery':rec}
    return {'max':'','spent':0,'recovery':[]}
def damage_parts(t, spell_level=None):
    parts=[]
    for m in re.finditer(r'(\d+)d(\d+)(?:\s*(?:\+|plus)\s*(?:your )?(\w+)(?: modifier)?)?\s+(\w+)(?:\s+or\s+(\w+))?\s+damage',t):
        typ=[x.lower() for x in (m.group(4),m.group(5)) if x and x.lower() in DTYPES]
        if not typ: continue
        bonus=''
        if m.group(3):
            g=m.group(3).lower()
            bonus='@mod' if g in('spellcasting','ability') else (f"@abilities.{ABIL[g]}.mod" if g in ABIL else '')
        p={'number':int(m.group(1)),'denomination':int(m.group(2)),'bonus':bonus,'types':typ,'custom':{'enabled':False,'formula':''},'scaling':{'mode':'','number':None,'formula':''}}
        parts.append(p)
    return parts[:3]
def heal_part(t):
    m=re.search(r'regains? (?:a number of )?Hit Points equal to (\d+)d(\d+)(?:\s*(?:\+|plus)\s*(?:your )?(\w+) modifier)?',t) or re.search(r'regains? (\d+)d(\d+)(?:\s*(?:\+|plus)\s*(?:your )?(\w+) modifier)? Hit Points',t)
    if m:
        g=(m.group(3) or '').lower(); bonus='@mod' if g in('spellcasting',) else (f"@abilities.{ABIL[g]}.mod" if g in ABIL else '')
        return {'number':int(m.group(1)),'denomination':int(m.group(2)),'bonus':bonus,'types':['healing'],'custom':{'enabled':False,'formula':''},'scaling':{'mode':'','number':None,'formula':''}}
    m=re.search(r'(?:gain|gains) (\d+)d(\d+)(?:\s*(?:\+|plus)\s*(?:your )?(\w+) modifier)? Temporary Hit Points',t) or re.search(r'(?:gain|gains) (\d+) Temporary Hit Points',t)
    if m:
        if len(m.groups())>=2 and m.group(2):
            g=(m.group(3) or '').lower(); bonus=f"@abilities.{ABIL[g]}.mod" if g in ABIL else ''
            return {'number':int(m.group(1)),'denomination':int(m.group(2)),'bonus':bonus,'types':['temphp'],'custom':{'enabled':False,'formula':''},'scaling':{'mode':'','number':None,'formula':''}}
        return {'number':None,'denomination':None,'bonus':'','types':['temphp'],'custom':{'enabled':True,'formula':m.group(1)},'scaling':{'mode':'','number':None,'formula':''}}
    return None
def save_of(t):
    m=re.search(r'(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw',t)
    return ABIL[m.group(1).lower()] if m else None
def attack_of(t):
    m=re.search(r'(melee|ranged) spell attack',t,re.I)
    if m: return {'value':m.group(1).lower(),'classification':'spell'}
    m=re.search(r'make an? (melee|ranged) (weapon )?attack',t,re.I)
    if m and not re.search(r'(when you make|used to make|time you make)',t[:m.end()][-60:],re.I): return {'value':m.group(1).lower(),'classification':'weapon'}
    return None
def base_activity(typ,seed,act,name=''):
    return {'_id':mkid(seed),'type':typ,'name':name,'activation':{'type':act or '','value':None,'condition':'','override':False},
      'consumption':{'targets':[],'scaling':{'allowed':False,'max':''},'spellSlot':True},'description':{'chatFlavor':''},
      'duration':{'units':'inst','concentration':False,'override':False},'effects':[],'range':{'override':False,'units':'self','special':''},
      'target':{'template':{'contiguous':False,'units':'ft','type':''},'affects':{'choice':False,'count':'','type':''},'prompt':True,'override':False},
      'uses':{'spent':0,'recovery':[],'max':''},'sort':0}
def build_activity(text, seed, *, is_spell=False, spell_level=0, dc_ability=None, act=None, consume_uses=False, scaling=None, name=''):
    t=text
    act=act or activation_of(t)
    atk=attack_of(t); sv=save_of(t); dmg=damage_parts(t); heal=heal_part(t)
    if scaling and dmg:
        for p in dmg:
            p['scaling']={'mode':'whole','number':scaling.get('number') or 1,'formula':''}
    if is_spell and spell_level==0 and dmg:
        for p in dmg: p['scaling']={'mode':'whole','number':None,'formula':''}
    if atk:
        a=base_activity('attack',seed,act,name); a['attack']={'ability':'','bonus':'','critical':{'threshold':None},'flat':False,'type':atk}
        a['damage']={'critical':{'bonus':''},'includeBase':not is_spell and atk['classification']=='weapon','parts':dmg}
    elif sv and dmg and not re.search(r'(failed save|fail(s|ed)? the save|on a failure|Failure:|half as much)',t, re.I) and t.find('saving throw')>t.find(' damage'):
        a=base_activity('damage',seed,act,name); a['damage']={'critical':{'allow':False,'bonus':''},'parts':dmg}
    elif sv:
        a=base_activity('save',seed,act,name)
        calc='spellcasting' if (is_spell or 'spell save DC' in t) else (dc_ability or 'spellcasting')
        a['save']={'ability':[sv],'dc':{'calculation':calc,'formula':''}}
        a['damage']={'onSave':'half' if re.search(r'half as much damage',t) else 'none','parts':dmg}
    elif heal:
        a=base_activity('heal',seed,act,name); a['healing']=heal
        if scaling and heal.get('number'): heal['scaling']={'mode':'whole','number':scaling.get('heal') or heal['number'],'formula':''}
    elif dmg:
        a=base_activity('damage',seed,act,name); a['damage']={'critical':{'allow':False,'bonus':''},'parts':dmg}
    elif act or consume_uses or is_spell:
        a=base_activity('utility',seed,act,name); a['roll']={'formula':'','name':'','prompt':False,'visible':False}
    else:
        return None
    if consume_uses: a['consumption']['targets']=[{'type':'itemUses','value':'1','target':'','scaling':{}}]
    if is_spell:
        a['range']={'override':False}; a['duration']={'override':False}; a['target']={'override':False,'prompt':True}
    return a
