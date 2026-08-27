#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def t(rel): return (ROOT/rel).read_text(encoding='utf-8')
home=t('index.html'); rev=t('revizie/index.html'); cons=t('assets/js/consent.js'); priv=t('ochrana-sukromia/index.html'); css=t('assets/css/v040.css')
hs=BeautifulSoup(home,'html.parser'); rs=BeautifulSoup(rev,'html.parser')
main=hs.find('main')
if len(main.find_all('section',recursive=False))!=6: errors.append('Homepage must keep six customer-first sections')
if len(main.get_text(' ',strip=True).split())>500: errors.append('Homepage customer copy exceeded 500 words')
if hs.find('h1').get_text(' ',strip=True)!='Revízie elektrických zariadení a inštalácií': errors.append('Service-first H1 changed')
if re.search(r'\b(?:LPS|RCD|Zs|PEN|RCBO|RCCB)\b',main.get_text(' ',strip=True)): errors.append('Technical acronym leaked into homepage customer path')
if len(hs.select('#situacie a.service-intent-card--link[data-service-situation]'))!=4: errors.append('Four tracked situation cards required')
for rel,txt in [('home',home),('revisions',rev)]:
    for needle in ['service-trust-inline','Ing. Lukáš Likavčan, PhD.','O mne a kvalifikácii','komerčné služby zatiaľ neposkytujem']:
        if needle not in txt: errors.append(f'{rel}: missing trust/pre-commercial invariant {needle}')
if 'Čo ak sa pri revízii nájde problém?' not in rev: errors.append('Revisions FAQ must explain what happens when a problem is found')
faq=next((n for script in rs.find_all('script',attrs={'type':'application/ld+json'}) for n in (json.loads(script.string or '{}').get('@graph',[]) if (script.string or '').strip() else []) if isinstance(n,dict) and n.get('@type')=='FAQPage'),None)
if not faq or not any(q.get('name')=='Čo ak sa pri revízii nájde problém?' for q in faq.get('mainEntity',[])): errors.append('FAQPage JSON-LD missing detected-problem question')
for ev in ['service_interest_click','price_interest_click','service_situation_click','expert_content_click']:
    if ev not in cons: errors.append(f'Analytics implementation missing {ev}')
    if ev not in priv: errors.append(f'Privacy disclosure missing {ev}')
for bad in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed']:
    if bad in home+rev: errors.append(f'Forbidden pre-commercial element: {bad}')
if '.service-trust-inline{' not in css: errors.append('Missing rc1 trust styling in source CSS module')
if not (ROOT/'RELEASE-v0.6.0-rc1.md').is_file(): errors.append('Missing rc1 release notes')
if not t('README.md').startswith('# Bezpečná elektrika v0.6.0-rc1'): errors.append('README does not identify rc1')
if errors:
    print('V0.6.0-RC1 CHECK FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print(f'V0.6.0-RC1 CHECK OK · homepage {len(main.get_text(" ",strip=True).split())} words · service-first + trust + analytics + pre-commercial guardrails')
