#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
home=(ROOT/'index.html').read_text(encoding='utf-8')
por=(ROOT/'poradna/index.html').read_text(encoding='utf-8')
rev=(ROOT/'revizie/index.html').read_text(encoding='utf-8')
mainjs=(ROOT/'assets/js/main.js').read_text(encoding='utf-8')

for x in [
    'data-prototype="service-home-a3"',
    'Pripravované služby revízneho technika',
    'Bezpečná elektrika je stránka pripravovaných revíznych služieb.',
    'mailto:kontakt@bezpecnaelektrika.sk',
    'kontakt@bezpecnaelektrika.sk',
    'term-popover__trigger',
    'term-lps-faq', 'term-rcd-faq',
]:
    if x not in home: errors.append(f'Missing A3 homepage invariant: {x}')

for forbidden in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"']:
    if forbidden in home or forbidden in rev or forbidden in por:
        errors.append(f'Forbidden pre-commercial element: {forbidden}')
if 'komerčné služby zatiaľ neposkytujem' not in home:
    errors.append('Homepage must retain explicit pre-commercial status')

for x in ['Čo budete pri elektrorevízii riešiť?','Potrebujem riešiť…','advice-situation-grid','term-lps-poradna','term-rcd-poradna']:
    if x not in por: errors.append(f'Missing A3 Poradna customer-first invariant: {x}')
for old in ['Elektrika bez hmly.','Nájdite svoju tému','Najprv to, čo riešime najčastejšie.']:
    if old in por: errors.append(f'Old content-first Poradna intro still present: {old}')
if por.count('advice-situation-card') < 6:
    errors.append('Poradna must expose at least six customer-situation cards')

for x in ['Táto stránka pripravuje ponuku revíznych služieb v rozsahu E2A.','mailto:kontakt@bezpecnaelektrika.sk','term-lps-revizie','term-rcd-revizie']:
    if x not in rev: errors.append(f'Missing A3 Revisions service invariant: {x}')

# Every Poradna detail should now offer a direct pre-commercial email contact.
details=list((ROOT/'poradna').glob('*/index.html'))
if len(details)!=12: errors.append(f'Expected 12 Poradna details, found {len(details)}')
for p in details:
    txt=p.read_text(encoding='utf-8')
    if 'customer-article-contact' not in txt or 'mailto:kontakt@bezpecnaelektrika.sk' not in txt:
        errors.append(f'Customer contact missing from {p.relative_to(ROOT)}')
    if 'komerčné služby' not in txt.lower():
        errors.append(f'Pre-commercial wording missing from {p.relative_to(ROOT)}')

if 'prototype A3 — inline term explanations' not in mainjs:
    errors.append('A3 popover behavior missing from main.js')

# Glosar remains directly reachable from primary and mobile navigation.
for p in ROOT.rglob('*.html'):
    txt=p.read_text(encoding='utf-8')
    if 'class="nav-group nav-primary"' in txt and not re.search(r'<div class="nav-group nav-primary">.*?href="/glosar/"[^>]*>Glosár</a>',txt,re.S):
        errors.append(f'Glosar missing from primary nav: {p.relative_to(ROOT)}')
    if 'class="mobile-bottom-nav"' in txt and not re.search(r'<nav[^>]+class="mobile-bottom-nav".*?href="/glosar/"[^>]*>Glosár</a>',txt,re.S):
        errors.append(f'Glosar missing from mobile nav: {p.relative_to(ROOT)}')

if errors:
    print('PROTOTYPE A3 CHECK FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print('PROTOTYPE A3 CHECK OK · customer-first paths + inline term explanations + direct pre-commercial contact')
