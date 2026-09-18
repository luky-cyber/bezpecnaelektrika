#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import json, os, re, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]
UTF8_ENV={**os.environ, "PYTHONUTF8":"1"}

def text(rel): return (ROOT/rel).read_text(encoding='utf-8')

consent=text('assets/js/consent.js')
main=text('assets/js/main.js')
search=text('assets/js/search.js')
podcast=text('assets/js/podcast.js')
readme=text('README.md')

# 1) Consent state changes are independent from the one-time GA script load.
for needle in [
    'const updateAnalyticsConsent = (granted) =>',
    'const ensureAnalyticsLoaded = () =>',
    'const grantAnalytics = () =>',
    'updateAnalyticsConsent(true);',
    'ensureAnalyticsLoaded();',
    'const denyAnalytics = () =>',
    'updateAnalyticsConsent(false);',
    'clearAnalyticsCookies();',
]:
    if needle not in consent:
        errors.append(f'Missing consent/regrant guardrail: {needle}')
# The old failure mode returned from loadAnalytics before sending a fresh granted update.
if re.search(r'function\s+loadAnalytics\s*\([^)]*\)\s*\{\s*if\s*\(analyticsLoaded\)\s*return', consent):
    errors.append('Old analyticsLoaded early-return consent bug is still present')

# 2) localStorage failure cannot abort theme/consent initialization.
for source,name in [(main,'main.js'),(consent,'consent.js')]:
    if 'try {' not in source or 'window.localStorage' not in source:
        errors.append(f'{name} missing safe localStorage wrapper')
if 'const safeStorageGet' not in main or 'const safeStorageSet' not in main:
    errors.append('Theme storage wrappers missing')
if 'const safeStorageGet' not in consent or 'const safeStorageSet' not in consent or 'memoryChoice' not in consent:
    errors.append('Consent storage fallback/memory state missing')
# Direct unguarded forms from v0.6.3 must be gone.
for bad in ['const storedTheme = localStorage.getItem', 'localStorage.setItem("be-theme"', 'localStorage.setItem(STORAGE_KEY', 'const value = localStorage.getItem(STORAGE_KEY)']:
    if bad in main+consent:
        errors.append(f'Unguarded localStorage access remains: {bad}')

# 3) Search privacy defense-in-depth: q remains usable locally but is redacted for GA.
for needle in [
    'url.pathname === "/hladat/"',
    'url.searchParams.set("q", "(redacted)")',
    'page_location: pageLocation',
    'config.page_referrer = pageReferrer',
    'window.beSetSafeAnalyticsLocation',
]:
    if needle not in consent:
        errors.append(f'Missing GA search privacy guardrail: {needle}')
if 'window.beSetSafeAnalyticsLocation?.(url.href);' not in search:
    errors.append('Search must set safe analytics location before history.replaceState')
pos_safe=search.find('window.beSetSafeAnalyticsLocation?.(url.href);')
pos_history=search.find('history.replaceState(null, "", url);')
if pos_safe < 0 or pos_history < 0 or pos_safe > pos_history:
    errors.append('Safe analytics URL must be set before history.replaceState')
if re.search(r'beTrack\?\.\([^\n]+(?:query|search_term)\s*:', search, re.I):
    errors.append('Search analytics must not send raw query/search_term')

# 4) Search relevance requires a genuine match; rejected index fetch can retry.
for needle in [
    'const QUESTION_STOPWORDS = new Set(',
    'const meaningfulTokens = queryTokens.filter((token) => !QUESTION_STOPWORDS.has(token));',
    'if (!score) return null;',
    'indexPromise = null;',
]:
    if needle not in search:
        errors.append(f'Missing v0.6.4 search guardrail: {needle}')
if search.find('if (!score) return null;') > search.find('if (questionIntent(q)'):
    errors.append('Question intent bonus is still able to manufacture a match')
try:
    proc=subprocess.run([sys.executable,str(ROOT/'tools/test-search-index.py')],cwd=ROOT,text=True,capture_output=True,timeout=20,env=UTF8_ENV)
    if proc.returncode:
        errors.append('Search smoke test failed: '+proc.stdout.replace('\n',' | '))
    for query in ['xyzqwerty','ako xyzqwerty','preco xyzqwerty','co xyzqwerty']:
        if query not in proc.stdout or f'{query}' not in proc.stdout:
            errors.append(f'Negative search case missing from smoke output: {query}')
except Exception as e:
    errors.append(f'Could not run search smoke test: {e}')

# 5) Visible professional link uses the real page, structured Person @id remains stable.
about=text('o-projekte/index.html')
soup=BeautifulSoup(about,'html.parser')
profile=soup.find('a',string=lambda x: x and 'Osobný profil na likavcan.cz' in x)
if not profile or profile.get('href')!='https://likavcan.cz/lukas/':
    errors.append('Visible O mne profile link must use https://likavcan.cz/lukas/')
if 'href="https://likavcan.cz/lukas/#lukas-likavcan"' in about:
    errors.append('Visible broken Person-fragment href remains on O mne')
if '"@id":"https://likavcan.cz/lukas/#lukas-likavcan"' not in about:
    errors.append('Stable Person JSON-LD @id must remain unchanged')

# 6) Podcast card semantics and visible audio error states.
podcast_html=text('podcast/index.html')
for needle in [
    'id="player-status"', 'role="status"', 'aria-live="polite"',
    'Vybrať epizódu', 'aria-pressed="false"',
    'audio.addEventListener("error"', 'setPlayerStatus("Audio sa momentálne nepodarilo načítať.',
    'setPlayerStatus("Prehrávanie sa nepodarilo spustiť.',
]:
    if needle not in podcast+podcast_html:
        errors.append(f'Missing podcast hardening guardrail: {needle}')
if '<button type="button" class="button episode-play">▶ Prehrať</button>' in podcast:
    errors.append('Episode selector is still mislabeled as Prehrať')
if '.player-status{' not in text('assets/css/components.css'):
    errors.append('Podcast player status styling missing from source CSS')

# 7) README/current status and release documentation are synchronized.
m_current=re.match(r'^# Bezpečná elektrika v(\d+)\.(\d+)\.(\d+)',readme)
if not m_current or tuple(map(int,m_current.groups())) < (0,6,4):
    errors.append('README must identify v0.6.4 or a later release')
for stale in ['certificate pending','čakám na vydanie osvedčenia','Osvedčenie: čakám']:
    if stale.lower() in readme.lower():
        errors.append(f'Stale certificate state remains in README: {stale}')
for needle in ['certificate issued','commercial services not yet launched','## v0.6.4 – Stability & consent hardening']:
    if needle not in readme:
        errors.append(f'README current-state marker missing: {needle}')
if not (ROOT/'RELEASE-v0.6.4.md').is_file():
    errors.append('Missing RELEASE-v0.6.4.md')

# 8) GitHub Pages publication boundary and build fingerprint.
config=text('_config.yml') if (ROOT/'_config.yml').is_file() else ''
for needle in ['"*.md"','docs/','tools/']:
    if needle not in config:
        errors.append(f'_config.yml missing repository-only exclusion: {needle}')
if (ROOT/'.nojekyll').exists():
    errors.append('.nojekyll would bypass the Jekyll exclude publication boundary')
try:
    version=json.loads(text('version.json'))
    if version.get('project')!='Bezpečná elektrika': errors.append(f"version.json project mismatch: {version.get('project')!r}")
    current=version.get('version','')
    m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',current)
    if not m or tuple(map(int,m.groups())) < (0,6,4):
        errors.append(f'version.json must identify v0.6.4 or later, got {current!r}')
    rel=str(version.get('release','')); base=f"v{current}"
    if not (rel==base or re.match(r'^'+re.escape(base)+r'-rc\d+$',rel)): errors.append(f"version.json release mismatch: {version.get('release')!r}")
    if not version.get('fingerprint'): errors.append('version.json fingerprint missing')
except Exception as e:
    errors.append(f'Invalid version.json: {e}')

# 9) Technical-only release: no artificial content timestamp churn.
if '2026-09-01' in text('sitemap.xml'):
    errors.append('Technical v0.6.4 must not churn sitemap lastmod to 2026-09-01')
for hp in ROOT.rglob('*.html'):
    if '"dateModified":"2026-09-01"' in hp.read_text(encoding='utf-8'):
        errors.append(f'Technical v0.6.4 must not churn content dateModified: {hp.relative_to(ROOT)}')

# 10) Pre-commercial boundary remains intact.
allhtml='\n'.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html'))
for bad in ['Objednať revíziu','"@type":"LocalBusiness"','"@type":"Electrician"','"@type":"Service"','"@type":"Offer"','areaServed','href="tel:']:
    if bad in allhtml:
        errors.append(f'Forbidden pre-commercial element: {bad}')
if 'mám vydané osvedčenie' not in text('index.html') or 'mám vydané osvedčenie' not in text('revizie/index.html'):
    errors.append('Issued-certificate status regressed')

# 11) General validator must be Windows-safe for nested Unicode search output.
release_validator=text('tools/validate-release.py')
if 'UTF8_ENV={**os.environ, "PYTHONUTF8":"1"}' not in release_validator:
    errors.append('validate-release.py missing UTF-8 subprocess environment')
if 'env=UTF8_ENV' not in release_validator:
    errors.append('validate-release.py nested subprocesses are not using UTF8_ENV')

# 12) RC2 mobile UX polish: hamburger utility links, QR size and safe touch popover dismissal.
html_pages=list(ROOT.rglob('*.html'))
nav_pages=0
for hp in html_pages:
    page=hp.read_text(encoding='utf-8')
    if 'nav-group nav-supplemental' not in page:
        continue
    nav_pages += 1
    soup=BeautifulSoup(page,'html.parser')
    nav=soup.select_one('.nav-supplemental')
    if not nav:
        errors.append(f'Missing supplemental nav after marker on {hp.relative_to(ROOT)}')
        continue
    for href in ['/metodika/','/obsah/']:
        link=nav.find('a',href=href)
        if not link or 'nav-mobile-omit' not in (link.get('class') or []):
            errors.append(f'Mobile hamburger omit marker missing for {href} on {hp.relative_to(ROOT)}')
if nav_pages < 30:
    errors.append(f'Unexpectedly few pages with supplemental nav: {nav_pages}')

v040=text('assets/css/v040.css')
for needle in [
    '.site-header .nav.open .nav-supplemental .nav-mobile-omit{display:none!important}',
    '.about-contact-compact{grid-template-columns:1fr;gap:.9rem;padding:.9rem}',
    '.about-contact-compact__qr{width:min(188px,58vw);justify-self:start}',
]:
    if needle not in v040:
        errors.append(f'Missing RC2 mobile CSS guardrail: {needle}')
for needle in [
    'const openItem = popovers.find((item) => item.classList.contains("is-open"));',
    'event.target.closest?.(".term-popover__trigger")',
    'window.matchMedia?.("(pointer: coarse)").matches',
    'event.preventDefault();',
    'event.stopImmediatePropagation();',
    '}, true);',
]:
    if needle not in main:
        errors.append(f'Missing RC2 touch-popover guardrail: {needle}')

# 13) Final-RC polish: remove copy-link UI, preserve deep-link targets, sync concise llms status.
copy_markers=['section-link-copy','article-link-copy','data-copy-anchor','data-copy-page','copy-toast','Odkaz na sekciu skopírovaný','Odkaz skopírovaný']
public_code=allhtml+'\n'+text('assets/js/main.js')+'\n'+text('assets/css/v040.css')
for marker in copy_markers:
    if marker in public_code:
        errors.append(f'Legacy copy-link UI marker still present: {marker}')
for path,anchor in [
    ('glosar/tn-c-tn-s-tn-c-s/index.html','suvislost-s-reviziou'),
    ('glosar/impedancia-poruchovej-slucky-zs/index.html','zs-nie-je-zline'),
    ('glosar/rcd-prudovy-chranic/index.html','tlacidlo-test'),
]:
    soup=BeautifulSoup(text(path),'html.parser')
    if not soup.find(id=anchor):
        errors.append(f'Deep-link anchor regressed: {path}#{anchor}')
llms=text('llms.txt')
for needle in ['rozsahu E2A je absolvovaná','osvedčenie vydané','Komerčné revízne služby zatiaľ nie sú spustené']:
    if needle not in llms:
        errors.append(f'llms.txt qualification/status sync missing: {needle}')

if errors:
    print('V0.6.4 CHECK FAILED')
    for e in sorted(set(errors)): print(' -',e)
    sys.exit(1)
print('V0.6.4 CHECK OK · consent regrant + safe storage + GA query redaction + negative search + profile link + podcast errors/semantics + mobile popover/nav/QR polish + copy-link UI cleanup + llms status sync + deployment boundary/fingerprint')
