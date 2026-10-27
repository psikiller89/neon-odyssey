import pymupdf, json, io, glob, os
from PIL import Image
L=json.load(open('lines.json')); outl=json.load(open('outline.json'))
H=pymupdf.open('/home/ubuntu/attachments/b5d7ad51-25c5-4f45-99ae-512a102d1eec/Outrunners_Handbook_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf')
O=pymupdf.open('/home/ubuntu/attachments/511d651c-f209-4eb8-a6e5-d1e0b47364d1/Overdrive_Expansion_v0.1.1_-_Neon_Odyssey_Playtest_1.pdf')
subs={s['name'].upper():s['name'] for c in outl['classes'].values() for s in c['subclasses']}
EXCL={1740,1749}
D='/home/ubuntu/work/neon-odyssey/icons/subclasses'
for f in glob.glob(D+'/*'): os.remove(f)
res={}
def pix(doc,x):
    base=pymupdf.Pixmap(doc,x); sm=doc.extract_image(x).get('smask')
    if base.colorspace and base.colorspace.n!=3: base=pymupdf.Pixmap(pymupdf.csRGB,base)
    if sm:
        if base.alpha: base=pymupdf.Pixmap(base,0)
        base=pymupdf.Pixmap(base,pymupdf.Pixmap(doc,sm))
    return Image.open(io.BytesIO(base.tobytes('png'))).convert('RGBA')
for key,doc in (('handbook',H),('overdrive',O)):
    used=set(); seen=set()
    for l in L[key]:
        t=l.get('text','').strip()
        if l.get('k')!='H_SECTION' or t in seen: continue
        if key=='handbook' and t in subs: name=subs[t]
        elif key=='overdrive' and ':' in t and 'CHANGE' not in t: name=t.split(':',1)[1].strip().title()
        else: continue
        seen.add(t)
        cand=[i['xref'] for pp in (l['p'],l['p']+1) for i in doc[pp-1].get_image_info(xrefs=True) if i['xref'] and i['xref'] not in EXCL and i['xref'] not in used]
        if not cand: print('NONE',name); continue
        x=cand[0]; used.add(x); im=pix(doc,x)
        bb=im.getbbox() or (0,0,im.width,im.height); im=im.crop(bb)
        w,h=im.size; s=min(w,h)
        im=im.crop(((w-s)//2,0,(w-s)//2+s,s)).resize((512,512),Image.LANCZOS)
        fn=name.lower().replace(' ','-'); im.save(f'{D}/{fn}.webp',quality=88); res[name]=fn
print(len(res))
fs=sorted(glob.glob(D+'/*.webp'))
sheet=Image.new('RGBA',(10*96,6*96),(40,0,60,255))
for i,f in enumerate(fs):
    t=Image.open(f).resize((96,96)); sheet.paste(t,((i%10)*96,(i//10)*96),t)
sheet.save('/home/ubuntu/work/img/subsheet.png')
cs=sorted(glob.glob('/home/ubuntu/work/neon-odyssey/icons/classes/*.png'))
s2=Image.new('RGB',(13*80,80))
for i,f in enumerate(cs): s2.paste(Image.open(f).convert('RGB').resize((80,80)),(i*80,0))
s2.save('/home/ubuntu/work/img/classsheet.png')
print([os.path.basename(f) for f in fs])
