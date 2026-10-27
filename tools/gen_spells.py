import sys, re, json; sys.path.insert(0,'.')
from common import *
from autoact import build_activity, mkid
T=json.load(open('tables.json'))
def parse_time(s):
    s=s or 'Action'; cond=''
    m=re.match(r'^(Reaction|Bonus Action|Action)(?:,\s*which you take\s*(.*))?',s)
    if m:
        t={'Reaction':'reaction','Bonus Action':'bonus','Action':'action'}[m.group(1)]; cond=(m.group(2) or '').strip()
        return {'type':t,'value':None,'condition':cond}
    m=re.match(r'^(\d+)\s*(minute|hour|round)',s)
    if m: return {'type':m.group(2),'value':int(m.group(1)),'condition':''}
    return {'type':'special','value':None,'condition':s}
def parse_duration(s):
    s=s or ''; conc='Concentration' in s
    m=re.search(r'(\d+)\s*(round|minute|hour|day|week|month|year)',s)
    if m: return {'value':m.group(1),'units':m.group(2)},conc
    if 'Instantaneous' in s: return {'value':'','units':'inst'},conc
    if 'dispelled' in s or 'Permanent' in s: return {'value':'','units':'perm'},conc
    return {'value':'','units':'spec'},conc
def parse_range(s):
    s=s or ''
    if s.startswith('Self'): return {'units':'self','special':''}
    if s.startswith('Touch'): return {'units':'touch','special':''}
    m=re.match(r'([\d,]+)\s*(feet|foot|miles?)',s)
    if m: return {'value':m.group(1).replace(',',''),'units':'ft' if m.group(2).startswith('f') else 'mi','special':''}
    if 'Sight' in s: return {'units':'spec','special':'Sight'}
    if 'Unlimited' in s: return {'units':'any','special':''}
    return {'units':'spec','special':s}
TPL={'sphere':'sphere','cone':'cone','cube':'cube','line':'line','emanation':'radius','cylinder':'cylinder'}
def parse_template(*texts):
    for t in texts:
        m=re.search(r'(\d+)-foot(?:-radius|-long|-wide|-tall)?,?\s*(?:[\w-]+\s+)?(Sphere|Cone|Cube|Line|Emanation|Cylinder)',t or '')
        if m:
            d={'type':TPL[m.group(2).lower()],'size':m.group(1),'units':'ft','contiguous':False,'count':''}
            if d['type']=='line': d['width']='5'
            return d
    return {'type':'','size':'','units':'ft','contiguous':False,'count':''}
import os
SUMMON=json.load(open('summon_uuids.json')) if os.path.exists('summon_uuids.json') else {}
def summon_act(name,text,_id,act):
    m=re.search(r'uses the ([A-Z][\w\- ]+?) stat block',text)
    if not m or m.group(1) not in SUMMON: return None
    return {'_id':mkid(_id+':summon'),'type':'summon','name':'Summon','activation':{'type':act,'value':None,'condition':'','override':False},
      'consumption':{'targets':[],'scaling':{'allowed':False,'max':''},'spellSlot':True},'description':{'chatFlavor':''},'duration':{'override':False},'range':{'override':False},'target':{'override':False,'prompt':False},
      'effects':[],'uses':{'spent':0,'recovery':[],'max':''},'sort':0,'bonuses':{'ac':'','hd':'','hp':'','attackDamage':'','saveDamage':'','healing':''},
      'match':{'attacks':True,'proficiency':True,'saves':True,'ability':''},'profiles':[{'_id':mkid(_id+':prof'),'count':'1','cr':'','level':{'min':None,'max':None},'name':'','uuid':SUMMON[m.group(1)]}],
      'summon':{'mode':'','prompt':True},'creatureSizes':[],'creatureTypes':[]}
def build_spell(s):
    p=s['props']; text=s['text']
    comps=p.get('Components','')
    props=[]
    if re.search(r'\bV\b',comps): props.append('vocal')
    if re.search(r'\bS\b',comps): props.append('somatic')
    mm=re.search(r'M \((.*)\)',comps)
    mat={'value':'','consumed':False,'cost':0,'supply':0}
    if re.search(r'\bM\b',comps):
        props.append('material')
        if mm:
            mat['value']=mm.group(1)
            c=re.search(r'worth (?:at least )?\$?([\d,]+)',mm.group(1))
            if c: mat['cost']=int(c.group(1).replace(',',''))
            mat['consumed']='consume' in mm.group(1)
    dur,conc=parse_duration(p.get('Duration'))
    if conc: props.append('concentration')
    if 'Ritual' in p.get('Casting Time','') or 'Ritual' in s['meta']: props.append('ritual')
    act=parse_time(p.get('Casting Time'))
    tpl=parse_template(p.get('Range'),text)
    rng=parse_range(p.get('Range'))
    affects={'type':'creature' if re.search(r'creature',text) else '','count':'','choice':False,'special':''}
    if rng['units']=='self' and not tpl['type']: affects={'type':'self','count':'','choice':False,'special':''}
    sc=None
    m=re.search(r'(?:damage|Hit Points|healing)[^.]*increases? by (\d+)d(\d+) for each spell slot level above',text) or re.search(r'increases? by (\d+)d(\d+) for each spell slot level above',text)
    if m: sc={'number':int(m.group(1)),'heal':int(m.group(1))}
    first=text.split('Using a Higher-Level Spell Slot')[0].split('Cantrip Upgrade')[0]
    _id=spell_id(s['name'])
    a=build_activity(first,f"{_id}:act",is_spell=True,spell_level=s['level'],act=act['type'] if act['type'] in('action','bonus','reaction') else None,scaling=sc)
    sysd={'description':{'value':s['html'],'chat':''},'source':dict(SRC_HB),'activation':act,'duration':dur,
      'target':{'affects':affects,'template':tpl},'range':rng,'uses':{'max':'','recovery':[],'spent':0},
      'level':s['level'],'school':SCHOOLS.get((s['school'] or '').lower(),''),'properties':props,'materials':mat,
      'method':'spell','prepared':0,'activities':{a['_id']:a} if a else {},'identifier':ident(s['name'])}
    sa=summon_act(s['name'],text,_id,act['type'] if act['type'] in('action','bonus','reaction') else 'action')
    if sa: sysd['activities']={sa['_id']:sa}
    return {'_id':_id,'name':s['name'],'type':'spell','img':IMG.get(sysd['school'],'icons/svg/book.svg'),'system':sysd,'effects':[],'folder':None,'sort':0}
IMG={'abj':'icons/magic/defensive/shield-barrier-glowing-blue.webp','con':'icons/magic/symbols/runes-star-pentagon-blue.webp','div':'icons/magic/perception/eye-ringed-glow-angry-small-teal.webp','enc':'icons/magic/control/hypnosis-mesmerism-swirl.webp','evo':'icons/magic/lightning/bolt-strike-blue.webp','ill':'icons/magic/perception/silhouette-stealth-shadow.webp','nec':'icons/magic/death/skull-horned-goat-pentagram-red.webp','trs':'icons/magic/movement/trail-streak-zigzag-yellow.webp'}
LVLNAME={0:'Cantrips',1:'Level 1',2:'Level 2',3:'Level 3',4:'Level 4',5:'Level 5',6:'Level 6',7:'Level 7',8:'Level 8',9:'Level 9'}
def main():
    reset('spells')
    fids={l:folder('spells',f'level-{l}',LVLNAME[l],sort=l*1000) for l in range(10)}
    for s in O['spells']:
        d=build_spell(s); d['folder']=fids[s['level']]
        write('spells',f"level-{s['level']}/{ident(s['name'])}.yml",d)
    # class spell lists
    CL_PAGES={'Cryptist':(23,24),'Enforcer':(38,39),'Esper':(47,49),'Gridrunner':(55,59),'Icon':(65,67),'Machinist':(82,83),'Oracle':(90,92),'Primalist':(101,103),'Tracer':(122,123)}
    reset('spell-lists')
    pages=[]; report={}
    for i,(cl,(a,b)) in enumerate(CL_PAGES.items()):
        uuids=[]; unlinked=[]
        for k,t in T.items():
            pg=int(k.split('.')[0])
            if not (a<=pg<=b): continue
            rows=[r for r in t['rows'] if r and len(r)>=2 and r[0] and r[1] and r[1].split()[0] in('Abjuration','Conjuration','Divination','Enchantment','Evocation','Illusion','Necromancy','Transmutation')]
            if not rows: continue
            res=[(r,resolve_spell(r[0].replace('\n',' '))) for r in rows]
            lv=[x[1][1] for x in res if x[1][1] is not None]
            tl=max(set(lv),key=lv.count) if lv else None
            for r,(u,l,sch,kind) in res:
                if kind=='phb': unlinked.append({'_id':mkid('ul:'+cl+r[0]),'name':re.sub(r'\*','',r[0].replace('\n',' ')).strip(),'system':{'level':tl or 0,'school':SCHOOLS.get(r[1].split()[0].lower(),'')},'source':{'book':'PHB 2024','page':'','custom':'','uuid':''}})
                elif u not in uuids: uuids.append(u)
        for s in O['spells']:
            if cl in [c.strip(' ,') for c in s['classes']]:
                u=uuid('spells',spell_id(s['name']))
                if u not in uuids: uuids.append(u)
        report[cl]=(len(uuids),len(unlinked))
        pages.append({'_id':mkid('page:'+cl),'name':f'{cl} Spell List','type':'spells','sort':(i+1)*100000,
          'system':{'type':'class','identifier':ident(cl),'grouping':'level','description':{'value':f'<p>Spells available to the {cl} class (Neon Odyssey).</p>'},'spells':uuids,'unlinkedSpells':unlinked},
          'title':{'show':True,'level':1},'image':{},'text':{'format':1},'video':{'controls':True,'volume':0.5},'src':None,'ownership':{'default':-1},'flags':{},'category':None,'_stats':stats()})
    jid=mkid('journal:spell-lists')
    for pg in pages: pg['_key']=f"!journal.pages!{jid}.{pg['_id']}"
    j={'_id':jid,'name':'Neon Odyssey Spell Lists','pages':pages,'folder':None,'flags':{},'sort':0,'ownership':{'default':0},'categories':[],'_stats':stats(),'_key':f'!journal!{jid}'}
    import yaml,os
    os.makedirs(os.path.join(OUT,'spell-lists'),exist_ok=True)
    yaml.safe_dump(j,open(os.path.join(OUT,'spell-lists','neon-odyssey-spell-lists.yml'),'w'),sort_keys=False,allow_unicode=True,width=200)
    json.dump({cl:f'Compendium.{MOD}.spell-lists.JournalEntry.{jid}.JournalEntryPage.{pg["_id"]}' for cl,pg in zip(CL_PAGES,pages)},open('spelllist_uuids.json','w'),indent=1)
    print(report)
if __name__=='__main__': main()
