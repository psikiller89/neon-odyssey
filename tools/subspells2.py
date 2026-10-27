import pymupdf, json, re, unicodedata
L=json.load(open('lines.json')); O=json.load(open('outline.json')); T=json.load(open('tables.json'))
srd=json.load(open('/home/ubuntu/work/srd_spells24.json'))
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s.replace('’',"'")).lower())
vocab={norm(n):n for n in srd}
for s in O['spells']: vocab[norm(s['name'])]=s['name']
for t in T.values():
    for r in t['rows']:
        if r and r[0] and len(r)>=2 and r[1] and r[1].split()[0] in('Abjuration','Conjuration','Divination','Enchantment','Evocation','Illusion','Necromancy','Transmutation'):
            n=re.sub(r'\*|\(.*?\)','',r[0].replace('\n',' ')).strip(); vocab.setdefault(norm(n),n)
keys=sorted(vocab,key=len,reverse=True)
SRC=(('/home/ubuntu/attachments/b5d7ad51-25c5-4f45-99ae-512a102d1eec/Outrunners_Handbook_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf','handbook'),('/home/ubuntu/attachments/511d651c-f209-4eb8-a6e5-d1e0b47364d1/Overdrive_Expansion_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf','overdrive'))
res={}
for path,key in SRC:
    doc=pymupdf.open(path)
    titles=[l for l in L[key] if l.get('k')=='TABLE' and re.search(r'\S Spells\s*$',l['text']) and not re.match(r'Level \d',l['text'])]
    for tl in titles:
        p=tl['p']; page=doc[p-1]
        ws=[w for w in page.get_text('words') if tl['x0']-10<=w[0]<=tl['x0']+262 and tl['y0']+8<w[1]<tl['y0']+140]
        digs=sorted([w for w in ws if re.fullmatch(r'(3|5|7|9|11|13|17)',w[4]) and w[0]<tl['x0']+60],key=lambda w:w[1])
        lv=[]; 
        for d in digs:
            if lv and int(d[4])<=lv[-1][0]: break
            lv.append((int(d[4]),d[1]))
        rows=[]
        for i,(l,y) in enumerate(lv):
            yend=lv[i+1][1]-2 if i+1<len(lv) else y+14
            txt=' '.join(w[4] for w in sorted([w for w in ws if y-4<=w[1]<yend and w[0]>tl['x0']+15],key=lambda w:(round(w[1]/4),w[0])))
            n=norm(txt.replace('*','')); found=[]
            for k in keys:
                if len(k)>3 and k in n: found.append(vocab[k]); n=n.replace(k,'|')
            rows.append({'level':l,'spells':found,'raw':txt})
        res[tl['text'].strip().replace(' Spells','')]={'p':p,'src':key,'rows':rows}
json.dump(res,open('subspells.json','w'),indent=1,ensure_ascii=False)
for k,v in res.items(): print(k,[(r['level'],r['spells']) for r in v['rows']])
