import sys,re,os,copy,yaml; sys.path.insert(0,'.')
from gen_bestiary import *
from PIL import Image
VI='/home/ubuntu/work/neon-odyssey/icons/vehicles'; os.makedirs(VI,exist_ok=True)
import io
_p=pymupdf.Pixmap(DOC,1683)
if _p.colorspace and _p.colorspace.n!=3: _p=pymupdf.Pixmap(pymupdf.csRGB,_p)
im=Image.open(io.BytesIO(_p.tobytes('png'))).convert('RGB'); im.save(VI+'/planetary-vehicles.webp',quality=88)
im.crop((660,460,1190,777)).resize((512,306)).save(VI+'/planetary-vehicles-icon.webp',quality=88)
c=im.crop((780,540,960,700)); c=c.resize((400,int(400*c.height/c.width))); sq=Image.new('RGB',(400,400),(20,20,30)); sq.paste(c,(0,(400-c.height)//2)); sq.save(VI+'/vehicle-token.webp',quality=88)
IMG='modules/neon-odyssey/icons/vehicles/planetary-vehicles-icon.webp'; TOK='modules/neon-odyssey/icons/vehicles/vehicle-token.webp'
T=yaml.safe_load(open('/home/ubuntu/work/dnd5e/packs/_source/actors24/vehicles/galley.yml'))
SZ={'Tiny':'tiny','Small':'sm','Medium':'med','Large':'lg','Huge':'huge','Gargantuan':'grg'}
def blocks():
    for pn in (195,196,197):
        full='\n'+DOC[pn-1].get_text(); ms=list(re.finditer(r'\n([A-Z][\w ]+)\n\1\n',full))
        for i,m in enumerate(ms): yield pn,m.group(1),full[m.start():ms[i+1].start() if i+1<len(ms) else len(full)]
def num(s,d=0):
    m=re.search(r'\d[\d,]*',s or ''); return int(m.group().replace(',','')) if m else d
def main():
    fv=folder('bestiary','vehicles','Planetary Vehicles',typ='Actor',sort=3)
    for pn,name,t in blocks():
        t=t.split('NEON ODYSSEY PLAYTEST')[0]
        a=copy.deepcopy(T); s=a['system']; _id=mkid('vehicle:'+name)
        m=re.search(r'\n(\w+) Vehicle \(([^;]+); ([^)]+)\)',t); size,cls,wt=m.groups()
        flying='Air' in name or 'Airspeeder' in name or re.search(r'Speed [^\n]*fly',t)
        s['details']['type']='air' if flying else 'land'
        s['traits']['size']=SZ[size]; s['traits']['weight']={'value':num(wt),'units':'lb'}
        ac=re.search(r'AC (\d+)([^\n]*)',t); s['attributes']['ac']={'flat':int(ac.group(1)),'calc':'flat','motionless':ac.group(2).strip(' \t()')}
        hp=re.search(r'HP (\d+) \(Damage Threshold (\d+), Mishap Threshold (\d+)\)',t)
        s['attributes']['hp'].update(value=int(hp.group(1)),max=int(hp.group(1)),dt=int(hp.group(2)),mt=int(hp.group(3)))
        sp=re.search(r'Speed ([^\n]+)',t).group(1); mf=re.search(r'[Ff]ly (?:Speed )?(\d+)',sp); ft=int(mf.group(1)) if (flying and mf) else num(sp); mph=re.search(r'Cruise (\d+) mph',sp)
        s['attributes']['movement']={'units':'ft','hover':'hover' in sp.lower(),'ignoredDifficultTerrain':[],('fly' if flying else 'walk'):ft}
        if mph: s['attributes']['travel']={'units':'mph','paces':{},'speeds':{('air' if flying else 'land'):int(mph.group(1))},'time':24}
        ini=re.search(r'Initiative ([+−-]\d+)',t)
        flat=re.sub(r'\s+',' ',t)
        for ab in ('STR','DEX','CON','INT','WIS','CHA'):
            v=re.search(ab+r' (\d+) ',flat); s['abilities'][ab.lower()]['value']=int(v.group(1)) if v else 0
        s['abilities']['dex']['proficient']=0
        cargo=re.search(r'Cargo Capacity ([^\n]+)',t).group(1); pas=re.search(r'Passengers ([^\n]+)',t).group(1); crew=re.search(r'Crew ([^\n]+)',t).group(1)
        s['attributes']['capacity']={'creature':str(num(pas)+num(crew)),'cargo':{'value':num(cargo) if 'ton' in cargo else round(num(cargo)/2000,2),'units':'tn'}}
        s['attributes']['actions']={'stations':True,'thresholds':{'0':None,'1':None,'2':None},'max':0,'spent':0}
        s['identifier']=ident(name); s['source']={'revision':1,'rules':'2024','license':'','book':'Neon Odyssey: Outrunner’s Handbook','page':str(pn),'custom':''}
        desc=re.search(rf'\n{name.upper()}\n(.*?)(?=\n[A-Z ]{{6,}}\n|$)',DOC[194].get_text(),re.S)
        dtxt=re.sub(r'\s+',' ',desc.group(1)).strip() if desc else ''
        s['details']['biography']={'value':f"<p>{dtxt}</p><p><strong>Class</strong> {cls}. <strong>Cargo</strong> {cargo}. <strong>Passengers</strong> {pas}. <strong>Crew</strong> {crew}. <strong>Initiative</strong> {ini.group(1) if ini else '+0'} plus PB.</p>",'public':''}
        secs={'Traits':[],'Actions':[]}; cur=None
        for ln in t.split('\n'):
            ln=ln.strip()
            if ln=='Traits': cur='Traits'; continue
            if ln=='Crew Stations': cur='Actions'; continue
            if not cur or not ln: continue
            if re.match(r'^[A-Z][\w’\'\- ]*(?: \([^)]*\)?)?\.\s',ln) or (re.match(r'^[A-Z][\w’\'\- ]* \(',ln) and secs[cur] and secs[cur][-1].endswith('.')): secs[cur].append(ln)
            elif secs[cur]: secs[cur][-1]+=' '+ln
        items=[]
        for sec,ents in secs.items():
            for i,e in enumerate(ents):
                it=item_for(e,sec,f'vehicle:{name}:{sec}:{i}','icons/svg/upgrade.svg'); it['_key']=f"!actors.items!{_id}.{it['_id']}"; it['_stats']=stats(); items.append(it)
        a.update(_id=_id,name=name,img=IMG,items=items,folder=fv,_key=f'!actors!{_id}',_stats=stats(),effects=[])
        a['prototypeToken'].update(name=name,actorLink=False); a['prototypeToken']['texture']['src']=TOK
        write('bestiary',f'vehicles/{ident(name)}.yml',a,kind='actors')
        print(name,s['details']['type'],size,s['attributes']['ac']['flat'],s['attributes']['hp']['max'],ft,{k:len(v) for k,v in secs.items()})
main()
