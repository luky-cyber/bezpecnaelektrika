#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import re, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def text(rel): return (ROOT/rel).read_text(encoding='utf-8')

components=text('assets/css/components.css')
v040=text('assets/css/v040.css')
main_js=text('assets/js/main.js')
consent_js=text('assets/js/consent.js')

# 1) Light-theme legacy accent is aligned with the AA-safe v0.4+ token.
if 'html[data-theme="light"]{--accent:#137672}' not in components:
    errors.append('Missing v0.6.3 light-theme legacy accent override')

def luminance(hex_color):
    h=hex_color.lstrip('#')
    vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    vals=[v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in vals]
    return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]

def contrast(a,b):
    l1,l2=sorted((luminance(a),luminance(b)),reverse=True)
    return (l1+.05)/(l2+.05)

for bg in ['#f5f8fa','#ffffff','#edf3f6','#f2f7f8']:
    ratio=contrast('#137672',bg)
    if ratio < 4.5:
        errors.append(f'Legacy light accent contrast below 4.5:1 on {bg}: {ratio:.2f}')

# 2) Every actual main nav gets an explicit Home link on desktop and mobile; only homepage marks it current.
html_pages=list(ROOT.rglob('*.html'))
nav_pages=[]
for p in html_pages:
    soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    nav=soup.find(id='main-nav')
    if not nav:
        continue
    nav_pages.append(p)
    primary=nav.select_one('.nav-primary')
    home=nav.select_one('a.nav-home-link[href="/"]')
    if not primary or not home:
        errors.append(f'Missing main-nav Home link: {p.relative_to(ROOT)}')
        continue
    first_link=primary.find('a')
    if first_link is not home:
        errors.append(f'Home must be first primary-nav link: {p.relative_to(ROOT)}')
    if p == ROOT/'index.html':
        if 'active' not in (home.get('class') or []) or home.get('aria-current')!='page':
            errors.append('Homepage Home link must have active aria-current=page state')
    elif 'active' in (home.get('class') or []) or home.has_attr('aria-current'):
        errors.append(f'Non-home Home link must not be current: {p.relative_to(ROOT)}')

if len(nav_pages)!=35:
    errors.append(f'Expected 35 main-nav pages, found {len(nav_pages)}')
if '.nav-home-link{display:block}' not in components:
    errors.append('Home link must be visible in the complete desktop/mobile main nav')

# 3) Poradna term popovers have explicit accessible close controls and JS support.
poradna=BeautifulSoup(text('poradna/index.html'),'html.parser')
popovers=poradna.select('[data-term-popover]')
if len(popovers)!=2:
    errors.append(f'Expected 2 Poradna term popovers, found {len(popovers)}')
for pop in popovers:
    close=pop.select_one('button.term-popover__close')
    if not close or not close.get('aria-label'):
        errors.append('Each term popover needs an aria-labelled close button')
for needle in [
    'item.querySelector(".term-popover__close")?.addEventListener("click"',
    'close(item);',
    'trigger?.focus();',
    'item.classList.add("is-dismissed")',
    'item.addEventListener("mouseleave"'
]:
    if needle not in main_js:
        errors.append(f'Missing term-popover close JS guardrail: {needle}')
for needle in ['.term-popover__close{','position:absolute','width:1.8rem','height:1.8rem','.term-popover.is-dismissed .term-popover__bubble']:
    if needle not in v040:
        errors.append(f'Missing term-popover close CSS: {needle}')
if '@media(min-width:621px) and (max-width:1100px)' not in v040:
    errors.append('Existing 621–1100px popover viewport anchoring must remain')

# 4) Revisions hero receives a later v0.6.3 sizing override without deleting v0.6.2 baseline.
for needle in [
    'width:clamp(218px,18vw,252px)', # v0.6.2 baseline remains
    'width:clamp(270px,22vw,320px)', # v0.6.3 desktop override
    'max-width:88%',
    'width:180px',
    'height:180px'
]:
    if needle not in v040:
        errors.append(f'Missing Revisions logo hardening guardrail: {needle}')

# 5) Consent dialog has an explicit accessible name; behavior/IDs remain stable.
for needle in [
    'dialog.id = "consent-settings";',
    'dialog.setAttribute("aria-labelledby", "consent-settings-title");',
    '<h2 id="consent-settings-title">Nastavenia analytiky</h2>',
    'id="consent-analytics"'
]:
    if needle not in consent_js:
        errors.append(f'Missing consent accessibility/behavior guardrail: {needle}')


# 6) Homepage is visibly distinct from /revizie/ while remaining service-first.
home_soup=BeautifulSoup(text('index.html'),'html.parser')
home_h1=(home_soup.find('h1') or {}).get_text(' ',strip=True)
if home_h1!='Viac než revízie elektrických zariadení': errors.append('Homepage differentiation H1 missing or changed')
brand=home_soup.select_one('.home-brand-intro__name')
brand_logo=home_soup.select_one('.home-brand-intro__logo')
if not brand or brand.get_text(' ',strip=True)!='Bezpečná elektrika': errors.append('Homepage brand lockup name missing')
if not brand_logo or brand_logo.get('src')!='/assets/img/bezpecna-elektrika-logo-header.webp': errors.append('Homepage brand lockup logo missing')
if 'Pripravované revízne služby' not in text('index.html') or 'Opýtať sa na revíziu' not in text('index.html'): errors.append('Homepage must retain service-first lead and CTA')
for needle in ['.home-brand-intro{','.home-brand-intro__logo{','.contact-utility{','.contact-utility__qr{']:
    if needle not in v040: errors.append(f'Missing homepage/contact CSS guardrail: {needle}')

# 7) vCard + QR contact utility: public pre-commercial fields only.
vcf_path=ROOT/'bezpecna-elektrika-lukas-likavcan.vcf'; legacy_vcf_path=ROOT/'kontakt.vcf'; qr_path=ROOT/'assets/img/qr/bezpecnaelektrika-vcard.png'
if not vcf_path.exists(): errors.append('Missing bezpecna-elektrika-lukas-likavcan.vcf')
else:
    raw=vcf_path.read_bytes()
    if b'\r\n' not in raw or b'\n' in raw.replace(b'\r\n',b''): errors.append('Main vCard must use CRLF line endings')
    vcf=raw.decode('utf-8')
    for needle in ['BEGIN:VCARD','VERSION:3.0','kontakt@bezpecnaelektrika.sk','https://bezpecnaelektrika.sk/','END:VCARD']:
        if needle not in vcf: errors.append(f'Main vCard missing: {needle}')
    for forbidden in ['TEL','ADR','REVIZNY TECHNIK','REVÍZNY TECHNIK']:
        if forbidden in vcf.upper(): errors.append(f'Main vCard contains forbidden pre-commercial field: {forbidden}')
if not qr_path.exists(): errors.append('Missing vCard QR image')
else:
    try:
        from PIL import Image
        with Image.open(qr_path) as im:
            if im.width < 492 or im.height < 492 or im.width!=im.height: errors.append(f'vCard QR image must be square and scan-friendly, got {im.size}')
    except Exception as e: errors.append(f'Could not inspect vCard QR: {e}')
vcf_link=home_soup.select_one('a[href="/bezpecna-elektrika-lukas-likavcan.vcf"][download]')
qr_img=home_soup.select_one('img[src="/assets/img/qr/bezpecnaelektrika-vcard.png"]')
if not vcf_link: errors.append('Homepage vCard download link missing')
if not qr_img or not qr_img.get('alt'): errors.append('Homepage vCard QR image/alt missing')
if not (ROOT/'.gitattributes').exists() or '*.vcf binary' not in (ROOT/'.gitattributes').read_text(encoding='ascii'): errors.append('.gitattributes must preserve vCard line endings')

# 8) Meaningful homepage copy change gets content/crawl timestamps.

# 9) Release remains pre-commercial.
allhtml=''.join(p.read_text(encoding='utf-8') for p in html_pages)
for bad in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed','href="tel:']:
    if bad in allhtml:
        errors.append(f'Forbidden pre-commercial element: {bad}')

# 10) Production CSS stays generated from modules.
try:
    proc=subprocess.run([sys.executable,str(ROOT/'tools/build-css.py'),'--check'],cwd=ROOT,text=True,capture_output=True,timeout=20)
    if proc.returncode:
        errors.append('CSS build check failed: '+proc.stdout.replace('\n',' | '))
except Exception as e:
    errors.append(f'Could not run CSS check: {e}')


# v0.6.3 RC4 QR/vCard + desktop polish guardrails
from PIL import Image as _V063Image
_qr = ROOT/'assets/img/qr/bezpecnaelektrika-vcard.png'
with _V063Image.open(_qr) as _im:
    if _im.size != (492,492):
        errors.append(f'v0.6.3 contact QR asset must remain 492x492 px, got {_im.size}')
_vcf_bytes=(ROOT/'bezpecna-elektrika-lukas-likavcan.vcf').read_bytes()
if _vcf_bytes.startswith(b'\xef\xbb\xbf'):
    errors.append('v0.6.3 vCard must not contain UTF-8 BOM')
if b'\r\n' not in _vcf_bytes or _vcf_bytes.count(b'\n') != _vcf_bytes.count(b'\r\n'):
    errors.append('v0.6.3 vCard must use CRLF line endings')
try:
    _vcf=_vcf_bytes.decode('utf-8')
except UnicodeDecodeError:
    errors.append('v0.6.3 vCard must be valid UTF-8')
    _vcf=''
for _needle in ['VERSION:3.0','FN;CHARSET=utf-8:Ing. Lukáš Likavčan, PhD.','N;CHARSET=utf-8:Likavčan;Lukáš;;Ing.;PhD.','ORG;CHARSET=utf-8:Bezpečná elektrika']:
    if _needle not in _vcf:
        errors.append(f'v0.6.3 vCard UTF-8 compatibility marker missing: {_needle}')
if 'QUOTED-PRINTABLE' in _vcf or '=C3=' in _vcf or '=C4=' in _vcf or '=C5=' in _vcf:
    errors.append('v0.6.3 Outlook compatibility: vCard must not use quoted-printable UTF-8 sequences')
_qr_html=home_soup.select_one('img[src="/assets/img/qr/bezpecnaelektrika-vcard.png"]')
if not _qr_html or _qr_html.get('width')!='492' or _qr_html.get('height')!='492':
    errors.append('v0.6.3 homepage QR intrinsic HTML dimensions must stay 492x492')
if 'width:min(208px,24vw)' not in v040 or 'width:min(192px,100%)' not in v040:
    errors.append('v0.6.3 compact contact QR display CSS missing')
if '.page-hero h1{font-size:clamp(2.7rem,5.2vw,4.5rem)' not in v040:
    errors.append('v0.6.3 hub H1 desktop scale guardrail missing')
if '.profile-link-cta{' not in v040:
    errors.append('v0.6.3 professional profile CTA emphasis missing')
about=BeautifulSoup(text('o-projekte/index.html'),'html.parser')
if not about.select_one('a.profile-link-cta[href="https://likavcan.cz/lukas/"]'):
    errors.append('O mne professional profile CTA class missing')
if '"dateModified":"2026-08-31"' not in text('index.html'):
    errors.append('Homepage dateModified must reflect final v0.6.3 content change date')
if '<loc>https://bezpecnaelektrika.sk/</loc>\n    <lastmod>2026-08-31</lastmod>' not in text('sitemap.xml'):
    errors.append('Homepage sitemap lastmod must reflect final v0.6.3 content change date')


# v0.6.3 RC5 — certificate status, O mne contact and named vCard.
_main_vcf=ROOT/'bezpecna-elektrika-lukas-likavcan.vcf'
_legacy_vcf=ROOT/'kontakt.vcf'
if not _main_vcf.exists():
    errors.append('RC5 named vCard missing')
elif _legacy_vcf.exists() and _legacy_vcf.read_bytes()!=_main_vcf.read_bytes():
    errors.append('Legacy /kontakt.vcf alias must stay byte-identical to named vCard')
if _main_vcf.exists():
    _b=_main_vcf.read_bytes()
    _ref_needles=[
        b'BEGIN:VCARD\r\nVERSION:3.0\r\n',
        'FN;CHARSET=utf-8:Ing. Lukáš Likavčan, PhD.'.encode('utf-8'),
        'N;CHARSET=utf-8:Likavčan;Lukáš;;Ing.;PhD.'.encode('utf-8'),
        'ORG;CHARSET=utf-8:Bezpečná elektrika'.encode('utf-8'),
    ]
    for _n in _ref_needles:
        if _n not in _b: errors.append('RC5 vCard no longer matches likavcan.cz UTF-8 profile')
    if _b.startswith(b'\xef\xbb\xbf'): errors.append('RC5 vCard must not have BOM')
    if b'QUOTED-PRINTABLE' in _b.upper(): errors.append('RC5 vCard must not use quoted-printable')
_about=BeautifulSoup(text('o-projekte/index.html'),'html.parser')
if not _about.select_one('a.about-contact-compact__email[href="mailto:kontakt@bezpecnaelektrika.sk"]'):
    errors.append('O mne compact email missing')
if not _about.select_one('a[href="/bezpecna-elektrika-lukas-likavcan.vcf"][download]'):
    errors.append('O mne named vCard download missing')
if not _about.select_one('.about-contact-compact__qr img[src="/assets/img/qr/bezpecnaelektrika-vcard.png"]'):
    errors.append('O mne compact QR missing')
if 'Osvedčenie: vydané' not in text('o-projekte/index.html'):
    errors.append('O mne certificate status must be vydané')
_runtime_html='\n'.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html'))
for _old in ['Osvedčenie: čakám','čakám na osvedčenie','čakám na vydanie osvedčenia']:
    if _old in _runtime_html:
        errors.append(f'Stale certificate waiting text remains in runtime HTML: {_old}')
if 'osvedčenie bolo vydané' not in text('index.html') or 'osvedčenie bolo vydané' not in text('revizie/index.html'):
    errors.append('Homepage/Revisions issued-certificate wording missing')
if '.about-contact-compact{' not in v040:
    errors.append('O mne compact contact CSS missing')

if errors:
    print('V0.6.3 CHECK FAILED')
    for e in sorted(set(errors)): print(' -',e)
    sys.exit(1)
print('V0.6.3 CHECK OK · Home nav + light accent + popover close + Revisions logo + consent a11y + homepage differentiation + compact URL QR + named UTF-8 vCard + O mne contact + issued-certificate status + hub H1 polish')
