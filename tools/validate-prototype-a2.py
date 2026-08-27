#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
home=(ROOT/'index.html').read_text(encoding='utf-8')
mer=(ROOT/'meranie/index.html').read_text(encoding='utf-8')
rev=(ROOT/'revizie/index.html').read_text(encoding='utf-8')

# Homepage structure / service-first constraints.
required_home=[
    'data-prototype="service-home-a2"',
    'id="kedy-revizia"', 'id="ako-casto"', 'id="co-dostanete"',
    'id="ako-prebieha"', 'id="najcastejsie-otazky"', 'id="cena"',
    'Rýchla odpoveď. Detail o klik ďalej.',
    '/glosar/lps-ochrana-pred-bleskom/',
    '/poradna/prudovy-chranic-opakovane-vypina/',
    '/poradna/hlinikova-elektroinstalacia/',
    '/meranie/#veliciny',
]
for x in required_home:
    if x not in home: errors.append(f'Missing A2 homepage invariant: {x}')
if 'brand-principles-section' in home or '<div class="eyebrow">Ako k tomu pristupujem</div>' in home:
    errors.append('A2 must not restore the large standalone brand-principles section')
if home.count('quick-answer-card') < 6:
    errors.append('A2 homepage must expose at least six quick-answer bridges')

# Glosar must be one-tap/one-click in both nav layers wherever those navs exist.
for p in ROOT.rglob('*.html'):
    txt=p.read_text(encoding='utf-8')
    if 'class="nav-group nav-primary"' in txt and not re.search(r'<div class="nav-group nav-primary">.*?href="/glosar/"[^>]*>Glosár</a>',txt,re.S):
        errors.append(f'Glosar missing from primary nav: {p.relative_to(ROOT)}')
    if 'class="mobile-bottom-nav"' in txt and not re.search(r'<nav[^>]+class="mobile-bottom-nav".*?href="/glosar/"[^>]*>Glosár</a>',txt,re.S):
        errors.append(f'Glosar missing from mobile bottom nav: {p.relative_to(ROOT)}')

# MI 3102 status: owned but not yet evidenced by real measurement content.
for x in ['Metrel MI 3102 BT EurotestXE','status-chip ok">už mám','skontroloval príslušenstvo','overil, že sa zapne','Reálne merania s týmto prístrojom na webe ešte nepublikujem']:
    if x not in mer: errors.append(f'Missing truthful MI 3102 BT status: {x}')
if 'MI 3102 BT EurotestXE</h3><span class="status-chip">objednaný' in mer:
    errors.append('MI 3102 BT must no longer be marked as ordered')
if 'už mám fyzicky k dispozícii' not in rev or 'nie publikované meranie v praxi' not in rev:
    errors.append('Revision page must state MI 3102 ownership without claiming real field measurements')

# Pre-commercial guardrails on the A2 customer-facing surface.
for forbidden in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"']:
    if forbidden in home:
        errors.append(f'Forbidden pre-commercial homepage element: {forbidden}')
if 'komerčné služby zatiaľ neposkytujem' not in home:
    errors.append('Homepage must keep explicit pre-commercial status')

if errors:
    print('PROTOTYPE A2 CHECK FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print('PROTOTYPE A2 CHECK OK · service-first + Glosar bridges + MI 3102 status')
