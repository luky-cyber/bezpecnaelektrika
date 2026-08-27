#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]

def txt(rel): return (ROOT/rel).read_text(encoding='utf-8')
home=txt('index.html'); rev=txt('revizie/index.html'); por=txt('poradna/index.html'); mer=txt('meranie/index.html'); mainjs=txt('assets/js/main.js')
hs=BeautifulSoup(home,'html.parser'); rs=BeautifulSoup(rev,'html.parser')

# Compression goals.
hmain=hs.find('main'); rmain=rs.find('main')
def prose_words(node):
    clone=BeautifulSoup(str(node),'html.parser')
    for tag in clone.find_all(['svg','style']): tag.decompose()
    return len(clone.get_text(' ',strip=True).split())
hwords=prose_words(hmain)
rwords=prose_words(rmain)
if len(hmain.find_all('section',recursive=False))!=6: errors.append('Homepage must have exactly 6 top-level sections in A4')
if hwords>700: errors.append(f'Homepage too long for A4 compression target: {hwords} words')
if rwords>850: errors.append(f'/revizie/ too long for A4 customer-first target: {rwords} words')
if len(rmain.find_all('section',recursive=False))>10: errors.append('Revisions page still has too many top-level sections')

for x in ['data-prototype="service-home-a4"','Pripravované revízne služby E2A','Pre rodinné domy, byty a vybrané administratívne priestory.','Mám záujem o pripravované služby','id="kedy-revizia"','id="ako-prebieha"','id="cena"']:
    if x not in home: errors.append(f'Missing A4 homepage invariant: {x}')
if home.count('quick-answer-card') < 3: errors.append('Homepage must expose three practical quick-answer cards')
if home.count('data-term-popover')>2: errors.append('Homepage uses too many technical popovers')
if 'Merať. Dokumentovať. Vysvetľovať.' not in home: errors.append('Short brand signature must remain')

# Customer-first revisions page, with legacy anchors preserved.
for x in ['data-prototype="service-revisions-a4"','Čo budem pri elektrorevíziách riešiť?','Kedy revíziu potrebujete?','Ako revízia prebieha a čo dostanete?','Čo je dobré mať pripravené?','Ako často sa revízia robí?','Čo ovplyvňuje cenu?']:
    if x not in rev: errors.append(f'Missing A4 Revisions invariant: {x}')
for anchor in ['funkcnost-nie-je-dokaz','pripravovane-zameranie','pre-koho','ako-prebieha','co-sa-overuje','priprava-na-navstevu','domacnosti','zamestnavatelia','revizna-sprava','vybavenie','myty','faq']:
    if not rs.find(id=anchor): errors.append(f'Legacy/relevant revisions anchor missing: #{anchor}')
for forbidden in ['MI 3102','MI 3309','Z<sub>s</sub>','id="vybavenie"><div']:
    if forbidden in rev: errors.append(f'Technical equipment/detail leaked back into customer-first /revizie/: {forbidden}')

# Navigation: customer path first, expert content under one explicit entry.
for p in ROOT.rglob('*.html'):
    s=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    nav=s.find('nav',id='main-nav')
    if not nav: continue
    primary=nav.find('div',class_='nav-primary')
    labels=[a.get_text(' ',strip=True) for a in primary.find_all('a',recursive=False)] if primary else []
    if labels!=['Revízie','Kedy revíziu','Cena','Poradňa','O mne']:
        errors.append(f'Primary nav mismatch: {p.relative_to(ROOT)} -> {labels}')
    btn=nav.find('button',class_='more-toggle')
    if not btn or 'Odborný obsah' not in btn.get_text(' ',strip=True): errors.append(f'Odborný obsah toggle missing: {p.relative_to(ROOT)}')
    supp=nav.find('div',class_='nav-supplemental')
    slabels=[a.get_text(' ',strip=True) for a in supp.find_all('a',recursive=False)] if supp else []
    if slabels!=['Glosár','Meranie v praxi','Čo nové v elektro','Podcast','Zdroje a metodika','Mapa obsahu']:
        errors.append(f'Expert nav mismatch: {p.relative_to(ROOT)} -> {slabels}')
    if primary and primary.find('a',href='/glosar/'):
        errors.append(f'Glosár must not be a primary customer-nav item in A4: {p.relative_to(ROOT)}')

# Pre-commercial and schema guardrails.
for forbidden in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"']:
    if forbidden in home or forbidden in rev or forbidden in por:
        errors.append(f'Forbidden pre-commercial element: {forbidden}')
if 'komerčné služby zatiaľ neposkytujem' not in home or 'komerčné služby zatiaľ neposkytujem' not in rev:
    errors.append('Explicit pre-commercial status missing from homepage or /revizie/')

# Poradna A3 customer-first direction remains intact.
for x in ['Čo budete pri elektrorevízii riešiť?','Potrebujem riešiť…','advice-situation-grid']:
    if x not in por: errors.append(f'Poradna customer-first invariant lost: {x}')
details=list((ROOT/'poradna').glob('*/index.html'))
if len(details)!=12: errors.append(f'Expected 12 Poradna details, found {len(details)}')
for p in details:
    t=p.read_text(encoding='utf-8')
    if 'customer-article-contact' not in t or 'mailto:kontakt@bezpecnaelektrika.sk' not in t:
        errors.append(f'Customer contact missing from {p.relative_to(ROOT)}')

# Popovers remain accessible interaction and MI status is truthful.
if 'prototype A3 — inline term explanations' not in mainjs: errors.append('Popover behavior missing from main.js')
for x in ['Metrel MI 3102 BT EurotestXE','už mám','skontroloval príslušenstvo','overil, že sa zapne','Reálne merania s týmto prístrojom na webe ešte nepublikujem']:
    if x not in mer: errors.append(f'MI 3102 BT status invariant missing: {x}')

if errors:
    print('PROTOTYPE A4 CHECK FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print(f'PROTOTYPE A4 CHECK OK · homepage {hwords} words / 6 sections · revisions {rwords} words · customer-first nav + pre-commercial guardrails')
