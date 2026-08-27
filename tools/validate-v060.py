#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
errors=[]
PERSON='https://likavcan.cz/lukas/#lukas-likavcan'
PROJECT='https://bezpecnaelektrika.sk/#project'
PROJECT_DESC='Bezpečná elektrika pripravuje revízne služby pre elektrické zariadenia a inštalácie a zároveň ponúka praktický a odborný obsah o elektrickej bezpečnosti.'

def text(rel): return (ROOT/rel).read_text(encoding='utf-8')
def jsonlds(p):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    out=[]
    for sc in s.find_all('script',{'type':'application/ld+json'}):
        try: out.append(json.loads(sc.string or sc.get_text()))
        except Exception as e: errors.append(f'Invalid JSON-LD in {p.relative_to(ROOT)}: {e}')
    return out

def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x,list):
        for v in x: yield from walk(v)

def luminance(h):
    h=h.lstrip('#')
    vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    vals=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in vals]
    return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
def contrast(a,b):
    l1,l2=sorted((luminance(a),luminance(b)),reverse=True)
    return (l1+.05)/(l2+.05)

home=text('index.html'); rev=text('revizie/index.html'); glos=text('glosar/index.html'); css=text('assets/css/components.css'); v40=text('assets/css/v040.css')
hs=BeautifulSoup(home,'html.parser'); rs=BeautifulSoup(rev,'html.parser')
main=hs.find('main')

# Customer-first architecture and pre-commercial truthfulness.
if not main or len(main.find_all('section',recursive=False))!=6: errors.append('Homepage must keep six top-level customer-first sections')
if main and len(main.get_text(' ',strip=True).split())>500: errors.append('Homepage customer copy exceeded 500 words')
if (hs.find('h1') or {}).get_text(' ',strip=True)!='Revízie elektrických zariadení a inštalácií': errors.append('Homepage service-first H1 changed')
if main and re.search(r'\b(?:LPS|RCD|Zs|PEN|RCBO|RCCB)\b',main.get_text(' ',strip=True)): errors.append('Technical acronym leaked into homepage customer path')
if 'service-intent-no' in home: errors.append('Alternative situation cards must not be numbered 01–04')
for rel,txt in [('home',home),('revisions',rev)]:
    for needle in ['Opýtať sa na revíziu','Služby zatiaľ nie sú spustené.','Rozsah odbornej spôsobilosti: E2A']:
        if needle not in txt: errors.append(f'{rel}: missing final customer/status invariant: {needle}')
    if 'komerčné služby zatiaľ neposkytujem' not in txt.lower(): errors.append(f'{rel}: missing explicit non-commercial status')
for bad in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed','href="tel:']:
    for p in ROOT.rglob('*.html'):
        if bad in p.read_text(encoding='utf-8'): errors.append(f'Forbidden pre-commercial element {bad} in {p.relative_to(ROOT)}')

# Titles / intent.
ht=(hs.find('title') or {}).get_text(strip=True); rt=(rs.find('title') or {}).get_text(strip=True)
if ht==rt: errors.append('Homepage and /revizie/ must have distinct <title> values')
if rt!='Revízie: rozsah, priebeh a cena | Bezpečná elektrika': errors.append('Unexpected final /revizie/ title')

# MI 3102 truthfulness in Glosar.
if 'Čím to meriame / overujeme' in glos: errors.append('Glosar still implies already-performed measurements via old heading')
for needle in ['Ako sa to dá merať / overovať','nejde automaticky o záznam už vykonaného merania','Reálne merania dokumentujeme samostatne v Meraní v praxi']:
    if needle not in glos: errors.append(f'Glosar missing MI/equipment truthfulness guardrail: {needle}')

# Schema semantics and Project identity.
project_descs=[]
for p in ROOT.rglob('*.html'):
    for data in jsonlds(p):
        for d in walk(data):
            if d.get('@id')==PROJECT and d.get('@type')=='Project': project_descs.append((p,d.get('description')))
            pub=d.get('publisher')
            if isinstance(pub,dict) and pub.get('@id')==PROJECT: errors.append(f'Project used as publisher in {p.relative_to(ROOT)}')
if project_descs and any(desc!=PROJECT_DESC for _,desc in project_descs): errors.append('Project description is not normalized sitewide')

# FAQ visible vs JSON-LD.
faqsec=rs.find('section',id='faq'); visible=[]
if faqsec:
    for d in faqsec.find_all('details'):
        q=d.find('summary'); a=d.find('p')
        if q and a: visible.append((q.get_text(' ',strip=True),a.get_text(' ',strip=True)))
faqnode=None
for data in jsonlds(ROOT/'revizie/index.html'):
    for d in walk(data):
        if d.get('@type')=='FAQPage': faqnode=d
if not faqnode: errors.append('Missing FAQPage JSON-LD on /revizie/')
else:
    structured=[(q.get('name',''),(q.get('acceptedAnswer') or {}).get('text','')) for q in faqnode.get('mainEntity',[])]
    if structured!=visible: errors.append('FAQPage JSON-LD does not match visible /revizie/ FAQ')

# Accessibility/color/performance final fixes.
m=re.search(r'html\[data-theme="light"\]\{[^}]*--bg:(#[0-9a-fA-F]{6})[^}]*--subtle:(#[0-9a-fA-F]{6})',css)
if not m: errors.append('Could not parse light-theme bg/subtle colors')
else:
    c=contrast(m.group(2),m.group(1))
    if c<4.5: errors.append(f'Light-theme subtle contrast below 4.5:1 ({c:.2f})')
if 'bezpecna-elektrika-logo.png' in rev or 'bezpecna-elektrika-logo.png' in text('o-projekte/index.html'): errors.append('Large PNG logo still used in small profile card')
small=ROOT/'assets/img/bezpecna-elektrika-logo-card.webp'
if not small.is_file(): errors.append('Missing optimized profile logo WebP')
elif small.stat().st_size>100_000: errors.append('Optimized profile logo is unexpectedly large')
for p in ROOT.rglob('*.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    for img in s.find_all('img'):
        src=img.get('src','')
        if src.startswith('/') and not src.startswith('//') and (ROOT/src.lstrip('/')).exists():
            if not img.get('width') or not img.get('height'): errors.append(f'Missing intrinsic dimensions: {p.relative_to(ROOT)} -> {src}')

# Poradna active state + breadcrumb.
for p in sorted((ROOT/'poradna').glob('*/index.html')):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    nav=s.select_one('.nav-primary')
    a=nav.find('a',href='/poradna/') if nav else None
    if not a or a.get('aria-current')!='page' or 'active' not in (a.get('class') or []): errors.append(f'Poradna desktop active state missing: {p.relative_to(ROOT)}')
# Check breadcrumb through parsed data directly.
crumb_ok=False
for data in jsonlds(ROOT/'o-projekte/index.html'):
    for d in walk(data):
        if d.get('@type')=='BreadcrumbList':
            for i in d.get('itemListElement',[]):
                if i.get('item')=='https://bezpecnaelektrika.sk/o-projekte/' and i.get('name')=='O mne': crumb_ok=True
if not crumb_ok: errors.append('O mne breadcrumb not normalized')

# Analytics placements: meaningful and consent-first event names remain.
cons=text('assets/js/consent.js'); privacy=text('ochrana-sukromia/index.html')
for ev in ['service_interest_click','price_interest_click','service_situation_click','expert_content_click']:
    if ev not in cons or ev not in privacy: errors.append(f'Missing consent/privacy coverage for {ev}')
for placement in ['home_hero','home_hero_email','home_end','revisions_hero','revisions_hero_email','revisions_price','revisions_end','advice_hero','advice_end']:
    if f'data-service-interest="{placement}"' not in ''.join(p.read_text(encoding='utf-8') for p in [ROOT/'index.html',ROOT/'revizie/index.html',ROOT/'poradna/index.html']): errors.append(f'Missing expected analytics placement: {placement}')
for stale in ['data-service-interest="revisions"','data-service-interest="advice_hub"']:
    if any(stale in p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html')): errors.append(f'Stale coarse analytics placement remains: {stale}')

# Final release identity/docs.
if not text('README.md').startswith('# Bezpečná elektrika v0.6.0'): errors.append('README does not identify final v0.6.0')
if not (ROOT/'RELEASE-v0.6.0.md').is_file(): errors.append('Missing RELEASE-v0.6.0.md')
if 'python tools/validate-v060.py' not in text('docs/RELEASE-CHECKLIST.md'): errors.append('Release checklist does not include final validator')

if errors:
    print('V0.6.0 CHECK FAILED')
    for e in sorted(set(errors)): print(' -',e)
    sys.exit(1)
print(f'V0.6.0 CHECK OK · homepage {len(main.get_text(" ",strip=True).split())} words · final-fix + service-first + pre-commercial guardrails')
