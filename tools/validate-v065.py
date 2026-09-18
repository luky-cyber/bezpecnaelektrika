#!/usr/bin/env python3
from pathlib import Path
import json,re,sys,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
errors=[]
def text(rel): return (ROOT/rel).read_text(encoding='utf-8')

# Release identity.
readme=text('README.md')

try:
    m=re.match(r'^# Bezpečná elektrika v(\d+)\.(\d+)\.(\d+)', readme)
    current=tuple(map(int,m.groups())) if m else (0,0,0)
    if current < (0,6,5): errors.append('README must identify v0.6.5 or later')
except Exception:
    errors.append('Could not parse README release version')
if '## v0.6.5 – Odborná spôsobilosť a overený odborný obsah' not in readme: errors.append('README v0.6.5 RC2 summary missing')
try:
    v=json.loads(text('version.json'))
    if v.get('project')!='Bezpečná elektrika': errors.append('version.json project mismatch')
    vm=re.match(r'^(\d+)\.(\d+)\.(\d+)$',str(v.get('version','')))
    vv=tuple(map(int,vm.groups())) if vm else (0,0,0)
    if vv < (0,6,5): errors.append('version.json must be v0.6.5 or later')
    rel=str(v.get('release','')); base=f"v{v.get('version')}"
    if not (rel==base or re.match(r'^'+re.escape(base)+r'-rc\d+$',rel)): errors.append('version.json release/version mismatch')
    if not v.get('fingerprint'): errors.append('version.json fingerprint missing')
except Exception as e: errors.append(f'Invalid version.json: {e}')

# Public certificate assets remain privacy-safe.
full=ROOT/'assets/img/osvedcenie-e2a-lukas-likavcan-verejna-kopia.webp'
preview=ROOT/'assets/img/osvedcenie-e2a-lukas-likavcan-verejna-kopia-preview.webp'
for p in [full,preview]:
    if not p.is_file(): errors.append(f'Missing certificate asset: {p.relative_to(ROOT)}')
try:
    from PIL import Image
    if full.is_file():
        with Image.open(full) as im:
            if im.size!=(1097,1536): errors.append(f'Full certificate dimensions changed: {im.size}')
            if im.getexif(): errors.append('Full certificate must not contain EXIF metadata')
    if preview.is_file():
        with Image.open(preview) as im:
            if im.size!=(640,896): errors.append(f'Certificate preview dimensions changed: {im.size}')
            if im.getexif(): errors.append('Certificate preview must not contain EXIF metadata')
except Exception as e: errors.append(f'Certificate image check failed: {e}')

about=text('o-projekte/index.html')
for needle in ['Osvedčenie revízneho technika · E2/A','Zverejnená je 1. strana osvedčenia.','Dátum narodenia, trvalý pobyt a podpis boli redigované.','Verejná kópia nenahrádza originál dokumentu.','data-credential-open','id="credential-viewer"','data-credential-zoom','data-credential-image','/assets/js/credential-viewer.js']:
    if needle not in about: errors.append(f'O mne credential/viewer marker missing: {needle}')
viewer=text('assets/js/credential-viewer.js')
for needle in ['showModal','is-native','Prispôsobiť','100 % · natívna veľkosť','dialog.close()']:
    if needle not in viewer: errors.append(f'Credential viewer behavior missing: {needle}')
for rel in ['assets/css/components.css','assets/css/style.css']:
    css=text(rel)
    for needle in ['.credential-evidence{','.credential-viewer{','.credential-viewer.is-native','.podcast-transcript{']:
        if needle not in css: errors.append(f'Missing RC2 CSS in {rel}: {needle}')

# Credential schema remains non-commercial and stable.
for needle in ['"hasCredential"','"@type":"EducationalOccupationalCredential"','"credentialCategory":"E2/A"','"dateCreated":"2026-08-20"']:
    if needle not in about: errors.append(f'Credential JSON-LD marker missing: {needle}')
allhtml='\n'.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html'))
for bad in ['"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed','href="tel:']:
    if bad in allhtml: errors.append(f'Forbidden Commercial Switch marker: {bad}')

# Meaningful dates: O mne keeps 8 Sep; podcast content and map use 11 Sep.
if '"dateModified":' not in about: errors.append('O mne page-level dateModified missing')
if current==(0,6,5) and '"dateModified":"2026-09-11"' not in text('podcast/index.html'): errors.append('Podcast hub dateModified must be 2026-09-11')
if current==(0,6,5) and '"dateModified":"2026-09-11"' not in text('obsah/index.html'): errors.append('Content map dateModified must be 2026-09-11')

# Four standalone reviewed episode pages.
eps={
'BE-001':'be-001-preco-nestaci-ze-elektrina-funguje',
'BE-002':'be-002-merat-nie-hadat',
'BE-003':'be-003-namerana-hodnota-este-nie-je-vysledok',
'BE-004':'be-004-revizna-sprava-nie-je-len-papier',
}
for eid,slug in eps.items():
    rel=f'podcast/{slug}/index.html'
    p=ROOT/rel
    if not p.is_file(): errors.append(f'Missing episode page: {rel}'); continue
    raw=p.read_text(encoding='utf-8')
    soup=BeautifulSoup(raw,'html.parser')
    canonical=f'https://bezpecnaelektrika.sk/podcast/{slug}/'
    if not soup.find('link',rel='canonical',href=canonical): errors.append(f'{eid} canonical mismatch')
    for needle in ['id="audio"','id="prepis"','id="odborne-spresnenia"','id="zdroje"','Ako vznikol transcript:','Vecná kontrola:','Redakčné odborné spresnenia','Podcast a transcript majú edukačný charakter','"@type":"PodcastEpisode"','"@type":"AudioObject"','"dateModified":']:
        if needle not in raw: errors.append(f'{eid} missing marker: {needle}')
    for forbidden in ['[OVERIŤ V AUDIU]','[VECNE OVERIŤ]']:
        if forbidden in raw: errors.append(f'{eid} leaked internal marker: {forbidden}')

# Critical technical guardrails in editorial corrections.
e3=text('podcast/be-003-namerana-hodnota-este-nie-je-vysledok/index.html')
for needle in ['Zs ≠ Zline','Zline a Zs nie sú zameniteľné merania','Tlačidlo TEST nie je iba skúškou mechaniky','používateľská funkčná skúška samotného RCD','Úspešný TEST však neoveruje celú elektroinštaláciu']:
    if needle not in e3: errors.append(f'BE-003 guardrail missing: {needle}')
e1=text('podcast/be-001-preco-nestaci-ze-elektrina-funguje/index.html')
if 'Zs je impedancia, nie iba odpor' not in e1: errors.append('BE-001 Zs correction missing')
e2=text('podcast/be-002-merat-nie-hadat/index.html')
if 'skúšobné jednosmerné napätie' not in e2: errors.append('BE-002 insulation-resistance correction missing')
e4=text('podcast/be-004-revizna-sprava-nie-je-len-papier/index.html')
if 'Revízia nie je automaticky opravou' not in e4: errors.append('BE-004 revision/repair boundary missing')

# Verified audio passages are represented in public transcripts.
for rel,needle in [
('podcast/be-001-preco-nestaci-ze-elektrina-funguje/index.html','zaklínadlo z Harryho potra'),
('podcast/be-002-merat-nie-hadat/index.html','Je úplne nepozorovane prerežú izoláciu až na meď.'),
('podcast/be-003-namerana-hodnota-este-nie-je-vysledok/index.html','povedzme 38,5'),
('podcast/be-003-namerana-hodnota-este-nie-je-vysledok/index.html','Ale ak ten istý prístroj ukáže'),
('podcast/be-004-revizna-sprava-nie-je-len-papier/index.html','A povedzme si to úplne úprimne.'),
('podcast/be-004-revizna-sprava-nie-je-len-papier/index.html','Z krátkej cesty, nezaznamenalo.'),
]:
    if needle not in text(rel): errors.append(f'Audio-verified passage missing in {rel}: {needle}')

# Podcast data, RSS, sitemap, search, content map and llms sync.
pdata=json.loads(text('data/podcasts.json'))
if pdata.get('version',0)<4: errors.append('podcasts.json version must be 4 or later')
for ep in pdata.get('episodes',[]):
    eid=ep.get('id')
    if eid in eps and ep.get('page')!=f'/podcast/{eps[eid]}/': errors.append(f'{eid} page link missing from podcasts.json')
feed=text('podcast/feed.xml')
for eid,slug in eps.items():
    if f'https://bezpecnaelektrika.sk/podcast/{slug}/' not in feed: errors.append(f'{eid} canonical link missing from RSS')
try:
    tree=ET.parse(ROOT/'sitemap.xml'); ns={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    entries={u.find('sm:loc',ns).text:(u.find('sm:lastmod',ns).text if u.find('sm:lastmod',ns) is not None else '') for u in tree.findall('.//sm:url',ns)}
    if 'https://bezpecnaelektrika.sk/hladat/' in entries: errors.append('/hladat/ must stay outside sitemap')
    if not entries.get('https://bezpecnaelektrika.sk/o-projekte/'): errors.append('O mne sitemap entry/lastmod missing')
    if current==(0,6,5) and entries.get('https://bezpecnaelektrika.sk/podcast/')!='2026-09-11': errors.append('Podcast hub sitemap lastmod must be 2026-09-11')
    if current==(0,6,5) and entries.get('https://bezpecnaelektrika.sk/obsah/')!='2026-09-11': errors.append('Content map sitemap lastmod must be 2026-09-11')
    for eid,slug in eps.items():
        if not entries.get(f'https://bezpecnaelektrika.sk/podcast/{slug}/'): errors.append(f'{eid} sitemap entry/lastmod missing')
except Exception as e: errors.append(f'Could not verify sitemap: {e}')
index=text('data/search-index.json')
for eid,slug in eps.items():
    if f'/podcast/{slug}/' not in index: errors.append(f'{eid} missing from search index')
if '37 records' in index: pass
if not re.search(r'epizódy BE-001 až BE-00[4-9] majú samostatné stránky',text('llms.txt')): errors.append('llms podcast transcript pointer missing')
maphtml=text('obsah/index.html')
for slug in eps.values():
    if f'/podcast/{slug}/' not in maphtml: errors.append(f'Content map missing podcast page: {slug}')

# Search/runtime certificate status remains synchronized.
builder=text('tools/build-search-index.py'); index=text('data/search-index.json')
for runtime,name in [(builder,'build-search-index.py'),(index,'data/search-index.json')]:
    if 'čakám na osvedčenie' in runtime.lower(): errors.append(f'Stale certificate wait-state remains in {name}')
if 'osvedčenie je vydané' not in builder: errors.append('Search revisions summary must say certificate is issued')

if errors:
    print('V0.6.5 CHECK FAILED')
    for e in sorted(set(errors)): print(' -',e)
    sys.exit(1)
print('V0.6.5 CHECK OK · credential viewer + four reviewed podcast transcripts + technical corrections + schema/RSS/search/sitemap sync + pre-commercial guardrails')
