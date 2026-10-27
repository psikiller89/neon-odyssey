import sys,re,json; sys.path.insert(0,'.')
from gen_bestiary import *
def run():
    fs=folder('bestiary','summons','Summons & Companions',typ='Actor',sort=2)
    pages={}
    for ln in open('spirit_pages.txt'):
        p,n=ln.strip().split(' ',1); pages.setdefault(int(p),[]).append(n)
    out={}
    for pn,names in pages.items():
        full=DOC[pn-1].get_text()
        pos=[(full.find('\n'+n+'\n'),n) for n in names]; pos.sort()
        for rank,(st,n) in enumerate(pos):
            end=pos[rank+1][0] if rank+1<len(pos) else len(full)
            t=full[st:end]
            try: d=parse_block(t)
            except Exception as e: print('FAIL',n,e); continue
            img,tok=art(pn,n,rank)
            a=actor(d,n,f'<p>Summoned creature from Neon Odyssey (page {pn}).</p>',img,tok,'summon:'+n,fs)
            write('bestiary',f'summons/{ident(n)}.yml',a,kind='actors'); out[n]=uuid('bestiary',a['_id'],'Actor')
            print(n,d['size'],{k:len(v) for k,v in d['secs'].items()})
    json.dump(out,open('summon_uuids.json','w'),indent=1)
run()
