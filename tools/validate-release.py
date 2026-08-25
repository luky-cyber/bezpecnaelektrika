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

# Every canonical content URL should be represented in sitemap; 404 is intentionally excluded.
for p in ROOT.rglob('*.html'):
    if p.name=='404.html': continue
    txt=p.read_text(encoding='utf-8')
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

if errors:
    print('RELEASE CHECK FAILED')
    for e in sorted(set(errors)): print('-',e)
    sys.exit(1)
print('RELEASE CHECK OK')
print('Root:',ROOT)
print('HTML pages:',sum(1 for _ in ROOT.rglob('*.html')))
