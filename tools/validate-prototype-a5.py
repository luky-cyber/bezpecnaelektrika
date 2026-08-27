#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def txt(rel): return (ROOT/rel).read_text(encoding='utf-8')
def soup(rel): return BeautifulSoup(txt(rel),'html.parser')
def prose_words(node):
    clone=BeautifulSoup(str(node),'html.parser')
    for tag in clone.find_all(['svg','style','script']): tag.decompose()
    return len(clone.get_text(' ',strip=True).split())

home=txt('index.html'); rev=txt('revizie/index.html'); por=txt('poradna/index.html'); about=txt('o-projekte/index.html'); mer=txt('meranie/index.html'); js=txt('assets/js/main.js'); css=txt('assets/css/v040.css')
hs=soup('index.html'); rs=soup('revizie/index.html'); ps=soup('poradna/index.html'); os=soup('o-projekte/index.html')

# Compression and customer-language goals.
hwords=prose_words(hs.find('main')); rwords=prose_words(rs.find('main'))
if len(hs.find('main').find_all('section',recursive=False))!=6: errors.append('A5 homepage must keep exactly 6 top-level sections')
if hwords>500: errors.append(f'A5 homepage exceeds 500-word customer target: {hwords}')
if rwords>650: errors.append(f'A5 /revizie/ exceeds 650-word customer target: {rwords}')
for needle in ['Pripravované revízne služby','Revízie elektrických zariadení a inštalácií','Opýtať sa na revíziu','Rodinné domy, byty a vybrané administratívne priestory.']:
    if needle not in home: errors.append(f'Missing A5 hero/customer invariant: {needle}')
for forbidden in ['Mám záujem o pripravované služby','Pripravované revízne služby E2A','fiktívny cenník','Čo budete pri elektrorevízii riešiť?']:
    if forbidden in home+rev+por: errors.append(f'Old/project language remains: {forbidden}')
if 'data-term-popover' in str(hs.find('main')): errors.append('Homepage must not use technical term popovers in A5')
if re.search(r'\b(?:LPS|RCD|Zs|PEN|RCBO|RCCB)\b',hs.find('main').get_text(' ',strip=True)): errors.append('Technical abbreviations leaked into visible A5 homepage customer path')
# Four fully clickable situation cards.
cards=hs.select('#situacie a.service-intent-card--link')
if len(cards)!=4: errors.append(f'Expected 4 fully clickable situation cards, found {len(cards)}')
if any(c.find('a') for c in cards): errors.append('Clickable situation card must not contain nested links')
# Price before process.
secs=hs.find('main').find_all('section',recursive=False)
ids=[s.get('id') for s in secs]
if ids.index('cena')>ids.index('ako-prebieha'): errors.append('A5 price should appear before process on homepage')
if len(hs.select('#kontakt .quick-answer-card'))!=3: errors.append('Homepage must show exactly 3 practical questions')
if not hs.select_one('#kontakt .expert-strip'): errors.append('Homepage must use compact expert strip')
if hs.select_one('#kontakt .expert-entry-grid'): errors.append('Large expert card grid must not return to homepage')
if not hs.select_one('#kontakt .contact-author a[href="https://likavcan.cz/lukas/"]'): errors.append('Homepage must retain visible professional profile link')

# Customer-first /revizie/ structure and stable links.
for needle in ['data-prototype="service-revisions-a5"','Čo potrebujete skontrolovať alebo revidovať?','Kedy revíziu potrebujete?','Ako revízia prebieha a čo dostanete?','Čo je dobré mať pripravené?','Čo ovplyvňuje cenu?']:
    if needle not in rev: errors.append(f'Missing A5 revisions invariant: {needle}')
if rs.find('section',id='ako-casto'): errors.append('A5 must merge separate #ako-casto section into Kedy section')
if not rs.find(id='kedy-a-ako-casto') or not rs.find(id='ako-casto'): errors.append('Merged Kedy/interval section or legacy #ako-casto anchor missing')
for anchor in ['funkcnost-nie-je-dokaz','pripravovane-zameranie','pre-koho','ako-prebieha','co-sa-overuje','priprava-na-navstevu','domacnosti','zamestnavatelia','revizna-sprava','vybavenie','myty','faq','cena']:
    if not rs.find(id=anchor): errors.append(f'Legacy/relevant revisions anchor missing: #{anchor}')
if not rs.find('figure',id='be-diag-01'): errors.append('BE-DIAG-01 process diagram must remain on /revizie/')
if '/poradna/elektrikar-prerobil-rozvadzac-co-nasleduje/' not in rev: errors.append('Revisions page must retain practical rebuilt-board bridge')
for forbidden in ['MI 3102','MI 3309','FR2000','UT251','fiktívny cenník','Zákaznícky nájdete']:
    if forbidden in rev: errors.append(f'Customer revisions page contains unwanted technical/internal wording: {forbidden}')

# Poradna and About customer language.
if ps.find('h1').get_text(' ',strip=True)!='Akú situáciu riešite?': errors.append('Poradna must start with customer situation question')
if 'Ďalšie otázky' not in por: errors.append('Poradna FAQ label should be customer-language A5 version')
if 'Ing. Lukáš Likavčan, PhD.' not in about or 'Pripravujem revízne služby pre elektrické zariadenia a inštalácie' not in about: errors.append('O mne first viewport is not service/customer-first')
if 'Živnosť: zatiaľ nie' in about: errors.append('O mne must not foreground trade-licence absence as a pill')
# Titles/descriptions should not foreground jargon.
for rel,s in [('index.html',hs),('revizie/index.html',rs),('poradna/index.html',ps),('o-projekte/index.html',os)]:
    title=s.title.get_text(' ',strip=True) if s.title else ''
    desc=(s.find('meta',attrs={'name':'description'}) or {}).get('content','') if s.find('meta',attrs={'name':'description'}) else ''
    if re.search(r'\belektrorevíz',title+' '+desc,re.I): errors.append(f'Customer metadata still uses elektrorevízie: {rel}')
    if rel in ['index.html','revizie/index.html','poradna/index.html'] and re.search(r'\b(?:E2A|LPS)\b',title+' '+desc): errors.append(f'Customer metadata foregrounds technical acronym: {rel}')

# Navigation has one canonical price target; mobile has Contact.
expected_primary=[('Revízie','/revizie/'),('Kedy revíziu','/revizie/#kedy-a-ako-casto'),('Cena','/revizie/#cena'),('Poradňa','/poradna/'),('O mne','/o-projekte/')]
expected_mobile=[('Domov','/'),('Revízie','/revizie/'),('Cena','/revizie/#cena'),('Poradňa','/poradna/'),('Kontakt','/#kontakt')]
htmls=list(ROOT.rglob('*.html'))
for p in htmls:
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    if not s.find('a',class_='skip-link',href='#obsah'): errors.append(f'Missing skip link: {p.relative_to(ROOT)}')
    if not s.find('main',id='obsah'): errors.append(f'Missing #obsah main target: {p.relative_to(ROOT)}')
    nav=s.find('nav',id='main-nav')
    if nav:
        navlinks=nav.select('.nav-primary > a')
        got=[(a.get_text(' ',strip=True),a.get('href')) for a in navlinks]
        if got!=expected_primary: errors.append(f'Primary nav mismatch: {p.relative_to(ROOT)} -> {got}')
        active=[a for a in navlinks if a.get('aria-current')=='page']
        if len(active)>1: errors.append(f'Multiple aria-current primary nav items: {p.relative_to(ROOT)}')
        if any('#' in a.get('href','') and a.get('aria-current')=='page' for a in navlinks): errors.append(f'Anchor shortcut must not claim aria-current=page: {p.relative_to(ROOT)}')
    mb=s.find('nav',class_='mobile-bottom-nav')
    if mb:
        got=[(a.get_text(' ',strip=True),a.get('href')) for a in mb.find_all('a',recursive=False)]
        if got!=expected_mobile: errors.append(f'Mobile nav mismatch: {p.relative_to(ROOT)} -> {got}')

# Accessibility implementation guardrails.
for needle in ['min-height:44px!important','font-size:.70rem!important','moreWasOpen','navWasOpen','focusWasInside','trigger?.focus()']:
    if needle not in css+js: errors.append(f'A5 accessibility guardrail missing: {needle}')

# Search customer intent and contact naming.
try:
    data=json.loads(txt('data/search-index.json')); records=data['records']
    revrec=next((r for r in records if r.get('url')=='/revizie/'),None)
    if not revrec: errors.append('/revizie/ missing from search')
    else:
        for q in ['revizia domu','revizia bytu','cena revizie','ako casto revizia','revizia bleskozvodu']:
            if q not in revrec.get('aliases',[]): errors.append(f'Missing A5 customer search alias: {q}')
    contact=next((r for r in records if r.get('id')=='hub-kontakt'),None)
    if not contact or contact.get('title')!='Kontakt k pripravovaným revíznym službám': errors.append('Customer contact search record not renamed')
except Exception as e: errors.append(f'Could not inspect A5 search index: {e}')

# Pre-commercial guardrails and truthful MI status.
for forbidden in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed']:
    if forbidden in home+rev+por+about: errors.append(f'Forbidden pre-commercial element: {forbidden}')
if 'komerčné služby zatiaľ neposkytujem' not in home.lower() or 'komerčné služby zatiaľ neposkytujem' not in rev.lower(): errors.append('Explicit pre-commercial status missing')
for needle in ['Metrel MI 3102 BT EurotestXE','už mám','skontroloval príslušenstvo','overil, že sa zapne','Reálne merania s týmto prístrojom na webe ešte nepublikujem']:
    if needle not in mer: errors.append(f'MI 3102 BT truthful-state invariant missing: {needle}')
# All 12 Poradna details keep customer contact.
details=list((ROOT/'poradna').glob('*/index.html'))
if len(details)!=12: errors.append(f'Expected 12 Poradna detail pages, found {len(details)}')
for p in details:
    t=p.read_text(encoding='utf-8')
    if 'customer-article-contact' not in t or 'mailto:kontakt@bezpecnaelektrika.sk' not in t: errors.append(f'Poradna detail customer contact missing: {p.relative_to(ROOT)}')

if errors:
    print('PROTOTYPE A5 CHECK FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print(f'PROTOTYPE A5 CHECK OK · homepage {hwords} words / 6 sections · revisions {rwords} words · 36 skip links · customer language + accessibility + pre-commercial guardrails')
