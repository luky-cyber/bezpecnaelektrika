#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def text(rel): return (ROOT/rel).read_text(encoding='utf-8')

css=text('assets/css/v040.css')
home=text('index.html'); rev=text('revizie/index.html'); search=text('assets/js/search.js')
prep=text('poradna/co-pripravit-pred-reviziou/index.html')

# Full homepage image: later v0.6.2 override must neutralize fixed-height cover behavior.
block=re.search(r'/\* ===== v0\.6\.2 UX \+ discovery polish ===== \*/(.*)',css,re.S)
if not block: errors.append('Missing v0.6.2 CSS block')
else:
    b=block.group(1)
    for needle in ['[data-prototype="service-home-a5"] .service-hero-visual','height:auto','object-fit:contain','max-height:none']:
        if needle not in b: errors.append(f'Missing full-image guardrail: {needle}')
    # In the homepage subsection itself, no later cover override may reappear.
    home_part=b.split('/* Revisions hero:',1)[0]
    if 'object-fit:cover' in home_part: errors.append('Homepage v0.6.2 block must not crop with object-fit:cover')

# Revisions logo uses scoped CSS, not old inline sizing.
rs=BeautifulSoup(rev,'html.parser')
mark=rs.select_one('[data-prototype="service-revisions-a5"] .service-hero-logo')
if not mark: errors.append('Missing service-hero-logo class on Revisions hero')
else:
    if mark.get('style'): errors.append('Revisions hero logo must not use inline box sizing')
    img=mark.find('img')
    if not img or img.get('style'): errors.append('Revisions hero logo image must use scoped CSS, not inline sizing')
for needle in ['.service-hero-logo','width:clamp(218px,18vw,252px)','height:86%']:
    if needle not in css: errors.append(f'Missing Revisions logo balance CSS: {needle}')

# Enter behavior and help copy.
for needle in ['const openFirstResult = async','event.key === "Enter" && event.target === overlayInput','input.addEventListener("keydown"','openFirstResult(input, results, live, tracking)','<kbd>Enter</kbd> otvorí prvý výsledok']:
    if needle not in search and needle not in text('hladat/index.html'): errors.append(f'Missing search Enter UX: {needle}')

# Discovery pilot preserves one canonical URL and materially updates the existing answer.
ps=BeautifulSoup(prep,'html.parser')
canonical=ps.find('link',rel='canonical')
if not canonical or canonical.get('href')!='https://bezpecnaelektrika.sk/poradna/co-pripravit-pred-reviziou/': errors.append('Preparation answer canonical changed or missing')
if (ps.find('h1') or {}).get_text(' ',strip=True)!='Čo pripraviť pred revíziou elektroinštalácie?': errors.append('Preparation H1 mismatch')
for needle in ['1. Dokumentácia, ak existuje','Môže byť potrebné prerušiť napájanie?','Čo pred revíziou netreba robiť','IEC 60364-6:2016','Vyhláška č. 508/2009 Z. z.','dateModified":"2026-08-28']:
    if needle not in prep: errors.append(f'Missing discovery-pilot content: {needle}')
if '/poradna/co-pripravit-pred-reviziou-elektroinstalacie/' in ''.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html')): errors.append('Do not create a duplicate preparation URL')
if '/poradna/co-pripravit-pred-reviziou/' not in rev: errors.append('Revisions page must link to the detailed preparation answer')

# Search index and sitemap carry the pilot without changing privacy semantics.
try:
    data=json.loads(text('data/search-index.json'))
    rec=next((r for r in data.get('records',[]) if r.get('url')=='/poradna/co-pripravit-pred-reviziou/'),None)
    if not rec: errors.append('Preparation answer missing from search index')
    else:
        for alias in ['co treba k revizii','priprava na reviziu','dokumenty k revizii']:
            if alias not in rec.get('aliases',[]): errors.append(f'Missing preparation search alias: {alias}')
except Exception as e: errors.append(f'Could not parse search index: {e}')
sm=text('sitemap.xml')
if not re.search(r'<loc>https://bezpecnaelektrika\.sk/poradna/co-pripravit-pred-reviziou/</loc>\s*<lastmod>2026-08-28</lastmod>',sm): errors.append('Preparation sitemap lastmod must be 2026-08-28')
if 'search_term' in search: errors.append('Search JS must not send the search term to analytics')


# Audit hardening before publication: narrow-screen News, Poradna popovers and
# WCAG AA contrast for the v0.4+ light-theme design tokens.
def luminance(hex_color):
    h=hex_color.lstrip('#')
    vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    vals=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in vals]
    return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]

def contrast(a,b):
    l1,l2=sorted((luminance(a),luminance(b)),reverse=True)
    return (l1+.05)/(l2+.05)

if '.news-card{min-width:0;' not in css:
    errors.append('News cards must allow grid items to shrink at 320px')
if '.news-meta{display:flex;flex-wrap:wrap;' not in css:
    errors.append('News metadata must wrap on narrow screens')
if '@media(min-width:621px) and (max-width:1100px)' not in css:
    errors.append('Poradna popover viewport anchoring must cover 621–1100px')
if '.term-popover:hover .term-popover__bubble' not in css:
    errors.append('Popover hover transform must be neutralized in viewport-anchored range')

light=re.search(r'html\[data-theme="light"\]\{([^}]*)\}',css,re.S)
if not light:
    errors.append('Could not parse v0.4 light-theme token block')
else:
    tokens=dict(re.findall(r'--(c-(?:bg|surface|surface-2|surface-3|subtle|accent)):(#[0-9a-fA-F]{6})',light.group(1)))
    for key in ['c-bg','c-surface','c-surface-2','c-surface-3','c-subtle','c-accent']:
        if key not in tokens: errors.append(f'Missing light-theme contrast token: {key}')
    if all(k in tokens for k in ['c-bg','c-surface','c-surface-2','c-surface-3','c-subtle','c-accent']):
        for fg in ['c-subtle','c-accent']:
            for bg in ['c-bg','c-surface','c-surface-2','c-surface-3']:
                ratio=contrast(tokens[fg],tokens[bg])
                if ratio < 4.5:
                    errors.append(f'Light-theme {fg} contrast vs {bg} below 4.5:1 ({ratio:.2f})')

# Pre-commercial truthfulness remains intact.
allhtml=''.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html'))
for bad in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed','href="tel:']:
    if bad in allhtml: errors.append(f'Forbidden pre-commercial element: {bad}')

# Production CSS must still be generated, not hand-edited.
try:
    proc=subprocess.run([sys.executable,str(ROOT/'tools/build-css.py'),'--check'],cwd=ROOT,text=True,capture_output=True,timeout=20)
    if proc.returncode: errors.append('CSS build check failed: '+proc.stdout.replace('\n',' | '))
except Exception as e: errors.append(f'Could not run CSS check: {e}')

if errors:
    print('V0.6.2 CHECK FAILED')
    for e in sorted(set(errors)): print(' -',e)
    sys.exit(1)
print('V0.6.2 CHECK OK · hero + Revisions logo + Enter search + discovery pilot + responsive/contrast hardening')
