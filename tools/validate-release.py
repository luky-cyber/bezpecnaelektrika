#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
required=['index.html','CNAME','robots.txt','sitemap.xml','assets/js/main.js','assets/js/consent.js','assets/js/search.js','data/search-index.json','tools/build-search-index.py','tools/build-news-sitemap.py','obsah/index.html','hladat/index.html','RELEASE-v0.5.12.md']
errors=[]
readme=(ROOT/'README.md').read_text(encoding='utf-8') if (ROOT/'README.md').is_file() else ''
if not readme.startswith('# Bezpečná elektrika v0.5.12'):
    errors.append('README must identify v0.5.12')
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
        for needle in ['Stručne:','dateModified']:
            if needle not in txt: errors.append(f'Missing {needle} in knowledge-base page: {slug}')
        if not any(x in txt for x in ['Zdroje a proveniencia','Odborný a normatívny základ']): errors.append(f'Missing source/provenance section in knowledge-base page: {slug}')
        if not any(x in txt for x in ['Čo z výsledku nevyplýva','Čo výsledok neznamená','Čo z toho nevyplýva','Čo z výsledku nemožno automaticky vyvodiť']): errors.append(f'Missing interpretation-boundary section in knowledge-base page: {slug}')

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



# v0.5.8 AI/Search + Identity + UX/Performance checks
robots_txt=(ROOT/'robots.txt').read_text(encoding='utf-8')
for block in [
    'User-agent: OAI-SearchBot\nAllow: /',
    'User-agent: ChatGPT-User\nAllow: /',
    'User-agent: GPTBot\nDisallow: /',
]:
    if block not in robots_txt:
        errors.append(f'Missing crawler policy in robots.txt: {block.replace(chr(10), " / ")}')
if re.search(r'User-agent:\s*GPTBot\s*\n\s*Allow:\s*/', robots_txt, re.I):
    errors.append('GPTBot must not be allowed in v0.5.8')

style_txt=(ROOT/'assets/css/style.css').read_text(encoding='utf-8')
if '@import' in style_txt:
    errors.append('Production assets/css/style.css must not use @import in v0.5.8')

home_txt=(ROOT/'index.html').read_text(encoding='utf-8')
if 'class="contact-author' not in home_txt or 'https://likavcan.cz/lukas/' not in home_txt:
    errors.append('Homepage contact must include visible professional-profile link to likavcan.cz/lukas/')
for redundant in ['Funguje ≠ overené','Od pozorovania k rozhodnutiu']:
    if redundant in home_txt:
        errors.append(f'Homepage duplicate block still present: {redundant}')

# Identity graph consistency where Person/Project entities are present.
expected_person_id='https://likavcan.cz/lukas/#lukas-likavcan'
expected_person_url='https://likavcan.cz/lukas/'
expected_project_id='https://bezpecnaelektrika.sk/#project'
expected_project_socials={
    'https://www.instagram.com/bezpecnaelektrika/',
    'https://www.facebook.com/61591729689209/'
}
for hp in ROOT.rglob('*.html'):
    txt=hp.read_text(encoding='utf-8')
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',txt,re.S|re.I):
        try:
            data=json.loads(m.group(1))
        except Exception:
            continue
        graph=data.get('@graph',[]) if isinstance(data,dict) else []
        for obj in graph:
            if not isinstance(obj,dict): continue
            if obj.get('@type')=='Person' and obj.get('@id')==expected_person_id:
                if obj.get('url')!=expected_person_url:
                    errors.append(f'Person URL mismatch in {hp.relative_to(ROOT)}')
                if not obj.get('knowsAbout'):
                    errors.append(f'Missing knowsAbout in {hp.relative_to(ROOT)}')
            if obj.get('@type')=='Project' and obj.get('@id')==expected_project_id:
                if obj.get('founder',{}).get('@id')!=expected_person_id:
                    errors.append(f'Project founder mismatch in {hp.relative_to(ROOT)}')
                if set(obj.get('sameAs',[]))!=expected_project_socials:
                    errors.append(f'Project sameAs mismatch in {hp.relative_to(ROOT)}')

# Relevant edited pages should expose dateModified on their WebPage entity.
for rel in ['index.html','revizie/index.html','poradna/index.html','meranie/index.html','glosar/index.html','novinky/index.html','metodika/index.html','o-projekte/index.html']:
    txt=(ROOT/rel).read_text(encoding='utf-8')
    if '"@type":"WebPage"' not in txt or '"dateModified":' not in txt:
        errors.append(f'Missing WebPage dateModified in {rel}')

# Contextual CTA coverage requested by external audits.
for rel in ['o-projekte/index.html','meranie/index.html','glosar/index.html','novinky/index.html','metodika/index.html']:
    txt=(ROOT/rel).read_text(encoding='utf-8')
    if 'advice-contact-cta' not in txt or '/revizie/' not in txt:
        errors.append(f'Missing contextual CTA to revision practice in {rel}')

metodika_txt=(ROOT/'metodika/index.html').read_text(encoding='utf-8')
mobile_m=re.search(r'<nav[^>]+class=["\']mobile-bottom-nav["\'][^>]*>(.*?)</nav>',metodika_txt,re.S|re.I)
if mobile_m and re.search(r'class=["\']active["\'][^>]+href=["\']/o-projekte/["\']',mobile_m.group(1),re.I):
    errors.append('Metodika mobile nav must not mark O projekte as active')

poradna_txt=(ROOT/'poradna/index.html').read_text(encoding='utf-8')
for label in ['Uzemnenie','Spotrebiče a predlžovačky']:
    if re.search(r'<a\s+href=["\']#faq["\'][^>]*>.*?<strong>'+re.escape(label)+r'</strong>',poradna_txt,re.S|re.I):
        errors.append(f'Poradna topic still misleadingly points to #faq: {label}')
for required_link in [
    '/poradna/revizia-po-rekonstrukcii/',
    '/poradna/rozdiel-kontrola-elektrikar-a-revizia/',
    '/poradna/co-sa-da-zistit-bez-rozoberania-elektroinstalacie/',
    '/glosar/izolacny-odpor/'
]:
    count=0
    for hp in ROOT.rglob('*.html'):
        if required_link in hp.read_text(encoding='utf-8'):
            count += 1
    if count < 2:
        errors.append(f'Weak internal-link target still has fewer than 2 linking HTML pages: {required_link} ({count})')

if not (ROOT/'RELEASE-v0.5.8.md').is_file():
    errors.append('Missing RELEASE-v0.5.8.md')



# v0.5.9 Authority & Visual Evidence checks
for rel in [
    'glosar/rcd-prudovy-chranic/index.html',
    'glosar/impedancia-poruchovej-slucky-zs/index.html'
]:
    txt=(ROOT/rel).read_text(encoding='utf-8')
    for needle in ['article-byline','Odborný a normatívny základ','Od čoho výsledok závisí','Typické chyby interpretácie']:
        if needle not in txt: errors.append(f'Missing v0.5.9 authority element in {rel}: {needle}')
    if 'https://likavcan.cz/lukas/' not in txt: errors.append(f'Missing visible author profile in {rel}')

for rel in [
    'poradna/revizia-pri-kupe-starsieho-domu-alebo-bytu/index.html',
    'poradna/elektrikar-prerobil-rozvadzac-co-nasleduje/index.html'
]:
    p=ROOT/rel
    if not p.is_file(): errors.append(f'Missing v0.5.9 Poradna page: {rel}')
    else:
        txt=p.read_text(encoding='utf-8')
        for needle in ['Stručne:','article-byline','dateModified']:
            if needle not in txt: errors.append(f'Missing {needle} in v0.5.9 Poradna page: {rel}')

for rel in ['assets/img/diagrams/be-diag-01-proces-revizie.svg','assets/img/diagrams/be-diag-01-proces-revizie-mobile.svg','assets/img/diagrams/be-diag-02-poruchova-slucka-zs.svg']:
    p=ROOT/rel
    if not p.is_file(): errors.append(f'Missing diagram asset: {rel}')
    else:
        txt=p.read_text(encoding='utf-8')
        for needle in ['<title','<desc','viewBox']:
            if needle not in txt: errors.append(f'Missing accessible SVG element {needle} in {rel}')

rev_txt=(ROOT/'revizie/index.html').read_text(encoding='utf-8')
for needle in ['BE-DIAG-01','figcaption','diagram-provenance']:
    if needle not in rev_txt: errors.append(f'Missing process-diagram integration in Revízie: {needle}')
zs_txt=(ROOT/'glosar/impedancia-poruchovej-slucky-zs/index.html').read_text(encoding='utf-8')
if 'BE-DIAG-02' not in zs_txt: errors.append('Missing BE-DIAG-02 on Zs page')

for rel in ['assets/img/og/og-home-v1.jpg','assets/img/og/og-revizie-v1.jpg','assets/img/og/og-poradna-v1.jpg']:
    if not (ROOT/rel).is_file(): errors.append(f'Missing v0.5.9 OG image: {rel}')
for rel,img in [('index.html','og-home-v1.jpg'),('revizie/index.html','og-revizie-v1.jpg'),('poradna/index.html','og-poradna-v1.jpg')]:
    if img not in (ROOT/rel).read_text(encoding='utf-8'): errors.append(f'Missing custom OG assignment in {rel}: {img}')

if not (ROOT/'docs/ANALYTICS-BASELINE-v0.5.8.md').is_file(): errors.append('Missing v0.5.8 baseline checklist')
if not (ROOT/'RELEASE-v0.5.9.md').is_file(): errors.append('Missing RELEASE-v0.5.9.md')

# New/changed content URLs must use current lastmod without touching unrelated sitemap entries.
try:
    tree2=ET.parse(ROOT/'sitemap.xml'); ns2={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    lm={u.find('sm:loc',ns2).text:u.find('sm:lastmod',ns2).text if u.find('sm:lastmod',ns2) is not None else None for u in tree2.findall('.//sm:url',ns2)}
    for url in [
      'https://bezpecnaelektrika.sk/glosar/rcd-prudovy-chranic/',
      'https://bezpecnaelektrika.sk/glosar/impedancia-poruchovej-slucky-zs/',
      'https://bezpecnaelektrika.sk/poradna/revizia-pri-kupe-starsieho-domu-alebo-bytu/',
      'https://bezpecnaelektrika.sk/poradna/elektrikar-prerobil-rozvadzac-co-nasleduje/'
    ]:
      if lm.get(url)!='2026-08-25': errors.append(f'Wrong sitemap lastmod for v0.5.9 URL: {url}')
except Exception as e:
    errors.append(f'v0.5.9 sitemap lastmod check failed: {e}')

# Every indexable canonical content URL should be represented in sitemap; noindex utilities and 404 are intentionally excluded.
for p in ROOT.rglob('*.html'):
    if p.name=='404.html': continue
    txt=p.read_text(encoding='utf-8')
    if re.search(r'<meta[^>]+(?:name=["\']robots["\'][^>]+content=["\'][^"\']*noindex|content=["\'][^"\']*noindex[^"\']*["\'][^>]+name=["\']robots["\'])',txt,re.I):
        continue
    m=re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']|<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',txt,re.I)
    if m:
        u=m.group(1) or m.group(2)
        if u not in sitemap_urls: errors.append(f'Canonical URL missing from sitemap: {u}')


# v0.5.10 Authority & Visual Evidence II checks
lps_txt=(ROOT/'glosar/lps-ochrana-pred-bleskom/index.html').read_text(encoding='utf-8')
for needle in ['Od čoho posúdenie závisí','Trieda LPS: prečo ju nemožno určiť podľa typu domu','Odborný a normatívny základ','IEC 62305-2:2024','IEC 62305-3:2024','IEC 62305-4:2024']:
    if needle not in lps_txt: errors.append(f'Missing v0.5.10 LPS authority element: {needle}')
if 'Rodinný dom teda automaticky neznamená LPS III ani inú konkrétnu triedu.' not in lps_txt:
    errors.append('LPS page must preserve explicit boundary against building-type class shortcuts')

for rel in ['assets/img/diagrams/be-diag-03-zs-vs-zline.svg','assets/img/diagrams/be-diag-04-rccb-vs-rcbo.svg','assets/img/diagrams/be-diag-05-tn-c-tn-c-s.svg']:
    p=ROOT/rel
    if not p.is_file(): errors.append(f'Missing v0.5.10 diagram: {rel}')
    else:
        txt=p.read_text(encoding='utf-8')
        for needle in ['<title>','<desc>','viewBox']:
            if needle not in txt: errors.append(f'Missing accessible SVG element {needle} in {rel}')

for rel,needle in [
 ('glosar/impedancia-poruchovej-slucky-zs/index.html','BE-DIAG-03'),
 ('glosar/rccb-vs-rcbo/index.html','BE-DIAG-04'),
 ('glosar/tn-c-tn-s-tn-c-s/index.html','BE-DIAG-05')]:
    if needle not in (ROOT/rel).read_text(encoding='utf-8'): errors.append(f'Missing diagram integration {needle} in {rel}')

new_advice=ROOT/'poradna/prudovy-chranic-opakovane-vypina/index.html'
if not new_advice.is_file(): errors.append('Missing v0.5.10 Poradna page: prudovy-chranic-opakovane-vypina')
else:
    txt=new_advice.read_text(encoding='utf-8')
    for needle in ['Stručne:','Prečo nestačí stlačiť TEST','Čo z vypínania nevyplýva','Odborný a normatívny základ']:
        if needle not in txt: errors.append(f'Missing v0.5.10 RCD advice element: {needle}')
    if '/glosar/rcd-prudovy-chranic/' not in txt: errors.append('RCD advice must link to RCD knowledge page')

for rel in ['glosar/rccb-vs-rcbo/index.html','glosar/tn-c-tn-s-tn-c-s/index.html','glosar/uzemnenie/index.html','glosar/izolacny-odpor/index.html']:
    txt=(ROOT/rel).read_text(encoding='utf-8')
    if 'Odborný a normatívny základ' not in txt: errors.append(f'Missing expanded provenance in {rel}')

for rel in ['assets/img/og/og-glosar-v1.jpg','assets/img/og/og-meranie-v1.jpg','assets/img/og/og-podcast-v1.jpg','assets/img/og/og-rcd-v1.jpg','assets/img/og/og-zs-v1.jpg','assets/img/og/og-lps-v1.jpg']:
    if not (ROOT/rel).is_file(): errors.append(f'Missing v0.5.10 OG image: {rel}')
for rel,img in [
 ('glosar/index.html','og-glosar-v1.jpg'),('meranie/index.html','og-meranie-v1.jpg'),('podcast/index.html','og-podcast-v1.jpg'),
 ('glosar/rcd-prudovy-chranic/index.html','og-rcd-v1.jpg'),('glosar/impedancia-poruchovej-slucky-zs/index.html','og-zs-v1.jpg'),('glosar/lps-ochrana-pred-bleskom/index.html','og-lps-v1.jpg')]:
    if img not in (ROOT/rel).read_text(encoding='utf-8'): errors.append(f'Missing v0.5.10 custom OG assignment in {rel}: {img}')

if not (ROOT/'RELEASE-v0.5.10.md').is_file(): errors.append('Missing RELEASE-v0.5.10.md')
try:
    tree3=ET.parse(ROOT/'sitemap.xml'); ns3={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    lm3={u.find('sm:loc',ns3).text:u.find('sm:lastmod',ns3).text if u.find('sm:lastmod',ns3) is not None else None for u in tree3.findall('.//sm:url',ns3)}
    for url in [
      'https://bezpecnaelektrika.sk/glosar/lps-ochrana-pred-bleskom/',
      'https://bezpecnaelektrika.sk/glosar/rccb-vs-rcbo/',
      'https://bezpecnaelektrika.sk/glosar/tn-c-tn-s-tn-c-s/',
      'https://bezpecnaelektrika.sk/poradna/prudovy-chranic-opakovane-vypina/'
    ]:
      if lm3.get(url)!='2026-08-25': errors.append(f'Wrong sitemap lastmod for v0.5.10 URL: {url}')
except Exception as e:
    errors.append(f'v0.5.10 sitemap lastmod check failed: {e}')


# v0.5.10 final pre-deploy polish checks
style_final=(ROOT/'assets/css/style.css').read_text(encoding='utf-8')
if '.instrument-placeholder--planned{border-style:dashed}' in style_final:
    errors.append('MI 3102 BT planned placeholder must not use the unintended dashed frame')
if '.instrument-placeholder--planned{border:0;border-bottom:1px solid var(--border)}' not in style_final:
    errors.append('Missing final MI 3102 BT planned-placeholder border cleanup')

header_logo=ROOT/'assets/img/bezpecna-elektrika-logo-header.webp'
if not header_logo.is_file():
    errors.append('Missing optimized header logo asset')
elif header_logo.stat().st_size > 50_000:
    errors.append(f'Optimized header logo is unexpectedly large: {header_logo.stat().st_size} bytes')
for hp in ROOT.rglob('*.html'):
    txt=hp.read_text(encoding='utf-8')
    if 'class="brand-logo"' in txt and '/assets/img/bezpecna-elektrika-logo-header.webp' not in txt:
        errors.append(f'Header still uses unoptimized logo in {hp.relative_to(ROOT)}')

poradna_og='https://bezpecnaelektrika.sk/assets/img/og/og-poradna-v1.jpg'
for hp in ROOT.glob('poradna/*/index.html'):
    txt=hp.read_text(encoding='utf-8')
    if f'content="{poradna_og}" property="og:image"' not in txt:
        errors.append(f'Poradna detail missing shared Poradna OG image: {hp.relative_to(ROOT)}')
    if f'content="{poradna_og}" name="twitter:image"' not in txt:
        errors.append(f'Poradna detail missing shared Poradna Twitter image: {hp.relative_to(ROOT)}')

for rel,img in [
    ('glosar/rcd-prudovy-chranic/index.html','https://bezpecnaelektrika.sk/assets/img/og/og-rcd-v1.jpg'),
    ('glosar/impedancia-poruchovej-slucky-zs/index.html','https://bezpecnaelektrika.sk/assets/img/og/og-zs-v1.jpg'),
    ('glosar/lps-ochrana-pred-bleskom/index.html','https://bezpecnaelektrika.sk/assets/img/og/og-lps-v1.jpg'),
]:
    txt=(ROOT/rel).read_text(encoding='utf-8')
    if 'property="og:image:alt"' not in txt:
        errors.append(f'Missing og:image:alt in {rel}')
    if f'content="{img}" name="twitter:image"' not in txt:
        errors.append(f'Missing matching twitter:image in {rel}')

# Visible article update date should match structured dateModified where a byline is shown.
for hp in ROOT.rglob('*.html'):
    txt=hp.read_text(encoding='utf-8')
    vm=re.search(r'Atualizované:\s*<strong>(\d{2})\.\s*(\d{2})\.\s*(\d{4})</strong>',txt,re.I)
    if not vm:
        vm=re.search(r'Aktualizované:\s*<strong>(\d{2})\.\s*(\d{2})\.\s*(\d{4})</strong>',txt,re.I)
    dm=re.search(r'"dateModified":"(\d{4})-(\d{2})-(\d{2})"',txt)
    if vm and dm:
        visible=f'{vm.group(3)}-{vm.group(2)}-{vm.group(1)}'
        structured=f'{dm.group(1)}-{dm.group(2)}-{dm.group(3)}'
        if visible != structured:
            errors.append(f'Visible update date does not match dateModified in {hp.relative_to(ROOT)}: {visible} != {structured}')

# Every published custom OG raster should have an editable SVG source with the same stem.
for jpg in (ROOT/'assets/img/og').glob('og-*-v1.jpg'):
    src=ROOT/'assets/img/og-src'/(jpg.stem+'.svg')
    if not src.is_file():
        errors.append(f'Missing editable OG source for {jpg.name}')

if '/poradna/elektrikar-prerobil-rozvadzac-co-nasleduje/' not in (ROOT/'revizie/index.html').read_text(encoding='utf-8'):
    errors.append('Revízie must link to the Poradna page about a rebuilt distribution board')


# v0.5.11 Search & content orientation checks
import subprocess, unicodedata

for rel in ['RELEASE-v0.5.11.md','obsah/index.html','hladat/index.html','data/search-index.json','tools/build-search-index.py','tools/test-search-index.py','assets/js/search.js']:
    if not (ROOT/rel).is_file(): errors.append(f'Missing v0.5.11 file: {rel}')

search_page=(ROOT/'hladat/index.html').read_text(encoding='utf-8')
if 'content="noindex,follow" name="robots"' not in search_page and 'name="robots" content="noindex,follow"' not in search_page:
    errors.append('/hladat/ must use noindex,follow')
if 'https://bezpecnaelektrika.sk/hladat/' not in search_page:
    errors.append('/hladat/ must use its stable canonical URL')
if 'https://bezpecnaelektrika.sk/hladat/' in sitemap_urls:
    errors.append('/hladat/ must not be listed in sitemap')
if 'https://bezpecnaelektrika.sk/obsah/' not in sitemap_urls:
    errors.append('/obsah/ must be listed in sitemap')

# Search trigger + script should be available on every standard page with a site header.
for hp in ROOT.rglob('*.html'):
    txt=hp.read_text(encoding='utf-8')
    if 'class="site-header"' in txt:
        if 'data-search-open' not in txt: errors.append(f'Missing search trigger in {hp.relative_to(ROOT)}')
        if '/assets/js/search.js' not in txt: errors.append(f'Missing search.js in {hp.relative_to(ROOT)}')
    if 'class="site-footer"' in txt and '/obsah/' not in txt:
        errors.append(f'Missing Mapa obsahu footer link in {hp.relative_to(ROOT)}')
if 'data-prefill404="true"' not in (ROOT/'404.html').read_text(encoding='utf-8') or '/assets/js/search.js' not in (ROOT/'404.html').read_text(encoding='utf-8'):
    errors.append('404 must include the shared site search with URL prefill')

# Public anchor IDs must be unique. TOC links must resolve locally.
for hp in ROOT.rglob('*.html'):
    txt=hp.read_text(encoding='utf-8')
    ids=re.findall(r'\bid=["\']([^"\']+)["\']',txt,re.I)
    dupes={x for x in ids if ids.count(x)>1}
    if dupes: errors.append(f'Duplicate HTML IDs in {hp.relative_to(ROOT)}: {sorted(dupes)}')
    for href in re.findall(r'<a[^>]+href=["\']#([^"\']+)["\'][^>]*>',txt,re.I):
        # Ignore home-page contact links in fragments that are not TOC/anchor navigation.
        if f'id="{href}"' not in txt and f"id='{href}'" not in txt:
            errors.append(f'Local anchor #{href} has no target in {hp.relative_to(ROOT)}')

required_anchor_sets={
 'glosar/rcd-prudovy-chranic/index.html':['co-to-je','co-sa-overuje','tlacidlo-test','co-z-vysledku-nevyplyva','suvislost-s-reviziou','odborny-zaklad'],
 'glosar/impedancia-poruchovej-slucky-zs/index.html':['co-to-je','co-sa-overuje','zs-nie-je-zline','co-z-vysledku-nevyplyva','suvislost-s-reviziou','odborny-zaklad'],
 'glosar/lps-ochrana-pred-bleskom/index.html':['co-to-je','co-sa-overuje','co-z-vysledku-nevyplyva','suvislost-s-reviziou','odborny-zaklad','trieda-lps'],
 'revizie/index.html':['funkcnost-nie-je-dokaz','ako-prebieha','co-sa-overuje','revizna-sprava','myty','faq'],
 'meranie/index.html':['od-pohladu-k-zaveru','co-zistujeme','veliciny','pristroje','zdroje'],
 'metodika/index.html':['odborne-zdroje','normy-a-legislativa','ako-overujem','ako-vznikaju-novinky','ai-ako-pomocnik','co-na-webe-nenajdete'],
}
for rel,anchors in required_anchor_sets.items():
    txt=(ROOT/rel).read_text(encoding='utf-8')
    for aid in anchors:
        if f'id="{aid}"' not in txt and f"id='{aid}'" not in txt:
            errors.append(f'Missing stable anchor #{aid} in {rel}')
    if rel in ['glosar/rcd-prudovy-chranic/index.html','glosar/impedancia-poruchovej-slucky-zs/index.html','glosar/lps-ochrana-pred-bleskom/index.html','revizie/index.html','meranie/index.html','metodika/index.html']:
        if 'page-toc--desktop' not in txt or 'page-toc--mobile' not in txt:
            errors.append(f'Missing desktop/mobile TOC in {rel}')

# Curated continuation blocks must stay small, explicit and non-self-referential.
for hp in ROOT.rglob('*.html'):
    txt=hp.read_text(encoding='utf-8')
    for block in re.findall(r'<(?:aside|section)[^>]+class=["\'][^"\']*related-content[^"\']*["\'][^>]*>(.*?)</(?:aside|section)>',txt,re.S|re.I):
        if 'Pokračovať v téme' not in block:
            errors.append(f'Related block is not labelled Pokračovať v téme in {hp.relative_to(ROOT)}')
        links=re.findall(r'<a[^>]+href=["\']([^"\']+)["\']',block,re.I)
        if not (3 <= len(links) <= 5): errors.append(f'Related block must contain 3–5 curated links in {hp.relative_to(ROOT)} ({len(links)})')
        rel_path='/' + hp.relative_to(ROOT).as_posix().removesuffix('index.html')
        if rel_path!='/' and any(x.split('#',1)[0]==rel_path for x in links): errors.append(f'Related block contains self-link in {hp.relative_to(ROOT)}')

# Search index contract.
try:
    sp=json.loads((ROOT/'data/search-index.json').read_text(encoding='utf-8'))
    if sp.get('version') != 1: errors.append('Search index version must be 1')
    records=sp.get('records',[])
    ids=[r.get('id') for r in records]; urls=[r.get('url') for r in records]
    if len(ids)!=len(set(ids)): errors.append('Search index contains duplicate record IDs')
    for r in records:
        for field in ['id','url','title','type','summary','aliases','relatedTerms','headings','text']:
            if field not in r: errors.append(f'Search record {r.get("id")} missing {field}')
        base=(r.get('url') or '/').split('#',1)[0] or '/'
        absolute='https://bezpecnaelektrika.sk' + base
        if base=='/': absolute='https://bezpecnaelektrika.sk/'
        if absolute not in sitemap_urls: errors.append(f'Search record base URL not in sitemap: {r.get("url")}')
        # aliases and relatedTerms are deliberately normalized and curated.
        for term in list(r.get('aliases',[]))+list(r.get('relatedTerms',[])):
            normalized=''.join(c for c in unicodedata.normalize('NFD',term.lower()) if unicodedata.category(c)!='Mn')
            if term != normalized: errors.append(f'Unnormalized search term in {r.get("id")}: {term}')
        # Every heading target in index must exist on the target HTML page.
        if '#' not in r.get('url',''):
            target=ROOT/base.lstrip('/')
            if base.endswith('/'): target=target/'index.html'
            if target.is_file():
                htxt=target.read_text(encoding='utf-8')
                for heading in r.get('headings',[]):
                    aid=heading.get('id')
                    if aid and f'id="{aid}"' not in htxt and f"id='{aid}'" not in htxt:
                        errors.append(f'Search heading target missing: {r.get("id")}#{aid}')
    cena=[r.get('url') for r in records if 'cena' in r.get('aliases',[])]
    if cena != ['/revizie/']: errors.append(f'Alias cena must map only to /revizie/: {cena}')
except Exception as e:
    errors.append(f'Search index contract failed: {e}')

# Mapa obsahu must represent all searchable content except homepage/contact utility records.
map_txt=(ROOT/'obsah/index.html').read_text(encoding='utf-8')
try:
    for r in sp.get('records',[]):
        if r.get('url') in ['/', '/#kontakt']: continue
        if r.get('url') not in map_txt: errors.append(f'Mapa obsahu missing searchable URL: {r.get("url")}')
except Exception:
    pass

search_js=(ROOT/'assets/js/search.js').read_text(encoding='utf-8')
for event in ['search_used','search_no_results','search_result_click']:
    if event not in search_js: errors.append(f'Missing privacy-safe search analytics event: {event}')
if re.search(r'beTrack\?\.\([^\n]+query\s*:',search_js,re.I):
    errors.append('Search analytics must not send raw query text')
privacy=(ROOT/'ochrana-sukromia/index.html').read_text(encoding='utf-8')
if 'Text zadaného vyhľadávacieho dopytu do Google Analytics neposielame.' not in privacy:
    errors.append('Privacy page must explain that raw search queries are not sent to GA4')
if '.normalize("NFD")' not in (ROOT/'assets/js/glossary.js').read_text(encoding='utf-8'):
    errors.append('Glossary search must normalize Slovak diacritics')

# v0.5.12 Novinky: author, time and trust checks.
NEWS_AUTHOR_ID='https://likavcan.cz/lukas/#lukas-likavcan'
NEWS_AUTHOR_URL='https://likavcan.cz/lukas/'
NEWS_AUTHOR_NAME='Lukáš Likavčan'
NEWS_GENERIC_IMAGE='https://bezpecnaelektrika.sk/assets/img/og-bezpecna-elektrika.jpg'
news_paths=sorted((ROOT/'novinky').glob('[0-9][0-9][0-9][0-9]/*/index.html'))
hub_news=(ROOT/'novinky/index.html').read_text(encoding='utf-8')

def strip_tags(s):
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s)).strip()

def parse_iso(v):
    try: return datetime.fromisoformat(v.replace('Z','+00:00'))
    except Exception: return None

def find_jsonld_graphs(txt):
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',txt,re.S|re.I):
        try: data=json.loads(m.group(1))
        except Exception: continue
        if isinstance(data,dict) and isinstance(data.get('@graph'),list): yield data['@graph']

def jpeg_dimensions(path):
    data=path.read_bytes()
    if not data.startswith(b'\xff\xd8'): return None
    i=2
    while i+9 < len(data):
        if data[i] != 0xff: i += 1; continue
        marker=data[i+1]; i += 2
        if marker in (0xd8,0xd9): continue
        if i+2 > len(data): break
        length=int.from_bytes(data[i:i+2],'big')
        if marker in range(0xc0,0xc4) or marker in range(0xc5,0xc8) or marker in range(0xc9,0xcc) or marker in range(0xcd,0xd0):
            if i+7 <= len(data): return (int.from_bytes(data[i+5:i+7],'big'),int.from_bytes(data[i+3:i+5],'big'))
        i += max(length,2)
    return None

# Stable Person identity is one entity across the site.
for hp in ROOT.rglob('*.html'):
    txt=hp.read_text(encoding='utf-8')
    for graph in find_jsonld_graphs(txt):
        for node in graph:
            if isinstance(node,dict) and node.get('@id')==NEWS_AUTHOR_ID:
                if node.get('name')!=NEWS_AUTHOR_NAME or node.get('honorificPrefix')!='Ing.' or node.get('honorificSuffix')!='PhD.':
                    errors.append(f'Inconsistent stable Person identity in {hp.relative_to(ROOT)}')

for hp in news_paths:
    rel=hp.relative_to(ROOT).as_posix(); txt=hp.read_text(encoding='utf-8')
    h1m=re.search(r'<h1[^>]*>(.*?)</h1>',txt,re.S|re.I); h1=strip_tags(h1m.group(1)) if h1m else ''
    titlem=re.search(r'<title>(.*?)</title>',txt,re.S|re.I); title=strip_tags(titlem.group(1)) if titlem else ''
    def meta_value(key,attr='property'):
        m=re.search(r'<meta[^>]+%s=["\']%s["\'][^>]+content=["\']([^"\']+)["\']|<meta[^>]+content=["\']([^"\']+)["\'][^>]+%s=["\']%s["\']' % (attr,re.escape(key),attr,re.escape(key)),txt,re.I)
        return (m.group(1) or m.group(2)) if m else ''
    og_title=meta_value('og:title'); twitter_title=meta_value('twitter:title','name'); og_image=meta_value('og:image')
    if meta_value('og:site_name')!='Bezpečná elektrika': errors.append(f'News og:site_name mismatch in {rel}')
    article=None; person=None; webpage_name=''
    for graph in find_jsonld_graphs(txt):
        for node in graph:
            if isinstance(node,dict) and node.get('@type') in ('Article','NewsArticle') and str(node.get('@id','')).endswith('/#article'): article=node
            if isinstance(node,dict) and node.get('@id')==NEWS_AUTHOR_ID: person=node
            if isinstance(node,dict) and node.get('@type')=='WebPage': webpage_name=str(node.get('name','')).strip()
    if not article:
        errors.append(f'Missing Article/NewsArticle structured data in {rel}'); continue
    headline=str(article.get('headline','')).strip()
    if headline!=h1: errors.append(f'News headline must match H1 in {rel}')
    if og_title!=headline: errors.append(f'News og:title must match editorial headline in {rel}')
    if twitter_title!=headline: errors.append(f'News Twitter title must match editorial headline in {rel}')
    if title!=f'{headline} | Bezpečná elektrika': errors.append(f'News <title> must be editorial headline plus site suffix in {rel}')
    if webpage_name!=title: errors.append(f'News WebPage.name must match <title> in {rel}')
    words=headline.split()
    if len(headline)<10 or len(headline)>110: errors.append(f'News editorial headline should be 10–110 characters in {rel}')
    if len(words)<2 or len(words)>22: errors.append(f'News editorial headline should be 2–22 words in {rel}')
    if re.match(r'^\d',headline): errors.append(f'News editorial headline must not start with a number in {rel}')
    if article.get('image')!=og_image: errors.append(f'News structured image must match og:image in {rel}')
    if 'max-image-preview:large' not in txt: errors.append(f'News page must allow max-image-preview:large in {rel}')
    if meta_value('og:image:width')!='1200' or meta_value('og:image:height')!='675': errors.append(f'News og:image dimensions must declare 1200x675 in {rel}')
    if og_image==NEWS_GENERIC_IMAGE or 'og-news-' not in og_image: errors.append(f'News article must use a relevant image in {rel}')
    img_rel=og_image.replace('https://bezpecnaelektrika.sk/','') if og_image.startswith('https://bezpecnaelektrika.sk/') else ''
    if not img_rel or not (ROOT/img_rel).is_file(): errors.append(f'News article image missing: {og_image}')
    elif jpeg_dimensions(ROOT/img_rel)!=(1200,675): errors.append(f'News article image must be true 1200x675 in {rel}')
    expected_src=urlparse(og_image).path if og_image else ''
    fm=re.search(r'<figure[^>]+class=["\'][^"\']*news-lead-image[^"\']*["\'][^>]*>(.*?)</figure>',txt,re.S|re.I)
    if not fm: errors.append(f'Missing visible lead image in {rel}')
    else:
        im=re.search(r'<img\b([^>]*)>',fm.group(1),re.I|re.S)
        if not im: errors.append(f'Missing img in news lead figure in {rel}')
        else:
            attrs=im.group(1)
            def ia(name):
                m=re.search(r'\b'+re.escape(name)+r'=["\']([^"\']*)["\']',attrs,re.I); return m.group(1) if m else ''
            if ia('src')!=expected_src: errors.append(f'Visible lead image must match og:image in {rel}')
            if not ia('alt').strip(): errors.append(f'Visible lead image requires alt in {rel}')
            if ia('width')!='1200' or ia('height')!='675': errors.append(f'Visible lead image dimensions must be 1200x675 in {rel}')
            if '<figcaption>' not in fm.group(0): errors.append(f'Visible lead image requires caption in {rel}')
    h1_pos=txt.find('</h1>'); byline_pos=txt.find('class="article-byline news-byline"'); figure_pos=txt.find('class="news-lead-image"'); lead_pos=txt.find('class="hero-lead"')
    if min(h1_pos,byline_pos,figure_pos,lead_pos)<0 or not (h1_pos<byline_pos<figure_pos<lead_pos): errors.append(f'News header order must be H1 → byline → lead image → lead text in {rel}')
    if not person: errors.append(f'Missing stable Person in {rel}')
    else:
        if person.get('name')!=NEWS_AUTHOR_NAME: errors.append(f'News Person.name must omit honorifics in {rel}')
        if person.get('url')!=NEWS_AUTHOR_URL: errors.append(f'News Person.url mismatch in {rel}')
    if article.get('author')!={'@id':NEWS_AUTHOR_ID}: errors.append(f'News article author must reference stable Person @id in {rel}')
    if f'href="{NEWS_AUTHOR_URL}"' not in txt or 'rel="author"' not in txt: errors.append(f'Missing visible author link in {rel}')
    pub=str(article.get('datePublished','')); mod=str(article.get('dateModified',''))
    def time_attr(flag):
        m=re.search(r'<time[^>]*'+flag+r'[^>]*datetime=["\']([^"\']+)["\']|<time[^>]*datetime=["\']([^"\']+)["\'][^>]*'+flag,txt,re.I)
        return (m.group(1) or m.group(2)) if m else ''
    pubv=time_attr('data-news-published'); modv=time_attr('data-news-modified'); verified=time_attr('data-news-verified')
    if pubv!=pub: errors.append(f'Visible publication date must match datePublished in {rel}')
    if mod!=pub and modv!=mod: errors.append(f'Visible modified date must match dateModified in {rel}')
    if mod==pub and modv: errors.append(f'Do not show redundant updated date in {rel}')
    if not verified: errors.append(f'Missing visible verified date in {rel}')
    header_m=re.search(r'<article[^>]+class=["\'][^"\']*news-article[^"\']*["\'][^>]*>.*?<header[^>]+class=["\'][^"\']*section[^"\']*["\'][^>]*>(.*?)</header>',txt,re.S|re.I)
    if header_m and 'data-news-verified' in header_m.group(1): errors.append(f'Verified date must not be in publication header in {rel}')
    if not re.search(r'<aside[^>]+class=["\'][^"\']*news-provenance[^"\']*["\'][^>]*>.*?data-news-verified.*?</aside>',txt,re.S|re.I): errors.append(f'Verified date must be in provenance block in {rel}')
    pdt=parse_iso(pub); mdt=parse_iso(mod); vdt=parse_iso(verified)
    if not pdt or not mdt or not vdt: errors.append(f'Invalid news date metadata in {rel}')
    else:
        if mdt<pdt: errors.append(f'dateModified precedes datePublished in {rel}')
        if mdt.date()>vdt.date(): errors.append(f'dateModified later than factual verification date in {rel}')
        if vdt.date()<pdt.date(): errors.append(f'Verified date precedes publication in {rel}')
    if article.get('@type')=='NewsArticle' and ('T' not in pub or not pdt or pdt.tzinfo is None): errors.append(f'NewsArticle requires timezone-aware datePublished in {rel}')
    canonical_m=re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']|<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',txt,re.I)
    canonical=(canonical_m.group(1) or canonical_m.group(2)) if canonical_m else ''; path=urlparse(canonical).path if canonical else ''
    card_m=re.search(r'<article[^>]+class=["\'][^"\']*news-card[^"\']*["\'][^>]*>(.*?<a[^>]+href=["\']'+re.escape(path)+r'["\'][^>]*>.*?</a>.*?)</article>',hub_news,re.S|re.I)
    if not card_m: errors.append(f'News hub missing card for {rel}')
    else:
        card=card_m.group(1); link_m=re.search(r'<h2[^>]*>\s*<a[^>]+href=["\']'+re.escape(path)+r'["\'][^>]*>(.*?)</a>',card,re.S|re.I)
        if not link_m or strip_tags(link_m.group(1))!=headline: errors.append(f'News hub headline mismatch for {rel}')
        if not re.search(r'Publikované\s*<time[^>]+datetime=["\']'+re.escape(pub)+r'["\']',card,re.I): errors.append(f'News hub publication date mismatch for {rel}')

if 'assets/img/og/og-novinky-v1.jpg' not in hub_news: errors.append('Novinky hub must use its own OG image')
if 'max-image-preview:large' not in hub_news: errors.append('Novinky hub must allow max-image-preview:large')
if 'content="1200" property="og:image:width"' not in hub_news or 'content="675" property="og:image:height"' not in hub_news: errors.append('Novinky hub must declare 1200x675 OG dimensions')
for relimg in ['og-novinky-v1.jpg','og-news-62305-3-v1.jpg','og-news-62305-4-v1.jpg','og-news-rccb-rcbo-v1.jpg']:
    ip=ROOT/'assets/img/og'/relimg
    if not ip.is_file(): errors.append(f'Missing v0.5.12 news image: {relimg}')
    elif jpeg_dimensions(ip)!=(1200,675): errors.append(f'Invalid v0.5.12 news image dimensions: {relimg}')
for url,date in [('/novinky/2026/stn-en-iec-62305-3-2026/','2026-02-01'),('/novinky/2026/stn-en-iec-62305-4-2026/','2026-07-01')]:
    if not re.search(r'href=["\']'+re.escape(url)+r'["\']',hub_news,re.I) or f'datetime="{date}"' not in hub_news: errors.append(f'Novinky hub missing event date {date} for {url}')

metodika_txt=(ROOT/'metodika/index.html').read_text(encoding='utf-8')
for needle in ['Ako vznikajú Novinky','Dátum udalosti alebo vydania normy nie je dátumom publikovania článku','NewsArticle sa použije iba pri skutočne čerstvej, časovo citlivej udalosti','kontakt@bezpecnaelektrika.sk']:
    if needle not in metodika_txt: errors.append(f'Missing v0.5.12 methodology rule: {needle}')
workflow=(ROOT/'docs/CONTENT-WORKFLOW.md').read_text(encoding='utf-8')
for needle in ['Google News je možný distribučný kanál, nie publikačný cieľ','Europe/Bratislava','XML sitemap `<lastmod>` je samostatný crawl signál','dateModified','NewsArticle']:
    if needle not in workflow: errors.append(f'Missing v0.5.12 workflow rule: {needle}')

# Site/publication identity signals used by Google must not disappear.
home_txt=(ROOT/'index.html').read_text(encoding='utf-8')
if 'content="Bezpečná elektrika" property="og:site_name"' not in home_txt: errors.append('Homepage must preserve og:site_name')
if '"@type":"WebSite"' not in home_txt or '"name":"Bezpečná elektrika"' not in home_txt: errors.append('Homepage must preserve WebSite.name')
if 'href="/assets/img/favicon-48.png" rel="icon"' not in home_txt or not (ROOT/'assets/img/favicon-48.png').is_file(): errors.append('Homepage must preserve production favicon')

# News sitemap is time-sensitive and exists only while a true NewsArticle is eligible.
news_sitemap=ROOT/'news-sitemap.xml'; now=datetime.now(timezone.utc); eligible_now=[]
for hp in news_paths:
    txt=hp.read_text(encoding='utf-8')
    for graph in find_jsonld_graphs(txt):
        for node in graph:
            if isinstance(node,dict) and node.get('@type')=='NewsArticle':
                dt=parse_iso(str(node.get('datePublished','')))
                if dt and dt.tzinfo is not None and timedelta(0)<=now-dt.astimezone(timezone.utc)<=timedelta(days=2): eligible_now.append(node)
if eligible_now and not news_sitemap.is_file(): errors.append('Eligible NewsArticle exists but news-sitemap.xml has not been built')
robots=(ROOT/'robots.txt').read_text(encoding='utf-8')
if news_sitemap.is_file():
    try:
        nt=ET.parse(news_sitemap); nns={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9','news':'http://www.google.com/schemas/sitemap-news/0.9'}; entries=nt.getroot().findall('sm:url',nns)
        if not entries: errors.append('news-sitemap.xml must not be kept empty')
        for entry in entries:
            pub=entry.find('.//news:publication_date',nns); dt=parse_iso(pub.text.strip()) if pub is not None and pub.text else None
            if not dt or dt.tzinfo is None: errors.append('News sitemap publication_date must be timezone-aware')
            elif now-dt.astimezone(timezone.utc)>timedelta(days=2): errors.append('News sitemap contains article older than two days')
        if 'Sitemap: https://bezpecnaelektrika.sk/news-sitemap.xml' not in robots: errors.append('robots.txt must advertise news-sitemap.xml when file exists')
    except Exception as e: errors.append(f'Invalid news-sitemap.xml: {e}')
elif 'news-sitemap.xml' in robots: errors.append('robots.txt must not advertise a missing news-sitemap.xml')

# Automated search smoke test mirrors the public scoring contract.
try:
    proc=subprocess.run([sys.executable,str(ROOT/'tools/test-search-index.py')],cwd=ROOT,text=True,capture_output=True,timeout=20)
    if proc.returncode!=0: errors.append('Search smoke test failed: '+proc.stdout.replace('\n',' | '))
except Exception as e:
    errors.append(f'Could not run search smoke test: {e}')

if errors:
    print('RELEASE CHECK FAILED')
    for e in sorted(set(errors)): print('-',e)
    sys.exit(1)
print('RELEASE CHECK OK')
print('Root:',ROOT)
print('HTML pages:',sum(1 for _ in ROOT.rglob('*.html')))
