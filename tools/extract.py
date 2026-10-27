import pymupdf, glob, json, re, os
WHITE=16777215
def style(s):
    return (round(s['size'],1), s['font'], s['color'])
def classify(st):
    size,font,color=st
    if size>=40: return 'BIG'
    if size==23.1: return 'SKIP'
    if size==20.0 and 'Rift' in font: return 'H_SUBCLASSES'
    if size==15.0 and 'Rift' in font: return 'H_SECTION'
    if size==14.0 and 'Rift-BoldItalic' in font: return 'H_STATBLOCK'
    if size==14.0: return 'SKIP'   # page number
    if size==10.1: return 'SKIP'
    if size==8.0 and font=='ScalaSansPro-Bold' and color==WHITE: return 'SKIP'
    if size==12.0: return 'TAGLINE'
    if size==11.0 and 'Bold' in font and color==16773632: return 'STAT_H'
    if size==11.0 and 'Bold' in font: return 'H_FEATURE'
    if size==9.5 and font=='ScalaSansPro-Ita' and color==7821189: return 'META'
    if size==9.5 and color==786456: return 'SPELLMETA'
    if size==9.5 and color in (16773632,) : return 'TABLE'
    if size==8.6: return 'TABLE'
    if size==9.5 and font=='ScalaSansPro' and color==7821189: return 'TABLE'
    if size==9.5 and color==13813718: return 'SIDEHEAD'
    if size<=9.0: return 'STAT'
    if size==9.5 and color==WHITE: return 'SIDEBAR'
    if size==9.5: return 'BODY'
    return 'OTHER'

def extract(path, prange):
    d=pymupdf.open(path)
    out=[]
    for pn in prange:
        page=d[pn]
        for b in page.get_text('dict')['blocks']:
            for l in b.get('lines',[]):
                spans=[s for s in l['spans'] if s['text']!='' and not (s['color']==WHITE and (round(s['size'],1) in (11.0,9.9,15.0,55.0,42.0,20.0,12.0,23.1) or 'Rift-BoldItalic' in s['font']))]
                if not spans: continue
                # drop white shadow copies of headings
                kinds=[classify(style(s)) for s in spans]
                firstk=None
                for s,k in zip(spans,kinds):
                    if s['text'].strip(): firstk=k; fs=s; break
                if firstk is None:
                    if any('\t' in s['text'] for s in spans): out.append({'p':pn+1,'k':'TAB'})
                    continue
                if firstk=='SKIP': continue
                if firstk in('H_FEATURE','H_SECTION','BIG','H_SUBCLASSES','TAGLINE','H_STATBLOCK') and fs['color']==WHITE:
                    continue
                if firstk=='H_FEATURE' and re.fullmatch(r'\d+',fs['text'].strip()) and fs['color']==WHITE: continue
                parts=[]
                for s,k in zip(spans,kinds):
                    t=s['text']
                    if 'NeonOdysseyIcons' in s['font']: t='*'
                    if 'NO-GNote' in s['font']: t='$'
                    if s['font']=='ArialMT': t='•'
                    f=s['font']
                    fmt='b' if f.endswith('-Bold') else 'bi' if f.endswith('BoldIta') else 'i' if f.endswith('-Ita') else ''
                    parts.append((fmt,t))
                y0=round(l['bbox'][1]); x0=round(l['bbox'][0])
                if firstk in ('H_FEATURE','OTHER') and out and out[-1].get('k')=='H_FEATURE' and out[-1]['p']==pn+1 and abs(out[-1]['y0']-y0)<=2 and x0>=out[-1]['x0']:
                    out[-1]['parts']+=parts; out[-1]['text']+=''.join(t for _,t in parts); continue
                out.append({'p':pn+1,'k':firstk,'x0':x0,'y0':y0,'parts':parts,'text':''.join(t for _,t in parts)})
    return out

if __name__=='__main__':
    base=os.path.expanduser('~/attachments')
    hb=[x for x in glob.glob(base+'/*/*.pdf') if 'Outrunners' in x][0]
    od=[x for x in glob.glob(base+'/*/*.pdf') if 'Overdrive' in x][0]
    H=extract(hb, range(15,182))
    O=extract(od, range(2,61))
    json.dump({'handbook':H,'overdrive':O},open(os.path.expanduser('~/work/build/lines.json'),'w'))
    for name,L in (('handbook',H),('overdrive',O)):
        with open(os.path.expanduser(f'~/work/build/{name}_lines.txt'),'w') as f:
            lastp=None
            for l in L:
                if l['p']!=lastp: f.write(f'---- page {l["p"]}\n'); lastp=l['p']
                if l['k']=='TAB': f.write('[TAB]\n'); continue
                f.write(f'{l["k"]:<12}|{l["text"]}\n')
