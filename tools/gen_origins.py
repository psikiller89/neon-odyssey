import sys, re, json, os, io, glob, yaml; sys.path.insert(0,'.')
from common import *
from autoact import build_activity, uses_of, mkid
from outline import Item, fmt_parts
import pymupdf
from PIL import Image
L=json.load(open('lines.json')); F=json.load(open('lines_front.json'))
HB='/home/ubuntu/attachments/b5d7ad51-25c5-4f45-99ae-512a102d1eec/Outrunners_Handbook_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf'
DOC=pymupdf.open(HB)
OD='/home/ubuntu/attachments/511d651c-f209-4eb8-a6e5-d1e0b47364d1/Overdrive_Expansion_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf'
DOCS={'handbook':DOC,'overdrive':pymupdf.open(OD)}
SKILL={'acrobatics':'acr','animal handling':'ani','arcana':'arc','athletics':'ath','deception':'dec','history':'his','insight':'ins','intimidation':'itm','investigation':'inv','medicine':'med','nature':'nat','perception':'prc','performance':'prf','persuasion':'per','religion':'rel','sleight of hand':'slt','stealth':'ste','survival':'sur','computers':'cmp','technology':'tec'}
TYPES={'humanoid','construct','ooze','plant','elemental','fey','celestial','aberration','monstrosity','beast','dragon','fiend','giant','undead'}
ICON_DIR=os.path.expanduser('~/work/neon-odyssey/icons/species')
_COMMON={}
SP_RANK={'Benthos':1}
def species_icon(page,name,DOC=DOC):
    os.makedirs(ICON_DIR,exist_ok=True)
    if id(DOC) not in _COMMON:
        cnt={}
        for pg in DOC:
            for x in {i['xref'] for i in pg.get_image_info(xrefs=True) if i['xref']}: cnt[x]=cnt.get(x,0)+1
        _COMMON[id(DOC)]={x for x,c in cnt.items() if c>=3}
    infos=[i for i in DOC[page-1].get_image_info(xrefs=True) if i['xref'] and i['xref'] not in _COMMON[id(DOC)]]
    if not infos: return None
    infos=[i for i in infos if i['bbox'][0]>-20] or infos
    port=[i for i in infos if i['height']>i['width']*1.1]
    cand=sorted(port or infos,key=lambda i:-i['width']*i['height'])
    x=cand[min(SP_RANK.get(name,0),len(cand)-1)]['xref']
    base=pymupdf.Pixmap(DOC,x); sm=DOC.extract_image(x).get('smask')
    if base.colorspace and base.colorspace.n!=3: base=pymupdf.Pixmap(pymupdf.csRGB,base)
    if sm:
        if base.alpha: base=pymupdf.Pixmap(base,0)
        base=pymupdf.Pixmap(base,pymupdf.Pixmap(DOC,sm))
    im=Image.open(io.BytesIO(base.tobytes('png'))).convert('RGBA'); im=im.crop(im.getbbox() or (0,0,im.width,im.height))
    fn=ident(name); art=im.copy(); art.thumbnail((700,1100)); art.save(f'{ICON_DIR}/{fn}-art.webp',quality=88)
    w,h=im.size; s=min(w,h); im=im.crop(((w-s)//2,0,(w-s)//2+s,s)).resize((512,512),Image.LANCZOS)
    im.save(f'{ICON_DIR}/{fn}.webp',quality=88); return f'modules/{MOD}/icons/species/{fn}.webp'
def lineage_text(page,book='handbook',DOC=DOC):
    out=''
    for l in L[book]:
        if l['p']==page and l.get('k')=='TABLE' and l['text'].strip().endswith('Lineages'):
            r=pymupdf.Rect(l['x0']-8,l['y0']+10,l['x0']+262,l['y0']+330)
            txt=DOC[page-1].get_text('text',clip=r)
            out+=f"<h4>{l['text'].strip()}</h4><p>"+'<br>'.join(t for t in txt.split('\n') if t.strip())+'</p>'
    return out
def feat(name,html,text,*,seed,typ,subtype,req='',img='icons/svg/upgrade.svg',folder=None,adv=None):
    u=uses_of(text); a=build_activity(text,seed+':a',dc_ability='con',consume_uses=bool(u['max']))
    return {'_id':mkid(seed),'name':name,'type':'feat','img':img,'folder':folder,'sort':0,'effects':[],
        'system':{'description':{'value':html,'chat':''},'source':dict(SRC_HB),'uses':u,'type':{'value':typ,'subtype':subtype},'prerequisites':{'level':None,'repeatable':False},
        'properties':[],'requirements':req,'activities':{a['_id']:a} if a else {},'enchant':{},'identifier':ident(name),'advancement':adv or {}}}
def main():
    reset('origins')
    FS=folder('origins','species','Species',sort=1); FB=folder('origins','backgrounds','Backgrounds',sort=2); FF=folder('origins','origin-feats','Homeworld Origin Feats',sort=3)
    FT=folder('origins','species-traits','Species Traits',sort=4)
    # ---------- species ----------
    lines=[dict(l,book='handbook') for l in L['handbook'] if 127<=l['p']<=147]+[dict(l,book='overdrive') for l in L['overdrive'] if 41<=l['p']<=61]
    species=[]; cur=None; mode=None; tr=None; tab=False
    for ln in lines:
        k=ln.get('k'); t=ln.get('text','').strip()
        if k=='TAB': tab=True; continue
        if k=='H_SECTION':
            if cur and cur['name'].upper()==t: continue
            cur={'name':t.title(),'p':ln['p'],'book':ln['book'],'intro':Item('i'),'meta':{},'traits':[]}; species.append(cur); mode='intro'; continue
        if cur is None: continue
        if k=='H_FEATURE' and t.endswith('Traits'): mode='meta'; continue
        if k=='SPELLMETA' and mode=='meta':
            m=re.match(r'^(Creature Type|Size|Speed):\s*(.*)$',t)
            if m: cur['meta'][m.group(1)]=m.group(2); cur['_l']=m.group(1)
            elif cur.get('_l'): cur['meta'][cur['_l']]+=' '+t
            continue
        if k in('BODY','OTHER'):
            if mode=='intro': cur['intro'].add(ln,tab); tab=False; continue
            if mode=='meta':
                if t.startswith('As a') or t.startswith('As an'): mode='traits'; continue
                cur['meta'][cur.get('_l','Size')]+=' '+t; continue
            if mode=='traits':
                first=next((p for p in ln['parts'] if p[1].strip()),None)
                m=re.match(r'^([A-Z][\w’\'\- ]+?)\.\s',t)
                if first and first[0] in('b','bi') and m:
                    tr={'name':m.group(1),'body':Item(m.group(1))}; cur['traits'].append(tr)
                if tr: tr['body'].add(ln,tab)
                tab=False
    ABN={'Strength','Dexterity','Constitution','Intelligence','Wisdom','Charisma'}
    OPTS={'Murexian':['Camouflage','Carapace','Chromatic','Electrosensory','Spines','Traversal']}
    for sp in species:
        keep=[]
        for t in sp['traits']:
            if t['name'] in ABN and keep: keep[-1].setdefault('extra',[]).append(t); continue
            keep.append(t)
        sp['traits']=keep
    count={'species':0,'traits':0}
    for sp in species:
        sid=ident(sp['name']); meta=sp['meta']
        img=species_icon(sp['p'],sp['name'],DOCS[sp['book']]) or 'icons/environment/people/commoner.webp'
        tf=folder('origins',f'species-traits/{sid}',sp['name'],parent=FT)
        tuuids=[]; ouuids=[]; alltext=''
        for tr in sp['traits']:
            text=tr['body'].text(); html=tr['body'].html(); alltext+=' '+text
            html=re.sub(r'^<p><strong>[^<]*</strong>\s*','<p>',html)
            if 'Lineage' in tr['name']: html+=lineage_text(sp['p'],sp['book'],DOCS[sp['book']])
            for ex in tr.get('extra',[]): html+=ex['body'].html(); text+=' '+ex['body'].text()
            d=feat(tr['name'],html,text,seed=f'sptrait:{sp["name"]}:{tr["name"]}',typ='race',subtype='',req=sp['name'],img=img,folder=tf)
            write('origins',f'species-traits/{sid}/{ident(tr["name"])}.yml',d); count['traits']+=1
            (ouuids if tr['name'] in OPTS.get(sp['name'],[]) else tuuids).append(uuid('origins',d['_id']))
        size=meta.get('Size','Medium'); sizes=[s for s,kw in (('med','Medium'),('sm','Small')) if kw in size]
        ms=re.search(r'(\d+)',meta.get('Speed','30')); walk=ms.group(1) if ms else '30'
        speeds={'walk':walk}
        for mv in ('swim','climb','fly','burrow'):
            if re.search(rf'{mv.capitalize()} Speed equal to your Speed',alltext): speeds[mv]=walk
            m2=re.search(rf'{mv.capitalize()} Speed of (\d+) feet',alltext)
            if m2: speeds[mv]=m2.group(1)
        dv=re.search(r'Darkvision with a range of (\d+) feet',alltext)
        ct=(meta.get('Creature Type','Humanoid').split()[0]).lower()
        adv={}
        a={'_id':mkid(f'sz:{sid}'),'type':'Size','configuration':{'sizes':sizes or ['med']},'level':0,'hint':size,'value':{},'title':''}; adv[a['_id']]=a
        a={'_id':mkid(f'tg:{sid}'),'type':'ItemGrant','configuration':{'items':[{'uuid':u,'optional':False,'sort':0} for u in tuuids],'optional':False,'spell':None,'sorting':'m'},'value':{},'level':0,'hint':'','title':f'{sp["name"]} Traits'}; adv[a['_id']]=a
        if ouuids:
            a={'_id':mkid(f'oc:{sid}'),'type':'ItemChoice','configuration':{'choices':{'0':{'count':1,'replacement':False}},'allowDrops':False,'type':'feat','pool':[{'uuid':u} for u in ouuids],'restriction':{'type':'race','subtype':'','list':[]}},'value':{},'level':0,'title':'Evolutionary Adaptation','hint':'Choose one option.'}; adv[a['_id']]=a
        for i,m3 in enumerate(re.finditer(r'proficiency in (?:the |one of the following skills(?: of your choice)?:? )?((?:[A-Z][a-z]+(?: of Hand| Handling)?(?:,\s*|,? or\s*|\s+and\s+)?)+)(?: skills?)',alltext)):
            names=[n.strip().lower() for n in re.split(r',\s*|\s+or\s+|\s+and\s+',m3.group(1)) if n.strip()]
            pool=['skills:'+SKILL[n] for n in names if n in SKILL]
            if not pool: continue
            ch=[{'count':1,'pool':pool}] if len(pool)>1 and re.search(r'\bor\b',m3.group(1)) else []
            a={'_id':mkid(f'sk:{sid}:{i}'),'type':'Trait','configuration':{'mode':'default','allowReplacements':False,'grants':[] if ch else pool,'choices':ch},'value':{'chosen':[]},'level':0,'title':'Skill Proficiency','hint':''}; adv[a['_id']]=a
        arthtml=f'<p><img src="{img.replace(".webp","-art.webp")}" style="max-height:420px;float:right;margin-left:8px"></p>' if img.startswith('modules/') else ''
        sysd={'description':{'value':arthtml+sp['intro'].html(),'chat':''},'source':dict(SRC_HB if sp['book']=='handbook' else SRC_OD),'advancement':adv,
              'movement':{'units':None,'hover':False,'speeds':speeds,'ignoredDifficultTerrain':[]},
              'senses':{'units':None,'special':'','ranges':{'darkvision':int(dv.group(1)) if dv else None,'blindsight':None,'tremorsense':None,'truesight':None}},
              'type':{'value':ct if ct in TYPES else 'humanoid','custom':'','subtype':''},'identifier':sid}
        write('origins',f'species/{sid}.yml',{'_id':mkid('species:'+sp['name']),'name':sp['name'],'type':'race','img':img,'system':sysd,'effects':[],'folder':FS,'sort':0})
        count['species']+=1
    # ---------- homeworld origin feats ----------
    feats=[]; cur=None; on=False; tab=False
    for ln in F:
        k=ln.get('k'); t=ln.get('text','').strip()
        if k=='TAB': tab=True; continue
        if k=='H_SECTION': on = t=='HOMEWORLD ORIGIN FEATS'; continue
        if k=='H_SUBCLASSES': on=False; continue
        if not on: continue
        if k=='H_FEATURE': cur={'name':t,'pre':'','body':Item(t)}; feats.append(cur); tab=False; continue
        if cur is None: continue
        if k=='META': cur['pre']+=(' ' if cur['pre'] else '')+t; continue
        if k in('BODY','OTHER'): cur['body'].add(ln,tab); tab=False
    fu=[]
    for f in feats:
        m=re.search(r'Prerequisite:\s*(.*?)\)?$',f['pre']); pre=m.group(1) if m else ''
        d=feat(f['name'],f'<p><em>{f["pre"]}</em></p>'+f['body'].html(),f['body'].text(),seed='ofeat:'+f['name'],typ='feat',subtype='origin',req=pre,img='icons/magic/symbols/star-yellow.webp',folder=FF)
        write('origins',f'origin-feats/{ident(f["name"])}.yml',d); fu.append(uuid('origins',d['_id']))
    count['origin feats']=len(fu)
    # ---------- custom background ----------
    srd_origin=[ 'Compendium.dnd5e.feats24.Item.'+yaml.safe_load(open(p))['_id'] for p in glob.glob(os.path.expanduser('~/work/dnd5e/packs/_source/feats24/origin-feats/*.yml')) if not p.endswith('_folder.yml')]
    allsk=['skills:'+v for v in SKILL.values()]
    adv={}
    def put(a): adv[a['_id']]=a
    put({'_id':mkid('bg:asi'),'type':'AbilityScoreImprovement','configuration':{'cap':2,'fixed':{k:0 for k in('str','dex','con','int','wis','cha')},'locked':[],'points':3},'value':{},'level':0,'title':'Background Ability Score Improvement','hint':'+2 to one ability score and +1 to another, or +1 to three ability scores.'})
    put({'_id':mkid('bg:sk'),'type':'Trait','configuration':{'mode':'default','allowReplacements':False,'grants':[],'choices':[{'count':2,'pool':allsk}]},'value':{'chosen':[]},'level':0,'title':'Skill Proficiencies','hint':''})
    put({'_id':mkid('bg:tech'),'type':'Trait','configuration':{'mode':'default','allowReplacements':True,'grants':[],'choices':[{'count':1,'pool':['skills:cmp','skills:tec']}]},'value':{'chosen':[]},'level':0,'title':'Computers or Technology','hint':''})
    put({'_id':mkid('bg:tool'),'type':'Trait','configuration':{'mode':'default','allowReplacements':False,'grants':[],'choices':[{'count':1,'pool':['tool:*']}]},'value':{'chosen':[]},'level':0,'title':'Tool Proficiency','hint':''})
    put({'_id':mkid('bg:lang'),'type':'Trait','configuration':{'mode':'default','allowReplacements':False,'grants':['languages:standard:common'],'choices':[{'count':2,'pool':['languages:*']}]},'value':{'chosen':[]},'level':0,'title':'Languages','hint':''})
    put({'_id':mkid('bg:feat'),'type':'ItemChoice','configuration':{'choices':{'0':{'count':1,'replacement':False}},'allowDrops':True,'type':'feat','pool':[{'uuid':u} for u in fu+srd_origin],'restriction':{'type':'feat','subtype':'origin','list':[]}},'value':{},'level':0,'title':'Origin Feat','hint':'Choose an Origin feat (homeworld feats require a matching homeworld).'})
    bhtml='<p>Neon Odyssey recommends creating your own background with the following:</p><ul><li><p>2 Skill Proficiencies</p></li><li><p>1 Tool Proficiency</p></li><li><p>Proficiency in your choice of the Computers or Technology skill</p></li><li><p>2 Vehicle Proficiencies (Light Planetary recommended)</p></li><li><p>Common and 2 other languages</p></li><li><p>$2,500 to spend on equipment</p></li><li><p>+2 to one ability score and +1 to another, or +1 to three ability scores</p></li><li><p>An Origin feat of your choice</p></li></ul><p>Alternatively, use any background from the basic rules.</p>'
    write('origins','backgrounds/outrunner.yml',{'_id':mkid('bg:outrunner'),'name':'Outrunner (Custom Background)','type':'background','img':'icons/environment/settlement/city-night.webp' if False else 'icons/sundries/documents/document-sealed-signatures-red.webp',
        'system':{'description':{'value':bhtml,'chat':''},'source':dict(SRC_HB),'startingEquipment':[],'identifier':'outrunner','advancement':adv,'wealth':'50'},'effects':[],'folder':FB,'sort':0})
    print(count, [ (s['name'],len(s['traits'])) for s in species])
if __name__=='__main__': main()
