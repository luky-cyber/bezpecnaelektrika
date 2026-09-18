#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
errors=[]
def text(rel): return (ROOT/rel).read_text(encoding='utf-8')

readme=text('README.md')
try:
    m=re.match(r'^# Bezpečná elektrika v(\d+)\.(\d+)\.(\d+)', readme)
    current=tuple(map(int,m.groups())) if m else (0,0,0)
    if current < (0,6,6): errors.append('README must identify v0.6.6 or later')
except Exception:
    errors.append('Could not parse README release version')
if '## v0.6.6 – Production hardening & accessibility' not in readme:
    errors.append('README v0.6.6 summary missing')
try:
    v=json.loads(text('version.json'))
    if v.get('project')!='Bezpečná elektrika': errors.append('version.json project mismatch')
    vm=re.match(r'^(\d+)\.(\d+)\.(\d+)$',str(v.get('version','')))
    vv=tuple(map(int,vm.groups())) if vm else (0,0,0)
    if vv < (0,6,6): errors.append('version.json must be v0.6.6 or later')
    rel=str(v.get('release','')); base=f"v{v.get('version')}"
    if not (rel==base or re.match(r'^'+re.escape(base)+r'-rc\d+$',rel)): errors.append('version.json release/version mismatch')
    if not v.get('fingerprint'): errors.append('version.json fingerprint missing')
except Exception as e:
    errors.append(f'Invalid version.json: {e}')

for rel in ['RELEASE-v0.6.6.md','docs/PRODUCTION-HARDENING-v0.6.6.md','tools/validate-production-v066.py']:
    if not (ROOT/rel).is_file(): errors.append(f'Missing v0.6.6 artifact: {rel}')

# Certificate must keep preview in HTML but defer full-resolution viewer image until first open.
about=text('o-projekte/index.html')
soup=BeautifulSoup(about,'html.parser')
img=soup.select_one('#credential-viewer [data-credential-image]')
full='/assets/img/osvedcenie-e2a-lukas-likavcan-verejna-kopia.webp'
if not img: errors.append('Credential viewer full image element missing')
else:
    if img.has_attr('src'): errors.append('Credential full image must not have eager src in closed dialog')
    if img.get('data-src')!=full: errors.append('Credential full image data-src mismatch')
dialog=soup.find('dialog',id='credential-viewer')
if not dialog or dialog.get('aria-describedby')!='credential-viewer-hint': errors.append('Credential viewer aria-describedby missing')
stage=soup.find(id='credential-viewer-stage')
if not stage: errors.append('Credential viewer stage id missing')
zoom=soup.select_one('[data-credential-zoom]')
if not zoom or zoom.get('aria-controls')!='credential-viewer-stage' or zoom.get('aria-pressed')!='false': errors.append('Credential zoom state/control semantics missing')

viewer=text('assets/js/credential-viewer.js')
for needle in ['image.hasAttribute("src")','image.dataset.src','image.setAttribute("src", src)','zoom.setAttribute("aria-pressed"','opener?.focus()','if (dialog.open) dialog.close()']:
    if needle not in viewer: errors.append(f'Credential deferred/a11y behavior missing: {needle}')
css=text('assets/css/components.css')
for needle in ['.credential-viewer[open]{display:grid;grid-template-rows:auto minmax(0,1fr) auto','.credential-viewer:not([open]){display:none','min-height:44px','min-height:0','flex-wrap:wrap']:
    if needle not in css: errors.append(f'Credential reflow CSS missing: {needle}')
for forbidden in ['height:calc(100% - 112px)','credential-viewer__hint{height:48px']:
    if forbidden in css: errors.append(f'Legacy fixed viewer sizing remains: {forbidden}')

# Consent: same consent-first logic, deterministic focus return and mobile reflow.
consent=text('assets/js/consent.js')
for needle in ['let settingsOpener = null','settingsOpener = event?.currentTarget','restoreSettingsFocus','dialog.addEventListener("close", restoreSettingsFocus)','closeSettings();\n    hideBanner();']:
    if needle not in consent: errors.append(f'Consent focus/close guardrail missing: {needle}')
for needle in ['analytics_storage: analyticsStorage','ad_storage: "denied"','getChoice() !== "analytics"','sanitizeAnalyticsUrl']:
    if needle not in consent: errors.append(f'Consent/privacy guardrail regressed: {needle}')
v040=text('assets/css/v040.css')
for needle in ['min-height:44px','@media(max-width:420px)','max-height:94dvh']:
    if needle not in v040: errors.append(f'Consent reflow/touch CSS missing: {needle}')

# Static markup integrity relevant to accessibility and layout stability.
seen_titles={}
seen_canonicals={}
for hp in ROOT.rglob('*.html'):
    raw=hp.read_text(encoding='utf-8')
    soup=BeautifulSoup(raw,'html.parser')
    ids=[tag.get('id') for tag in soup.find_all(attrs={'id':True})]
    dup=sorted({x for x in ids if ids.count(x)>1})
    if dup: errors.append(f'Duplicate HTML ids in {hp.relative_to(ROOT)}: {dup}')
    for img_tag in soup.find_all('img'):
        if not img_tag.has_attr('alt'): errors.append(f'Image without alt in {hp.relative_to(ROOT)}: {img_tag.get("src") or img_tag.get("data-src")}')
        if not img_tag.get('width') or not img_tag.get('height'): errors.append(f'Image without intrinsic dimensions in {hp.relative_to(ROOT)}: {img_tag.get("src") or img_tag.get("data-src")}')
    titles=soup.head.find_all('title',recursive=False) if soup.head else []
    if len(titles)!=1: errors.append(f'Expected one title in {hp.relative_to(ROOT)}; got {len(titles)}')
    elif titles[0].get_text(strip=True):
        title=titles[0].get_text(strip=True)
        if title in seen_titles: errors.append(f'Duplicate title: {hp.relative_to(ROOT)} and {seen_titles[title]}')
        else: seen_titles[title]=str(hp.relative_to(ROOT))
    canon=soup.find('link',rel='canonical')
    if canon and canon.get('href'):
        href=canon['href']
        if href in seen_canonicals: errors.append(f'Duplicate canonical: {hp.relative_to(ROOT)} and {seen_canonicals[href]}')
        else: seen_canonicals[href]=str(hp.relative_to(ROOT))

# Existing accessibility basics remain.
base=text('assets/css/base.css'); responsive=text('assets/css/responsive.css')
if ':focus-visible' not in base: errors.append('Global focus-visible style missing')
if '.skip-link' not in base: errors.append('Skip-link CSS missing')
if '@media(prefers-reduced-motion:reduce)' not in responsive: errors.append('Reduced-motion CSS missing')
for hp in ROOT.rglob('*.html'):
    raw=hp.read_text(encoding='utf-8')
    if hp.name=='404.html' or '<body' in raw:
        if '<a class="skip-link" href="#obsah">' not in raw:
            errors.append(f'Skip link missing: {hp.relative_to(ROOT)}')

# Crawler/indexability and pre-commercial invariants.
robots=text('robots.txt')
for block in ['User-agent: OAI-SearchBot\nAllow: /','User-agent: ChatGPT-User\nAllow: /','User-agent: GPTBot\nDisallow: /']:
    if block not in robots: errors.append(f'Crawler policy missing: {block.replace(chr(10)," / ")}')
search=text('hladat/index.html')
if 'noindex,follow' not in search: errors.append('/hladat/ must remain noindex,follow')
if 'https://bezpecnaelektrika.sk/hladat/' in text('sitemap.xml'): errors.append('/hladat/ must remain outside sitemap')
allhtml='\n'.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html'))
for bad in ['"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed','href="tel:']:
    if bad in allhtml: errors.append(f'Forbidden Commercial Switch marker: {bad}')

# Technical hardening does not churn content dates.
if '2026-09-11' not in text('sitemap.xml'): errors.append('Expected existing 2026-09-11 content lastmods missing')
if '"dateModified":' not in about: errors.append('O mne content date missing')

# Generated CSS must be current.
try:
    import subprocess
    r=subprocess.run([sys.executable,str(ROOT/'tools/build-css.py'),'--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if r.returncode: errors.append('Generated style.css is not synchronized with CSS modules')
except Exception as e: errors.append(f'CSS build check failed: {e}')

if errors:
    print('V0.6.6 CHECK FAILED')
    for e in sorted(set(errors)): print(' -',e)
    sys.exit(1)
print('V0.6.6 CHECK OK · deferred credential asset + viewer reflow/a11y + consent focus/reflow + production-validation workflow + crawler/pre-commercial guardrails')
