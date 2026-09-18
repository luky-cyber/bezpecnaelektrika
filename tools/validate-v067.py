#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,subprocess,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def text(rel): return (ROOT/rel).read_text(encoding='utf-8')

# Release identity (v0.6.7 baseline must remain valid in later releases).
readme=text('README.md')
m=re.match(r'^# Bezpečná elektrika v(\d+)\.(\d+)\.(\d+)',readme)
current=tuple(map(int,m.groups())) if m else (0,0,0)
if current < (0,6,7): errors.append('README must identify v0.6.7 or later')
if '## v0.6.7 – Content graph & query gaps' not in readme: errors.append('README v0.6.7 summary missing')
try:
    v=json.loads(text('version.json')); vm=re.match(r'^(\d+)\.(\d+)\.(\d+)$',str(v.get('version',''))); vv=tuple(map(int,vm.groups())) if vm else (0,0,0)
    if vv < (0,6,7): errors.append('version.json must be v0.6.7 or later')
    if not v.get('fingerprint'): errors.append('version.json fingerprint missing')
except Exception as e: errors.append(f'Invalid version.json: {e}')
for rel in ['RELEASE-v0.6.7.md','tools/audit-content-graph.py','docs/CONTENT-GRAPH-REPORT-v0.6.7.md','poradna/ako-citat-reviznu-spravu/index.html']:
    if not (ROOT/rel).is_file(): errors.append(f'Missing v0.6.7 artifact: {rel}')

# Desktop QR scanability; mobile guardrail preserved.
css=text('assets/css/v040.css')
for needle in ['max-width:640px','.about-contact-compact__qr{width:168px','width:min(188px,58vw)']:
    if needle not in css: errors.append(f'QR sizing guardrail missing: {needle}')

# New how-to intent is distinct and integrated.
new=text('poradna/ako-citat-reviznu-spravu/index.html')
for needle in ['<h1>Ako čítať revíznu správu?</h1>','id="rozsah"','id="identifikacia"','id="zistenia"','id="zaver"','id="co-dalej"','id="hranice"','Stručne:','/podcast/be-004-revizna-sprava-nie-je-len-papier/']:
    if needle not in new: errors.append(f'New report-reading page missing: {needle}')
if 'https://bezpecnaelektrika.sk/poradna/ako-citat-reviznu-spravu/' not in text('sitemap.xml'):
    errors.append('New report-reading page missing from sitemap')
if '/poradna/ako-citat-reviznu-spravu/' not in text('obsah/index.html'):
    errors.append('New report-reading page missing from content map')
if '/poradna/ako-citat-reviznu-spravu/' not in text('poradna/index.html'):
    errors.append('New report-reading page missing from Poradna hub')
if '/poradna/ako-citat-reviznu-spravu/' not in text('poradna/co-obsahuje-revizna-sprava/index.html'):
    errors.append('Existing report page must point to practical reading guide')

# Article.image only where a relevant owned visual already exists.
images={
 'glosar/rcd-prudovy-chranic/index.html':'https://bezpecnaelektrika.sk/assets/img/og/og-rcd-v1.jpg',
 'glosar/impedancia-poruchovej-slucky-zs/index.html':'https://bezpecnaelektrika.sk/assets/img/og/og-zs-v1.jpg',
 'glosar/lps-ochrana-pred-bleskom/index.html':'https://bezpecnaelektrika.sk/assets/img/og/og-lps-v1.jpg',
}
for rel,want in images.items():
    soup=BeautifulSoup(text(rel),'html.parser'); sc=soup.find('script',type='application/ld+json')
    try:
        data=json.loads(sc.string); art=next(x for x in data['@graph'] if x.get('@type')=='Article')
        if art.get('image')!=[want]: errors.append(f'Article.image mismatch in {rel}: {art.get("image")}')
    except Exception as e: errors.append(f'Article.image parse failed in {rel}: {e}')

# Canonical topic graph: deepen existing destinations instead of duplicate pages.
if '/podcast/be-003-namerana-hodnota-este-nie-je-vysledok/#odborne-spresnenia' not in text('glosar/impedancia-poruchovej-slucky-zs/index.html'):
    errors.append('Zs page missing contextual BE-003 deep link')
if '/podcast/be-003-namerana-hodnota-este-nie-je-vysledok/#odborne-spresnenia' not in text('glosar/rcd-prudovy-chranic/index.html'):
    errors.append('RCD page missing contextual BE-003 deep link')
if '/podcast/be-001-preco-nestaci-ze-elektrina-funguje/' not in text('poradna/preco-zasuvka-funguje-a-instalacia-nemusi-byt-v-poriadku/index.html'):
    errors.append('Functionality advice missing contextual BE-001 link')
if 'href="/podcast/be-002-merat-nie-hadat/">BE-002' not in text('meranie/index.html'):
    errors.append('Meranie must link directly to BE-002 episode')

# Search/query-gap decisions.
builder=text('tools/build-search-index.py')
for needle in ['"/poradna/ako-citat-reviznu-spravu/"','"ako citat reviznu spravu"','"citanie reviznej spravy"']:
    if needle not in builder: errors.append(f'Search curated intent missing: {needle}')
try:
    r=subprocess.run([sys.executable,str(ROOT/'tools/test-search-index.py')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if r.returncode: errors.append('Search smoke test failed under v0.6.7')
except Exception as e: errors.append(f'Search test invocation failed: {e}')

# Graph report must be reproducible and have no expert page with <=1 main-content inbound links.
try:
    r=subprocess.run([sys.executable,str(ROOT/'tools/audit-content-graph.py')],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if r.returncode: errors.append('Content graph audit script failed')
except Exception as e: errors.append(f'Content graph invocation failed: {e}')
report=text('docs/CONTENT-GRAPH-REPORT-v0.6.7.md')
for needle in ['Zs ≠ Zline','TEST RCD','Ako čítať revíznu správu','None at the ≤1 inbound-link threshold.']:
    if needle not in report: errors.append(f'Content graph decision/report missing: {needle}')

# Counts and indexability: exactly one new HTML page vs v0.6.6.
html_count=sum(1 for _ in ROOT.rglob('*.html'))
if html_count<41: errors.append(f'Expected at least 41 HTML files, got {html_count}')
try:
    tree=ET.parse(ROOT/'sitemap.xml'); ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls=[e.text for e in tree.findall('.//s:loc',ns)]
    if len(urls)<39: errors.append(f'Expected at least 39 sitemap URLs, got {len(urls)}')
    if 'https://bezpecnaelektrika.sk/hladat/' in urls: errors.append('/hladat/ must remain outside sitemap')
except Exception as e: errors.append(f'Sitemap parse failed: {e}')
try:
    idx=json.loads(text('data/search-index.json'))
    if len(idx.get('records',[]))<38: errors.append(f'Expected at least 38 search records, got {len(idx.get("records",[]))}')
except Exception as e: errors.append(f'Search index parse failed: {e}')

# Content dates only where content genuinely changed/new; technical pages keep their earlier dates.
if '<lastmod>2026-09-11</lastmod>' not in text('sitemap.xml'): errors.append('Expected v0.6.7 content lastmod missing')
if current==(0,6,7):
    for rel in images:
        if '2026-08-31' not in text(rel): errors.append(f'Article.image-only change must not churn content date in {rel}')

# Pre-commercial and search-page invariants.
allhtml='\n'.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html'))
for bad in ['"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed','href="tel:']:
    if bad in allhtml: errors.append(f'Forbidden Commercial Switch marker: {bad}')
if 'noindex,follow' not in text('hladat/index.html'): errors.append('/hladat/ must remain noindex,follow')
if '/poradna/ako-citat-reviznu-spravu/' in text('llms.txt'):
    errors.append('llms.txt must not become a page-by-page sitemap')

# Generated CSS synchronized.
r=subprocess.run([sys.executable,str(ROOT/'tools/build-css.py'),'--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
if r.returncode: errors.append('Generated CSS is not synchronized')

if errors:
    print('V0.6.7 CHECK FAILED')
    for e in sorted(set(errors)): print(' -',e)
    sys.exit(1)
print('V0.6.7 CHECK OK · QR scanability + graph/query-gap audit + contextual links + report-reading intent + Article.image pass + search routing + pre-commercial guardrails')
