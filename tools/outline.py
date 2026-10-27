import json, re, os, html
L=json.load(open(os.path.expanduser('~/work/build/lines.json')))
CLASSES=['Cryptist','Disciple','Enforcer','Esper','Gridrunner','Icon','Juggernaut','Machinist','Oracle','Primalist','Scoundrel','Soldier','Tracer']

def fmt_parts(parts):
    s=''
    for f,t in parts:
        t=html.escape(t)
        if f in('b','bi') and t.strip(): s+=f'<strong>{t}</strong>'
        elif f=='i' and t.strip(): s+=f'<em>{t}</em>'
        else: s+=t
    return s.replace('</strong><strong>','').replace('</em><em>','')

class Item:
    def __init__(self,name,**kw):
        self.name=name; self.lines=[]; self.__dict__.update(kw)
    def add(self,line,tab_before=False):
        self.lines.append((line,tab_before))
    def html(self):
        paras=[]; cur=None
        for ln,tab in self.lines:
            raw=ln['text']; h=fmt_parts(ln['parts'])
            newp = cur is None or tab or raw.startswith('\t') or raw.lstrip().startswith('•')
            h=h.replace('\t','').strip()
            if newp:
                cur={'bullet':tab or raw.lstrip().startswith('•'),'t':h.lstrip('•').strip()}; paras.append(cur)
            else:
                if cur['t'].endswith('-') and not cur['t'].endswith(' -'): cur['t']=cur['t'][:-1]+h
                else: cur['t']+=' '+h
        out=''; inlist=False
        for p in paras:
            t=re.sub(r'\s+',' ',p['t']).replace('</strong> <strong>',' ')
            if p['bullet']:
                if not inlist: out+='<ul>'; inlist=True
                out+=f'<li><p>{t}</p></li>'
            else:
                if inlist: out+='</ul>'; inlist=False
                out+=f'<p>{t}</p>'
        if inlist: out+='</ul>'
        return out
    def text(self):
        return re.sub(r'\s+',' ',' '.join(l['text'] for l,_ in self.lines))

LVL=re.compile(r'^Level (\d+):\s*(.+)$')
def parse_handbook():
    lines=[l for l in L['handbook'] if 17<=l['p']<=126]
    classes={}; cur=None; section=None; item=None; tab=False; in_sub=False; sub=None; optlist=None; sidebar=None; last_sec=None
    for ln in lines:
        k=ln.get('k')
        if k=='TAB': tab=True; continue
        t=ln.get('text','').strip()
        if k=='BIG' and t.title() in CLASSES:
            cur={'name':t.title(),'tagline':'','intro':Item('intro'),'features':[],'options':{},'subclasses':[],'sidebars':[],'spelllist':Item('spelllist'),'core':Item('core')}
            classes[cur['name']]=cur; section='intro'; item=cur['intro']; in_sub=False; continue
        if cur is None: continue
        if k=='TAGLINE': cur['tagline']+=(' ' if cur['tagline'] else '')+t; continue
        if k=='H_SECTION':
            if t==last_sec: continue
            last_sec=t
            if t.startswith('BECOMING'): section='becoming'; item=Item('becoming'); continue
            if t.endswith('CLASS FEATURES'): section='features'; item=None; continue
            if t.endswith('SPELL LIST'): section='spelllist'; item=cur['spelllist']; continue
            if in_sub:
                sub={'name':t.title(),'intro':Item('intro'),'features':[],'sidebars':[]}; cur['subclasses'].append(sub); section='subclass'; item=sub['intro']; continue
            optlist=t.title().replace(' Options',''); cur['options'][optlist]=[]; section='options'; item=None; continue
        if k=='H_SUBCLASSES': in_sub=True; section='subintro'; item=Item('subintro'); continue
        if k=='STAT':  # sidebar title
            sidebar=Item(t); (sub or cur)['sidebars'].append(sidebar) if section=='subclass' else cur['sidebars'].append(sidebar); continue
        if k=='SIDEBAR' and sidebar is not None and section not in ('features',) or (k=='SIDEBAR' and sidebar is not None):
            sidebar.add(ln,tab); tab=False; continue
        if k=='SIDEHEAD': continue
        if k=='H_FEATURE':
            sidebar=None
            m=LVL.match(t)
            if section in('features','becoming') and m and not in_sub:
                item=Item(m.group(2).strip(),level=int(m.group(1))); cur['features'].append(item); tab=False; continue
            if section=='subclass' and m:
                item=Item(m.group(2).strip(),level=int(m.group(1))); sub['features'].append(item); tab=False; continue
            if section=='options':
                item=Item(t,prereq=None); cur['options'][optlist].append(item); tab=False; continue
            if item is not None:  # inline bold subheading inside feature
                item.add({'text':t,'parts':[('b',t)]},True); tab=False; continue
            continue
        if k=='META' and section=='options' and item is not None and item.prereq is None and not item.lines:
            item.prereq=t; continue
        if k in('BODY','META','SPELLMETA','OTHER','STAT_H') and item is not None:
            sidebar=None
            item.add(ln,tab); tab=False; continue
        if k=='TABLE': continue
    return classes

def parse_overdrive():
    lines=[l for l in L['overdrive'] if l['p']>=4]
    subs=[]; sub=None; item=None; tab=False; last=None; sidebar=None
    for ln in lines:
        k=ln.get('k')
        if k=='TAB': tab=True; continue
        t=ln.get('text','').strip()
        if k=='H_SECTION':
            if t==last: continue
            last=t
            m=re.match(r'^([A-Z]+):\s*(.+)$',t)
            if m:
                sub={'class':m.group(1).title(),'name':m.group(2).title(),'intro':Item('intro'),'features':[],'sidebars':[]}; subs.append(sub); item=sub['intro']; continue
        if sub is None: continue
        if k=='STAT': sidebar=Item(t); sub['sidebars'].append(sidebar); continue
        if k=='SIDEBAR' and sidebar is not None: sidebar.add(ln,tab); tab=False; continue
        if k=='SIDEHEAD': continue
        if k=='H_FEATURE':
            sidebar=None
            m=LVL.match(t)
            if m: item=Item(m.group(2).strip(),level=int(m.group(1))); sub['features'].append(item); tab=False; continue
            if item is not None: item.add({'text':t,'parts':[('b',t)]},True); tab=False
            continue
        if k in('BODY','META','SPELLMETA','OTHER','STAT_H') and item is not None:
            sidebar=None; item.add(ln,tab); tab=False
    return subs

SPELLHDR=re.compile(r'^(?:Level (\d) (\w+)|(\w+) Cantrip) \((.+)\)$')
def parse_spells():
    lines=[l for l in L['handbook'] if 163<=l['p']<=182]
    spells=[]; sp=None; tab=False; started=False
    for ln in lines:
        k=ln.get('k')
        if k=='TAB': tab=True; continue
        t=ln.get('text','').strip()
        if k=='H_SUBCLASSES' and t=='SPELL DESCRIPTIONS': started=True; continue
        if not started: continue
        if k=='H_FEATURE':
            sp={'name':t,'meta':'','props':{},'body':Item(t)}; spells.append(sp); tab=False; continue
        if sp is None: continue
        if k=='META' and not sp['meta']: sp['meta']=t; continue
        if k=='SPELLMETA':
            m=re.match(r'^(Casting Time|Range|Components|Duration):\s*(.*)$',t)
            if m: sp['props'][m.group(1)]=m.group(2); sp['_last']=m.group(1)
            else: sp['props'][sp['_last']]+=' '+t
            continue
        if k in('BODY','OTHER','STAT_H'): sp['body'].add(ln,tab); tab=False
    out=[]
    for s in spells:
        m=SPELLHDR.match(s['meta'])
        out.append({'name':s['name'],'level':int(m.group(1)) if m and m.group(1) else 0,'school':(m.group(2) or m.group(3)) if m else None,
            'classes':[c.strip() for c in m.group(4).split(',')] if m else [],'meta':s['meta'],'props':s['props'],'html':s['body'].html(),'text':s['body'].text()})
    return out

def ser_item(i):
    d={'name':i.name,'html':i.html(),'text':i.text()}
    for a in('level','prereq'):
        if hasattr(i,a): d[a]=getattr(i,a)
    return d

if __name__=='__main__':
    C=parse_handbook()
    res={'classes':{},'overdrive':[],'spells':parse_spells()}
    for n,c in C.items():
        res['classes'][n]={'name':n,'tagline':c['tagline'],'intro':ser_item(c['intro']),'features':[ser_item(f) for f in c['features']],
          'options':{k:[ser_item(o) for o in v] for k,v in c['options'].items()},'spelllist':c['spelllist'].text(),
          'sidebars':[ser_item(s) for s in c['sidebars']],
          'subclasses':[{'name':s['name'],'intro':ser_item(s['intro']),'features':[ser_item(f) for f in s['features']],'sidebars':[ser_item(x) for x in s['sidebars']]} for s in c['subclasses']]}
    for s in parse_overdrive():
        res['overdrive'].append({'class':s['class'],'name':s['name'],'intro':ser_item(s['intro']),'features':[ser_item(f) for f in s['features']],'sidebars':[ser_item(x) for x in s['sidebars']]})
    json.dump(res,open(os.path.expanduser('~/work/build/outline.json'),'w'),indent=1,ensure_ascii=False)
    for n,c in res['classes'].items():
        print(n,len(c['features']),{k:len(v) for k,v in c['options'].items()},[(s['name'],len(s['features'])) for s in c['subclasses']])
    print('overdrive',len(res['overdrive']),[(s['class'][:4],s['name'],len(s['features'])) for s in res['overdrive']])
    print('spells',len(res['spells']),sum(1 for s in res['spells'] if not s['classes']))
