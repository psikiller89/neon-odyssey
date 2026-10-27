import sys,re,json; sys.path.insert(0,'.')
import gen_bestiary as gb
import pymupdf
gb.DOC=pymupdf.open('/home/ubuntu/attachments/40cf019c-571c-4173-9841-a3fee0a2e470/Cosmic_Codex_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf')
from gen_bestiary import parse_block, art, actor, write, uuid, folder, ident
def main():
    fc=folder('bestiary','cosmic-codex','Cosmic Codex Monsters',typ='Actor',sort=4)
    out={}; fails=[]
    for pn in range(6,len(gb.DOC)+1):
        full='\n'+gb.DOC[pn-1].get_text()
        ms=list(re.finditer(r'\n([A-Z][\w’\'\- ]+)\n(?:Tiny|Small|Medium|Large|Huge|Gargantuan)[^\n]*\n',full))
        for rank,m in enumerate(ms):
            name=m.group(1); t=full[m.start():ms[rank+1].start() if rank+1<len(ms) else len(full)]
            if '\nActions\n' not in t and '\nTraits\n' not in t:
                idx=[full.find(k) for k in ('\nTraits\n','\nActions\n') if 0<=full.find(k)<m.start()]
                if idx: t=t.split('NEON ODYSSEY PLAYTEST')[0]+full[min(idx):m.start()]
            try: d=parse_block(t)
            except Exception as e: fails.append((pn,name,repr(e))); continue
            lore_end=ms[0].start(); lore=full[:lore_end].split('NEON ODYSSEY PLAYTEST')[0]
            bio='<p>'+'</p><p>'.join(x.strip().replace('\n',' ') for x in re.split(r'\n(?=[A-Z])',lore) if x.strip())+'</p>'
            img,tok=art(pn,name,rank)
            if not img: img=tok='icons/svg/mystery-man.svg'
            a=actor(d,name,bio,img,tok,'codex:'+name,fc)
            write('bestiary',f'cosmic-codex/{ident(name)}.yml',a,kind='actors'); out[name]=uuid('bestiary',a['_id'],'Actor')
            print(pn,name,d['size'],d['cr'],{k:len(v) for k,v in d['secs'].items()},bool(img))
    print('FAILS',fails); json.dump(out,open('codex_uuids.json','w'),indent=1)
main()
