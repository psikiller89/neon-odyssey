import sys, re, json, io, os; sys.path.insert(0,'.')
from common import *
from autoact import mkid, build_activity, ABIL
import pymupdf
from PIL import Image
HB='/home/ubuntu/attachments/b5d7ad51-25c5-4f45-99ae-512a102d1eec/Outrunners_Handbook_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf'
DOC=pymupdf.open(HB)
SIZES={'Tiny':'tiny','Small':'sm','Medium':'med','Large':'lg','Huge':'huge','Gargantuan':'grg'}
DT={'acid','bludgeoning','cold','fire','force','lightning','necrotic','piercing','poison','psychic','radiant','slashing','thunder'}
CONDS={'blinded','charmed','deafened','exhaustion','frightened','grappled','incapacitated','invisible','paralyzed','petrified','poisoned','prone','restrained','stunned','unconscious'}
SKL={'acrobatics':'acr','animal handling':'ani','arcana':'arc','athletics':'ath','deception':'dec','history':'his','insight':'ins','intimidation':'itm','investigation':'inv','medicine':'med','nature':'nat','perception':'prc','performance':'prf','persuasion':'per','religion':'rel','sleight of hand':'slt','stealth':'ste','survival':'sur'}
IDIR=os.path.expanduser('~/work/neon-odyssey/icons/creatures')
def art(page,name,rank=0):
    os.makedirs(IDIR,exist_ok=True)
    infos=[i for i in DOC[page-1].get_image_info(xrefs=True) if i['xref'] and i['width']<1100]
    if not infos: infos=[i for i in DOC[page-1].get_image_info(xrefs=True) if i['xref']]
    if not infos: return None,None
    infos=sorted(infos,key=lambda i:-i['width']*i['height'])
    x=infos[min(rank,len(infos)-1)]['xref']
    base=pymupdf.Pixmap(DOC,x); sm=DOC.extract_image(x).get('smask')
    if base.colorspace and base.colorspace.n!=3: base=pymupdf.Pixmap(pymupdf.csRGB,base)
    if sm:
        if base.alpha: base=pymupdf.Pixmap(base,0)
        base=pymupdf.Pixmap(base,pymupdf.Pixmap(DOC,sm))
    im=Image.open(io.BytesIO(base.tobytes('png'))).convert('RGBA'); im=im.crop(im.getbbox() or (0,0,im.width,im.height))
    fn=ident(name); w,h=im.size
    full=im.copy(); full.thumbnail((1024,1024)); full.save(f'{IDIR}/{fn}.webp',quality=88)
    s=max(w,h); tok=Image.new('RGBA',(s,s),(0,0,0,0)); tok.paste(im,((s-w)//2,(s-h)//2)); tok=tok.resize((512,512),Image.LANCZOS); tok.save(f'{IDIR}/{fn}-token.webp',quality=88)
    return f'modules/{MOD}/icons/creatures/{fn}.webp',f'modules/{MOD}/icons/creatures/{fn}-token.webp'
def parse_block(t):
    lines=[l.strip() for l in t.split('\n')]
    d={}
    m=re.search(r'\n(Tiny|Small|Medium|Large|Huge|Gargantuan)(?:,? (?:or )?(?:Tiny|Small|Medium|Large|Huge|Gargantuan))* (\w+)(?: \(([^)]*)\))?(?:, ([^\n]+))?',t); d['size'],d['type'],d['align']=m.group(1),m.group(2).lower(),(m.group(4) or '')
    m=re.search(r'AC (\d+)',t); d['ac']=int(m.group(1)) if m else 10
    m=re.search(r'HP (\d+) \(([^)]+)\)',t)
    if m: d['hp'],d['hpf']=int(m.group(1)),m.group(2)
    else:
        m=re.search(r'HP (\d+)([^\n]*)',t); d['hp'],d['hpf']=(int(m.group(1)),'') if m else (10,'')
        d['hpnote']=m.group(2).strip() if m else ''
    m=re.search(r'Speed ([^\n]+)',t); sp=m.group(1) if m else '30 ft.'; mw=re.match(r'(\d+)',sp); d['speed']={'walk':mw.group(1) if mw else '0'}
    for mv in ('Fly','Climb','Swim','Burrow'):
        m=re.search(mv+r' (\d+)',sp)
        if m: d['speed'][mv.lower()]=m.group(1)
    d['hover']='hover' in sp.lower()
    grid=t[t.find('STR'):t.find('Skills') if 'Skills' in t else t.find('Senses')]
    nums=re.findall(r'(STR|DEX|CON|INT|WIS|CHA)\s+(\d+)\s+([+−-]\d+)\s+([+−-]\d+)',grid.replace('\t',' ').replace('\n',' '))
    d['abil']={a.lower():(int(v),int(s.replace('−','-'))) for a,v,_,s in nums}
    def fld(n):
        m=re.search(n+r' ([^\n]+)',t); return m.group(1) if m else ''
    d['skills']={SKL[k.lower()] for k,_ in re.findall(r'([A-Z][a-z]+(?: of Hand| Handling)?) \+(\d+)',fld('Skills')) if k.lower() in SKL}
    d['dr']=[x.lower() for x in re.findall(r'\w+',fld('Resistances')) if x.lower() in DT]
    im=fld('Immunities'); dmg,_,cond=im.partition(';')
    d['di']=[x.lower() for x in re.findall(r'\w+',dmg) if x.lower() in DT]; d['ci']=[x.lower() for x in re.findall(r'\w+',cond+(' '+dmg if not cond else '')) if x.lower() in CONDS]
    d['senses']={k.lower():int(v) for k,v in re.findall(r'(Darkvision|Blindsight|Tremorsense|Truesight) (\d+)',fld('Senses'))}
    d['languages']=fld('Languages')
    m=re.search(r'CR ([\d/]+)',t); d['cr']=eval(m.group(1)) if m else 0
    secs={}; cur=None; buf=''
    body=t[t.find('\n',t.find('CR ')):]
    st=next((i for i,l in enumerate(lines) if l.startswith('CR ')),None)
    if st is None: st=next((i-1 for i,l in enumerate(lines) if l in('Traits','Actions','Bonus Actions','Reactions')),0)
    for ln in lines[st+1:]:
        if ln in('Traits','Actions','Bonus Actions','Reactions','Legendary Actions'): cur=ln; secs.setdefault(cur,[]); continue
        if cur is None: continue
        if re.match(r'^[A-Z][A-Z \-’]{3,}$',ln) or ln.startswith('NEON ODYSSEY'): break
        if re.match(r'^[A-Z][\w’\'\- ]*(?: \([^)]*\))?\.\s',ln): secs[cur].append(ln)
        elif secs[cur]: secs[cur][-1]+=' '+ln
    d['secs']=secs
    return d
ACT={'Actions':'action','Bonus Actions':'bonus','Reactions':'reaction','Traits':'','Legendary Actions':'legendary'}
def item_for(entry,sec,seed,img):
    name,_,text=entry.partition('. '); text=re.sub(r'\s+',' ',text)
    rech=re.search(r'\(Recharge (\d)',name); src=re.search(r'Recharge after a (Short or Long|Long) Rest',name); per=re.search(r'\((\d)/Day\)',name)
    clean=re.sub(r'\s*\(.*\)','',name)
    acts={}; uses={'max':'','spent':0,'recovery':[]}
    if rech: uses={'max':'1','spent':0,'recovery':[{'period':'recharge','formula':rech.group(1),'type':'recoverAll'}]}
    if src: uses={'max':'1','spent':0,'recovery':[{'period':'sr' if 'Short' in src.group(1) else 'lr','type':'recoverAll'}]}
    if per: uses={'max':per.group(1),'spent':0,'recovery':[{'period':'day','type':'recoverAll'}]}
    m=re.search(r'(Melee|Ranged) Attack Roll: \+(\d+)',text)
    if m and sec!='Traits':
        parts=[]
        for n,dd,ty in re.findall(r'\((\d+)d(\d+)(?: [+−-] \d+)?\) (\w+) damage',text):
            if ty.lower() in DT: parts.append({'number':int(n),'denomination':int(dd),'bonus':'@mod' if not parts else '','types':[ty.lower()],'custom':{'enabled':False,'formula':''},'scaling':{'mode':'','number':None,'formula':''}})
        rng=re.search(r'range (\d+)(?:/(\d+))? ft',text); reach=re.search(r'reach (\d+) ft',text)
        a={'_id':mkid(seed+':a'),'type':'attack','name':'','activation':{'type':ACT[sec] or 'action','value':None,'condition':'','override':False},'consumption':{'targets':[],'scaling':{'allowed':False,'max':''},'spellSlot':True},
           'attack':{'ability':'','bonus':'','critical':{'threshold':None},'flat':True,'type':{'value':m.group(1).lower(),'classification':'weapon'}},'damage':{'critical':{'bonus':''},'includeBase':False,'parts':parts},
           'range':{'override':True,'value':rng.group(1) if rng else (reach.group(1) if reach else '5'),'long':rng.group(2) if rng and rng.group(2) else None,'units':'ft'},'uses':{'spent':0,'recovery':[],'max':''},'sort':0,'effects':[],'description':{'chatFlavor':''},'duration':{'units':'inst','override':False},'target':{'override':False,'prompt':True}}
        a['attack']['bonus']=str(int(m.group(2)))
        acts[a['_id']]=a
    else:
        m2=re.search(r'(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) Saving Throw: DC (\d+)',text)
        a=build_activity(text.replace('Failure:','On a failed save, it takes').replace('Saving Throw:','saving throw'),seed+':a',act=ACT[sec] or None,consume_uses=bool(uses['max']))
        if a and m2 and a['type']=='save': a['save']={'ability':[ABIL[m2.group(1).lower()]],'dc':{'calculation':'','formula':m2.group(2)}}
        if a and sec!='Traits': acts[a['_id']]=a
    return {'_id':mkid(seed),'name':clean,'type':'feat','img':img,'effects':[],'sort':0,
        'system':{'description':{'value':f'<p>{text}</p>','chat':''},'type':{'value':'monster','subtype':''},'uses':uses,'activation':{'type':ACT[sec],'value':None,'condition':''},'activities':acts,'properties':[],'requirements':'','identifier':ident(clean)}}
def actor(d,name,bio,img,tok,seed,folder):
    _id=mkid(seed); items=[]
    for sec,ents in d['secs'].items():
        for i,e in enumerate(ents):
            it=item_for(e,sec,f'{seed}:{sec}:{i}','icons/svg/upgrade.svg'); it['_key']=f"!actors.items!{_id}.{it['_id']}"; it['_stats']=stats(); items.append(it)
    ab={k:{'value':d['abil'].get(k,(10,0))[0],'proficient':1 if d['abil'].get(k,(10,0))[1]!=(d['abil'].get(k,(10,0))[0]-10)//2 else 0} for k in ('str','dex','con','int','wis','cha')}
    sysd={'abilities':ab,'attributes':{'ac':{'flat':d['ac'],'calc':'natural'},'hp':{'value':d['hp'],'max':d['hp'],'formula':d['hpf'],'temp':None,'tempmax':None},
          'movement':{**d['speed'],'units':'ft','hover':d['hover']},'senses':{'units':'ft','special':'','ranges':{k:d['senses'].get(k) for k in ('darkvision','blindsight','tremorsense','truesight')}}},
          'details':{'cr':d['cr'],'type':{'value':d['type'],'subtype':'','custom':''},'alignment':d['align'],'biography':{'value':bio,'public':''},'source':dict(SRC_HB)},
          'traits':{'size':SIZES[d['size']],'dr':{'value':d['dr']},'di':{'value':d['di']},'ci':{'value':d['ci']},'languages':{'value':[],'custom':d['languages']}},
          'skills':{s:{'value':1,'ability':''} for s in d['skills']}}
    return {'_id':_id,'name':name,'type':'npc','img':img or 'icons/svg/mystery-man.svg','folder':folder,'system':sysd,'items':items,'effects':[],'sort':0,
            'prototypeToken':{'name':name,'texture':{'src':tok or img or 'icons/svg/mystery-man.svg'},'width':0.5 if d['size']=='Tiny' else 1,'height':0.5 if d['size']=='Tiny' else 1,'disposition':1,'actorLink':False}}
def main():
    reset('bestiary'); fb=folder('bestiary','creatures','Bestiary',typ='Actor')
    out={}
    for pn in range(183,190):
        full=DOC[pn-1].get_text()
        ms=list(re.finditer(r'\n([A-Z][a-z]+(?: [A-Z][a-z]+)?)\n(?:Tiny|Small|Medium|Large|Huge)',full))
        for rank,m in enumerate(ms):
            name=m.group(1)
            t=full[m.start():ms[rank+1].start()] if rank+1<len(ms) else full[m.start():]
            t='\n'+t
            try: d=parse_block(t)
            except Exception as e: print('FAIL',pn,name,e); continue
            lore=full[full.find(name.upper()):] if name.upper() in full else ''
            bio='<p>'+'</p><p>'.join(x.strip() for x in re.split(r'\n(?=[A-Z])',lore.split('NEON ODYSSEY PLAYTEST')[0]) if x.strip())+'</p>'
            img,tok=art(pn,name,rank)
            a=actor(d,name,bio,img,tok,'creature:'+name,fb)
            write('bestiary',f'creatures/{ident(name)}.yml',a,kind='actors'); out[name]=uuid('bestiary',a['_id'],'Actor')
            print(name,d['size'],d['cr'],{k:len(v) for k,v in d['secs'].items()})
    json.dump(out,open('bestiary_uuids.json','w'),indent=1)
if __name__=='__main__': main()
