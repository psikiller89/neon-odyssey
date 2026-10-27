import pymupdf, json, re
L=json.load(open('lines.json'))
res={}
SRC=(('/home/ubuntu/attachments/b5d7ad51-25c5-4f45-99ae-512a102d1eec/Outrunners_Handbook_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf','handbook'),('/home/ubuntu/attachments/511d651c-f209-4eb8-a6e5-d1e0b47364d1/Overdrive_Expansion_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf','overdrive'))
for path,key in SRC:
    doc=pymupdf.open(path)
    heads=[(l['p'],l['y0'],l['text'].strip()) for l in L[key] if l.get('k')=='H_SECTION']
    titles=[l for l in L[key] if l.get('k')=='TABLE' and re.search(r'\S Spells\s*$',l['text']) and not re.match(r'Level \d',l['text'])]
    for tl in titles:
        p=tl['p']; page=doc[p-1]
        words=[w for w in page.get_text('words') if tl['x0']-8<=w[0]<=tl['x0']+262 and tl['y0']+8<w[1]<tl['y0']+260]
        lines={}
        for w in words: lines.setdefault(round(w[3]/3),[]).append(w)
        rows=[]; lasty=None
        for k in sorted(lines):
            ws=sorted(lines[k],key=lambda w:w[0]); txt=' '.join(w[4] for w in ws)
            if lasty is not None and ws[0][1]-lasty>22: break
            if 'Level' in txt and not rows: lasty=ws[0][3]; continue
            if re.fullmatch(r'\d+',ws[0][4]):
                cells=[[]]; prevx=ws[0][2]
                for w in ws[1:]:
                    if w[0]-prevx>9 and cells[-1]: cells.append([])
                    cells[-1].append(w[4]); prevx=w[2]
                rows.append({'level':int(ws[0][4]),'cells':[' '.join(c) for c in cells]}); lasty=ws[0][3]
            elif rows:
                cells=[[]]; prevx=None
                # continuation: attach to cells by x proximity
                for w in ws:
                    if prevx is not None and w[0]-prevx>9: cells.append([])
                    cells[-1].append(w[4]); prevx=w[2]
                for i,c in enumerate(cells):
                    if i<len(rows[-1]['cells']): rows[-1]['cells'][i]+=' '+' '.join(c)
                lasty=ws[0][3]
            else: break
        prev=[h for h in heads if (h[0],h[1])<=(p,tl['y0']) and not h[2].endswith(('SUBCLASSES','LIST','FEATURES','OPTIONS')) and not h[2].startswith('BECOMING')]
        name=prev[-1][2] if prev else '?'
        res[key+':'+tl['text'].strip()]={'section':name,'p':p,'rows':rows}
json.dump(res,open('subspells.json','w'),indent=1,ensure_ascii=False)
for k,v in res.items(): print(k,'|',v['section'],[(r['level'],r['cells'][0][:40],len(r['cells'])) for r in v['rows']][:5])
