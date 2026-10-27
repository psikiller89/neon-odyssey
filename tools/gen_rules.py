import sys,json,re,os,yaml,html as H; sys.path.insert(0,'.')
from common import *
from autoact import mkid
import importlib.util
_sp=importlib.util.spec_from_file_location('ex','/home/ubuntu/work/build/extract.py'); EX=importlib.util.module_from_spec(_sp); _sp.loader.exec_module(EX)
LV=EX.extract('/home/ubuntu/attachments/b5d7ad51-25c5-4f45-99ae-512a102d1eec/Outrunners_Handbook_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf',range(189,194))
LF=json.load(open('lines_front.json')); LM=json.load(open('lines.json'))['handbook']
def render(lines):
    out=''; para=''
    def flush():
        nonlocal out,para
        if para.strip(): out+=f'<p>{para.strip()}</p>'
        para=''
    for l in lines:
        k=l.get('k'); t=l.get('text','')
        if k=='TAB': flush(); continue
        if k in('H_SUBCLASSES','BIG'): flush(); out+=f'<h2>{H.escape(t.strip().title())}</h2>'; continue
        if k=='H_SECTION': flush(); out+=f'<h3>{H.escape(t.strip().title())}</h3>'; continue
        if k in('H_FEATURE','STAT'): flush(); out+=f'<h4>{H.escape(t.strip())}</h4>'; continue
        if k in('BODY','SIDEBAR','META','SPELLMETA','OTHER','TABLE'):
            s=''.join(f'<strong>{H.escape(x)}</strong>' if f in('b','bi') and x.strip() else H.escape(x) for f,x in l.get('parts',[]))
            if t.startswith('\t'): flush()
            if para.endswith('-'): para=para[:-1]+s.strip()
            else: para+=' '+s.strip()
    flush(); return re.sub(r'(<h[234]>[^<]*</h[234]>)\1',r'\1',out)
def pages(src,a,b): return [l for l in src if a<=l.get('p',0)<=b]
SECTIONS=[('Computers & Technology Skills, Backgrounds, Languages',pages(LF,11,12)),('Aether Exposure & Grid Spiking',pages(LF,14,15)),
          ('Equipment Rules (Currency, Weapon Properties, Modules)',pages(LM,148,151)),('Hypertech Spellcasting',[l for l in pages(LM,163,163)]),
          ('Vehicle Rules',pages(LV,190,194))]
def main():
    reset('rules'); jid=mkid('journal:rules'); pgs=[]
    for i,(name,ls) in enumerate(SECTIONS):
        pid=mkid('rules:'+name)
        pgs.append({'_id':pid,'name':name,'type':'text','sort':(i+1)*100000,'title':{'show':True,'level':1},'text':{'format':1,'content':render(ls)},'image':{},'video':{'controls':True,'volume':0.5},'src':None,'system':{},'ownership':{'default':-1},'flags':{},'category':None,'_stats':stats(),'_key':f'!journal.pages!{jid}.{pid}'})
    j={'_id':jid,'name':'Neon Odyssey Rules','pages':pgs,'folder':None,'flags':{},'sort':0,'ownership':{'default':0},'categories':[],'_stats':stats(),'_key':f'!journal!{jid}'}
    os.makedirs(os.path.join(OUT,'rules'),exist_ok=True)
    yaml.safe_dump(j,open(os.path.join(OUT,'rules','neon-odyssey-rules.yml'),'w'),sort_keys=False,allow_unicode=True,width=200)
    print([(p['name'][:25],len(p['text']['content'])) for p in pgs])
if __name__=='__main__': main()
