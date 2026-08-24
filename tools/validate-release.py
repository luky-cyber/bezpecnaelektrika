#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
from html.parser import HTMLParser
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
required=['index.html','CNAME','robots.txt','sitemap.xml','assets/js/main.js','assets/js/consent.js']
errors=[]
for f in required:
    if not (ROOT/f).is_file(): errors.append(f'Missing root file: {f}')
for child in ROOT.iterdir():
    if child.is_dir() and child.name.lower().startswith('bezpecnaelektrika-v'):
        errors.append(f'Nested release directory detected: {child.name}; site files must be in repository root.')

# JSON files and JSON-LD
for p in ROOT.rglob('*.json'):
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'Invalid JSON {p.relative_to(ROOT)}: {e}')
for p in ROOT.rglob('*.html'):
    txt=p.read_text(encoding='utf-8')
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',txt,re.S|re.I):
        try: json.loads(m.group(1))
        except Exception as e: errors.append(f'Invalid JSON-LD {p.relative_to(ROOT)}: {e}')
    # root-relative internal href/src existence (anchors ignored)
    for attr,val in re.findall(r'\b(href|src)=["\']([^"\']+)["\']',txt,re.I):
        if not val.startswith('/') or val.startswith('//'): continue
        path=val.split('#',1)[0].split('?',1)[0]
        if not path: continue
        target=ROOT/path.lstrip('/')
        if path.endswith('/'):
            target=target/'index.html'
        if not target.exists(): errors.append(f'Broken internal {attr} in {p.relative_to(ROOT)}: {val}')

try: ET.parse(ROOT/'sitemap.xml')
except Exception as e: errors.append(f'Invalid sitemap.xml: {e}')
try: ET.parse(ROOT/'podcast/feed.xml')
except Exception as e: errors.append(f'Invalid podcast/feed.xml: {e}')

# Canonical URL conventions and sitemap consistency
canonical_urls=set()
for p in ROOT.rglob('*.html'):
    txt=p.read_text(encoding='utf-8')
    m=re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']|<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',txt,re.I)
    if m:
        u=m.group(1) or m.group(2)
        canonical_urls.add(u)
        parsed=urlparse(u)
        if parsed.netloc!='bezpecnaelektrika.sk': errors.append(f'Non-canonical host in {p.relative_to(ROOT)}: {u}')
        if parsed.path and not parsed.path.endswith('/') and '.' not in parsed.path.rsplit('/',1)[-1]: errors.append(f'Canonical page URL missing trailing slash in {p.relative_to(ROOT)}: {u}')
try:
    tree=ET.parse(ROOT/'sitemap.xml')
    ns={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap_urls={e.text.strip() for e in tree.findall('.//sm:loc',ns) if e.text}
    for u in sitemap_urls:
        parsed=urlparse(u)
        if parsed.netloc!='bezpecnaelektrika.sk': errors.append(f'Non-canonical sitemap host: {u}')
        if parsed.path and not parsed.path.endswith('/') and '.' not in parsed.path.rsplit('/',1)[-1]: errors.append(f'Sitemap page URL missing trailing slash: {u}')
except Exception:
    pass
for required_social in ['https://www.instagram.com/bezpecnaelektrika/','https://www.facebook.com/61591729689209/']:
    if required_social not in (ROOT/'index.html').read_text(encoding='utf-8'):
        errors.append(f'Missing project social identity on homepage: {required_social}')


# v0.5.5 answer-engine checks
for p in ROOT.rglob('poradna/*/index.html'):
    txt=p.read_text(encoding='utf-8')
    if '<h1' not in txt.lower(): errors.append(f'Missing H1 in answer page: {p.relative_to(ROOT)}')
    if 'dateModified' not in txt: errors.append(f'Missing dateModified in answer page: {p.relative_to(ROOT)}')
    if 'Stručne:' not in txt: errors.append(f'Missing Stručne summary in answer page: {p.relative_to(ROOT)}')


# v0.5.6 knowledge-base checks
knowledge_slugs = ['rcd-prudovy-chranic', 'rccb-vs-rcbo', 'impedancia-poruchovej-slucky-zs', 'pe-pen-ochranne-vodice', 'tn-c-tn-s-tn-c-s', 'izolacny-odpor', 'uzemnenie', 'lps-ochrana-pred-bleskom']
for slug in knowledge_slugs:
    p=ROOT/'glosar'/slug/'index.html'
    if not p.is_file(): errors.append(f'Missing knowledge-base page: {slug}')
    else:
        txt=p.read_text(encoding='utf-8')
        for needle in ['Stručne:','Zdroje a proveniencia','dateModified']:
            if needle not in txt: errors.append(f'Missing {needle} in knowledge-base page: {slug}')
        if not any(x in txt for x in ['Čo z výsledku nevyplýva','Čo výsledok neznamená','Čo z toho nevyplýva']): errors.append(f'Missing interpretation-boundary section in knowledge-base page: {slug}')

# v0.5.7 podcast BE-003 checks
try:
    pdata=json.loads((ROOT/'data/podcasts.json').read_text(encoding='utf-8'))
    eps={e.get('id'):e for e in pdata.get('episodes',[])}
    ep=eps.get('BE-003')
    if not ep: errors.append('Missing BE-003 in data/podcasts.json')
    else:
        if ep.get('duration')!='7:06': errors.append('BE-003 duration must be 7:06')
        if ep.get('audio')!='https://audio.bezpecnaelektrika.sk/podcast/2026/be-003-namerana-hodnota-este-nie-je-vysledok.mp3': errors.append('BE-003 audio URL mismatch')
        if not ep.get('featured'): errors.append('BE-003 must be featured')
except Exception as e:
    errors.append(f'BE-003 podcast data check failed: {e}')
feed_txt=(ROOT/'podcast/feed.xml').read_text(encoding='utf-8')
for needle in ['bezpecnaelektrika-be-003','length="5109546"','<itunes:duration>7:06</itunes:duration>']:
    if needle not in feed_txt: errors.append(f'Missing BE-003 RSS field: {needle}')
podcast_html=(ROOT/'podcast/index.html').read_text(encoding='utf-8')
if 'https://bezpecnaelektrika.sk/podcast/#be-003' not in podcast_html:
    errors.append('Missing BE-003 PodcastEpisode JSON-LD')

# Every canonical content URL should be represented in sitemap; 404 is intentionally excluded.
for p in ROOT.rglob('*.html'):
    if p.name=='404.html': continue
    txt=p.read_text(encoding='utf-8')
    m=re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']|<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',txt,re.I)
    if m:
        u=m.group(1) or m.group(2)
        if u not in sitemap_urls: errors.append(f'Canonical URL missing from sitemap: {u}')

if errors:
    print('RELEASE CHECK FAILED')
    for e in sorted(set(errors)): print('-',e)
    sys.exit(1)
print('RELEASE CHECK OK')
print('Root:',ROOT)
print('HTML pages:',sum(1 for _ in ROOT.rglob('*.html')))
