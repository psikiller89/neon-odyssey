import sys,yaml,glob,os,re,copy,json; sys.path.insert(0,'.')
from common import OUT, stats
from autoact import mkid
ABIL={'strength':'str','dexterity':'dex','constitution':'con','intelligence':'int','wisdom':'wis','charisma':'cha'}
DT={'acid','bludgeoning','cold','fire','force','lightning','necrotic','piercing','poison','psychic','radiant','slashing','thunder'}
def txt(d): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',(d.get('system',{}).get('description') or {}).get('value','') or ''))
def chg(key,val,typ): return {'key':key,'value':str(val),'priority':None,'type':typ,'phase':'initial','_id':mkid(f'fa:{key}:{val}')}
def eff(d,name,changes,tag):
    eid=mkid(d['_id']+':'+tag)
    return {'_id':eid,'name':name,'img':d.get('img'),'type':'base','system':{'changes':changes},'disabled':False,'transfer':True,
      'duration':{'value':None,'units':'seconds','expiry':None,'expired':False},'description':'','tint':'#ffffff','statuses':[],'sort':0,'flags':{},
      'origin':None,'start':None,'showIcon':1,'folder':None,'_stats':stats(),'_key':f"!items.effects!{d['_id']}.{eid}"}
def dump(d,f): yaml.safe_dump(d,open(f,'w'),sort_keys=False,allow_unicode=True,width=200)
files=[f for f in glob.glob(os.path.join(OUT,'**','*.yml'),recursive=True) if not f.endswith('_folder.yml')]
TPL=None
for f in files:
    d=yaml.safe_load(open(f))
    for a in ((d.get('system') or {}).get('activities') or {}).values():
        if a.get('type')=='save' and TPL is None: TPL=copy.deepcopy(a)
def save_act(seed,ab,dc,parts,act):
    a=copy.deepcopy(TPL); a['_id']=mkid(seed); a['name']='Save'; a['effects']=[]; a['activation']={'type':act,'value':None,'condition':'','override':False}
    a['save']={'ability':[ab],'dc':({'calculation':'','formula':str(dc)} if dc else {'calculation':'spellcasting','formula':''})}
    a['damage']={'onSave':'half','parts':parts}; a['consumption']={'targets':[],'scaling':{'allowed':False,'max':''},'spellSlot':True}; a['uses']={'spent':0,'recovery':[],'max':''}
    return a
def parts_from(t):
    out=[]
    for n,dd,sg,bn,ty in re.findall(r'\((\d+)d(\d+)(?:\s*([+−-])\s*(\d+))?\)\s+(\w+) damage',t):
        if ty.lower() in DT: out.append({'number':int(n),'denomination':int(dd),'bonus':(('-' if sg in '−-' else '')+bn) if bn else '','types':[ty.lower()],'custom':{'enabled':False,'formula':''},'scaling':{'mode':'','number':None,'formula':''}})
    return out
C={'resist':[],'speed':[],'npcsave':[],'spellsave':[]}
SKIP_SPEED={'Flight','Adaptive Mutation','Path of Life and Death','Mark II Armor','Critical Mass','Supreme Symbiosis','Saurian Lineage','Laika Lineage'}
for f in files:
    d=yaml.safe_load(open(f)); ch=False
    if d.get('type')=='feat' and not d.get('effects'):
        t=txt(d)
        for s in re.split(r'(?<=\.)\s+',t):
            m=re.match(r'You have Resistance to ((?:\w+ damage(?:, | and |, and )?)+)\.?',s.strip())
            if m and ' or ' not in s:
                types=[x.lower() for x in re.findall(r'(\w+) damage',m.group(1)) if x.lower() in DT]
                if types: d['effects']=[eff(d,d['name'],[chg('system.traits.dr.value',x,'add') for x in types],'res')]; C['resist'].append(d['name']); ch=True; break
        if not ch and d['name'] not in SKIP_SPEED and 'Alternatively' not in t:
            sp=[]
            for sen in re.split(r'(?<=\.)\s+',t):
                if re.match(r'\s*(When|While|If|As a|Until|Alternatively|For the duration)',sen) or re.search(r'\b(while|until|for the duration|for 1 minute)\b',sen): continue
                if re.search(r'\b(You|you)\b[^.]{0,40}?\b(gain|have) a (Climb|Swim|Burrow|Fly) Speed',sen):
                    sp+=[x.lower() for x in re.findall(r'(Climb|Swim|Burrow|Fly) Speed',sen.split('equal to your Speed')[0])] if 'equal to your Speed' in sen else []
            if sp:
                d['effects']=[eff(d,d['name'],[chg(f'system.attributes.movement.{x}','@attributes.movement.speed','upgrade') for x in dict.fromkeys(sp)],'spd')]; C['speed'].append(d['name']); ch=True
    if d.get('type')=='spell' and '/spells/' in f:
        t=txt(d); acts=d['system'].get('activities') or {}
        m=re.search(r'(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) saving throw',t)
        if m and acts and not any(a['type']=='save' for a in acts.values()):
            act=next(iter(acts.values()))['activation']['type']
            a=save_act(d['_id']+':xsave',ABIL[m.group(1).lower()],None,[],act); acts[a['_id']]=a; C['spellsave'].append(d['name']); ch=True
    if d.get('type') in('npc','vehicle'):
        for i in d.get('items',[]):
            t=txt(i); acts=i['system'].get('activities') or {}
            m=re.search(r'(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw: DC (\d+)',t)
            if m and not any(a['type']=='save' for a in acts.values()):
                fail=t[m.end():]; pf=parts_from(fail.split('Success:')[0])
                act=next(iter(acts.values()))['activation']['type'] if acts else 'action'
                a=save_act(i['_id']+':xsave',ABIL[m.group(1).lower()],m.group(2),pf,act); acts[a['_id']]=a; i['system']['activities']=acts
                C['npcsave'].append(f"{d['name']}>{i['name']}"); ch=True
    if ch: dump(d,f)
open("fix_audit.out","w").write("\n".join(f"{k} {len(v)} {v}" for k,v in C.items()))
for k,v in C.items(): print(k,len(v),v)
