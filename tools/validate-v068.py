#!/usr/bin/env python3
from pathlib import Path
import json, re, subprocess, sys, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []

def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')

def run(label, argv):
    r = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        errors.append(f'{label} failed: {r.stdout[-900:]} {r.stderr[-500:]}')

# v0.6.8 RC16 artifacts and release identity.
for rel in [
    'config/release.json', 'config/commercial-state.json', 'config/commercial-dry-run.json',
    'tools/sync-release-identity.py', 'tools/build-commercial-dry-run.py',
    'tools/validate-commercial-dry-run.py', 'tools/validate-podcasts.py',
    'tools/validate-production-v068.py', 'COMMERCIAL-GO-LIVE.md',
    'docs/COMMERCIAL-SWITCH-v0.7.0.md', 'docs/PRODUCTION-ACCEPTANCE-v0.6.8.md', 'RELEASE-v0.6.8.md'
]:
    if not (ROOT / rel).is_file():
        errors.append(f'Missing v0.6.8 artifact: {rel}')
try:
    cfg = json.loads(text('config/release.json'))
    public = json.loads(text('version.json'))
    expected = {
        'project': 'Bezpečná elektrika',
        'version': '0.6.8',
        'release': 'v0.6.8-rc16',
        'channel': 'release-candidate',
        'date': '2026-09-18',
        'fingerprint': 'be-v0.6.8-rc16-search-cache-revalidation',
        'commercialState': 'precommercial',
    }
    for k, val in expected.items():
        if cfg.get(k) != val: errors.append(f'config/release.json {k} mismatch: {cfg.get(k)!r}')
        if public.get(k) != val: errors.append(f'version.json {k} mismatch: {public.get(k)!r}')
except Exception as e:
    errors.append(f'Release identity JSON parse failed: {e}')
run('Release identity sync --check', [sys.executable, str(ROOT / 'tools/sync-release-identity.py'), '--check'])

# Every production HTML page exposes the same visible build marker.
html = [p for p in ROOT.rglob('*.html') if '.build' not in p.parts]
if len(html) != 42:
    errors.append(f'Expected 42 production HTML files, got {len(html)}')
for p in html:
    raw = p.read_text(encoding='utf-8')
    if raw.count('data-release-version="v0.6.8-rc16"') != 1:
        errors.append(f'Visible release marker missing/duplicate: {p.relative_to(ROOT)}')
    if '>v0.6.8-rc16</a>' not in raw:
        errors.append(f'Visible release text missing: {p.relative_to(ROOT)}')

# Fail-closed commercial state.
try:
    cs = json.loads(text('config/commercial-state.json'))
    if cs.get('state') != 'precommercial' or cs.get('goLiveAllowed') is not False or cs.get('publicCommercialServices') is not False:
        errors.append('Commercial state is not fail-closed precommercial')
    required = cs.get('requiredDecisions') or {}
    for k in ['businessLegalSetup', 'serviceScope', 'serviceArea', 'pricingModel', 'commercialContactPath', 'capacity', 'insuranceApplicability']:
        if required.get(k) != 'blocked':
            errors.append(f'Commercial decision must remain blocked in RC16: {k}')
except Exception as e:
    errors.append(f'Commercial state parse failed: {e}')

# Publication boundary: Jekyll exclusions are the primary boundary; noindex is only defense-in-depth.
if (ROOT / '.nojekyll').exists():
    errors.append('.nojekyll must not exist; _config.yml exclusions require Jekyll processing')
config = text('_config.yml')
for needle in ['  - config/', '  - .build/', '  - tools/', '  - docs/']:
    if needle not in config:
        errors.append(f'Publication exclusion missing: {needle}')
if (ROOT / '.build').exists():
    errors.append('.build must not be present in release candidate payload')

allhtml = '\n'.join(p.read_text(encoding='utf-8') for p in html)
for bad in [
    '"@type":"LocalBusiness"', '"@type":"Electrician"', '"@type":"Service"',
    '"@type":"Offer"', '"@type":"ProfessionalService"', 'areaServed', 'href="tel:',
    'Potrebujete revíziu?', 'commercial-dry-run-sticky', 'commercial-dry-run-decisions',
    'commercial-schema-candidate', 'DRY RUN – NEPUBLIKOVAŤ'
]:
    if bad in allhtml:
        errors.append(f'Commercial/dry-run marker leaked into production HTML: {bad}')

for required in [
    'Overall: **NO-GO**', 'Commercial/business legal setup | BLOCKED',
    'Final service scope | BLOCKED', 'Pricing model / price path | BLOCKED',
    'Full-surface local noindex dry-run'
]:
    if required not in text('COMMERCIAL-GO-LIVE.md'):
        errors.append(f'GO/NO-GO gate missing: {required}')
spec = text('docs/COMMERCIAL-SWITCH-v0.7.0.md')
for required in ['ProfessionalService` is not used', 'Do not publish a home address', 'Full-state commercial dry-run', 'no pre-commercial status wording may remain', 'rebuild the Search index', 'update `llms.txt`', 'whole public surface']:
    if required not in spec:
        errors.append(f'Commercial Switch specification missing: {required}')

# RC4 hardening invariants retained in RC6.
css_source = text('assets/css/v040.css')
if '.site-footer .footer-release a{color:inherit;font-size:.69rem;font-weight:750;text-decoration:none;opacity:1}' not in css_source:
    errors.append('Footer release link must not reduce text contrast with opacity')
search_builder = text('tools/build-search-index.py')
for required in ['--root', '--include-noindex', '--commercial-simulation']:
    if required not in search_builder:
        errors.append(f'Search builder missing dry-run interface: {required}')
dry_builder = text('tools/build-commercial-dry-run.py')
for required in ['transform_llms', 'rebuild_search_index', "'commercialState': 'commercial-simulation'", "'channel': 'local-dry-run'"]:
    if required not in dry_builder:
        errors.append(f'Commercial dry-run full-surface guardrail missing: {required}')

# Modular v0.6.8 acceptance.
run('Commercial full-surface dry-run validator', [sys.executable, str(ROOT / 'tools/validate-commercial-dry-run.py')])
run('Generic podcast integrity validator', [sys.executable, str(ROOT / 'tools/validate-podcasts.py')])

# Counts/indexability/search remain stable from RC1.
try:
    tree = ET.parse(ROOT / 'sitemap.xml')
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [e.text for e in tree.findall('.//s:loc', ns)]
    if len(urls) != 40: errors.append(f'Expected 40 sitemap URLs, got {len(urls)}')
    if 'https://bezpecnaelektrika.sk/hladat/' in urls: errors.append('/hladat/ must remain outside sitemap')
except Exception as e:
    errors.append(f'Sitemap parse failed: {e}')
try:
    idx = json.loads(text('data/search-index.json'))
    if len(idx.get('records', [])) != 39:
        errors.append(f'Expected 39 search records, got {len(idx.get("records", []))}')
except Exception as e:
    errors.append(f'Search index parse failed: {e}')
if 'noindex,follow' not in text('hladat/index.html'):
    errors.append('/hladat/ must remain noindex,follow')

# RC4 changes content only where audits justified it; unchanged release-only pages must not be mass-touched.
if '<lastmod>2026-09-14</lastmod>' not in text('sitemap.xml'):
    errors.append('RC5 editorial pass pages must expose 2026-09-14 lastmod')

# RC4 cross-discipline hardening invariants retained by RC5.
for rel in ['.gitignore', 'requirements-validation.txt', '.github/workflows/validate.yml', 'docs/RC4-HARDENING-v0.6.8.md']:
    if not (ROOT / rel).is_file(): errors.append(f'Missing RC4 hardening artifact: {rel}')
if '.build/' not in text('.gitignore') or '__pycache__/' not in text('.gitignore'):
    errors.append('.gitignore does not protect generated build/Python artifacts')
if 'mainNav.querySelector("a")?.focus()' not in text('assets/js/main.js'):
    errors.append('Mobile nav must move focus into the opened menu')
consent = text('assets/js/consent.js')
for required in ['POLICY_VERSION', 'decidedAt', 'DECISION_MAX_AGE_MS', '--consent-clearance']:
    if required not in consent: errors.append(f'Consent RC4 hardening missing: {required}')
css = text('assets/css/v040.css')
for required in ['--c-control-border:#718b94', '--c-control-border:#7896a0', 'body.consent-visible']:
    if required not in css: errors.append(f'WCAG RC4 CSS hardening missing: {required}')
if 'class="hero-visual-v04 service-hero-visual reveal"' in text('index.html') or 'fetchpriority="high"' not in text('index.html'):
    errors.append('Homepage LCP hero hardening missing')
if 'podcast-transcript' not in text('tools/build-search-index.py'):
    errors.append('Search builder must exclude raw podcast transcript snippets')
podcast_hub = text('podcast/index.html')
if 'Načítavam zoznam epizód' in podcast_hub or podcast_hub.count('class="episode-card') < 5:
    errors.append('Podcast hub must expose SSR episode cards')
if 'audio.load()' in text('assets/js/podcast.js'):
    errors.append('Podcast hub must not preload audio before explicit Play')
if '„100 % v poriadku“ nie je odborný záver' not in text('podcast/be-002-merat-nie-hadat/index.html'):
    errors.append('BE-002 safety correction missing')
if 'zámerne nereprodukujte' not in text('poradna/prudovy-chranic-opakovane-vypina/index.html'):
    errors.append('RCD active-fault safety boundary missing')
if 'FAQPage' in text('poradna/index.html') + text('revizie/index.html'):
    errors.append('Deprecated Google FAQPage markup must remain removed in RC10')
if '"@type":"ProfilePage"' not in text('o-projekte/index.html'):
    errors.append('O mne ProfilePage semantics missing')
if 'Opýtať sa na revíziu' in text('index.html') + text('revizie/index.html'):
    errors.append('Precommercial CTA must not use old transaction-like wording')
# RC5 simplification + RC6 customer-clarity + RC10 final-copy invariants.
poradna_hub = text('poradna/index.html')
if 'id="faq"' in poradna_hub or 'Krátke odpovede a detail o klik ďalej' in poradna_hub:
    errors.append('RC10 Poradna hub must not duplicate the question catalogue in a second FAQ layer')
if '<span>' in ''.join(re.findall(r'<li>.*?</li>', text('obsah/index.html'), flags=re.S)):
    errors.append('RC10 content map must remain a concise link map without duplicated page descriptions')
for obsolete in [
    'Všeobecná odpoveď pomáha pochopiť problém, ale stav konkrétnej elektroinštalácie',
    'Zdroje uvádzam s kontextom, aby bolo zrejmé, čo z nich na tejto stránke vychádza',
    'Audio rozhovor vzniká z odborne pripravených podkladov pomocou Gemini Notebook',
    'Komerčné služby ešte neposkytujem, ale otázku k pripravovanému rozsahu môžete poslať e-mailom.',
    'Kalibrácia nie je kúzelná nálepka správnosti.',
    'Jedna veličina, viac spôsobov vysvetlenia.',
]:
    if obsolete in allhtml:
        errors.append(f'RC10 obsolete editorial boilerplate still public: {obsolete}')
if 'Zs ≠ Zline' not in text('glosar/impedancia-poruchovej-slucky-zs/index.html'):
    errors.append('RC10 must retain the critical Zs != Zline distinction')
if 'Rodinný dom teda automaticky neznamená LPS III ani inú konkrétnu triedu.' not in text('glosar/lps-ochrana-pred-bleskom/index.html'):
    errors.append('RC10 must retain the LPS class anti-anchoring rule')
if 'Podcast vysvetľuje technické témy, nenahrádza však odborné posúdenie konkrétnej elektroinštalácie.' not in text('podcast/index.html'):
    errors.append('RC10 podcast hub safety boundary missing')
if text('revizie/index.html').count('<details>') > 2:
    errors.append('RC10 Revisions FAQ should contain only non-duplicative questions')

# RC6 customer clarity / human voice invariants retained in RC10.
home = text('index.html')
rev = text('revizie/index.html')
advice = text('poradna/index.html')
for required in ['Pripravované služby revízneho technika', 'Revízie elektrických zariadení a inštalácií', 'Služby pripravujem. Zákazky zatiaľ neprijímam.', 'Napísať mi e-mail', 'Viac než samotná revízna správa.', 'Merať. Dokumentovať. Vysvetľovať.']:
    if required not in home:
        errors.append(f'RC10 homepage customer-clarity invariant missing: {required}')
for obsolete in ['Viac než revízie elektrických zariadení</h1>', 'Opýtať sa e-mailom', 'požadovaný rozsah revízie', 'Úkony potrebné pre konkrétnu inštaláciu']:
    if obsolete in home + rev:
        errors.append(f'RC10 administrative/old customer copy remains: {obsolete}')
if 'data-term-popover' in advice or '>LPS<' in advice or '>RCD<' in advice:
    errors.append('RC10 Poradna first decision layer must use customer terms, not acronym popovers')
if 'Ak chcete ísť viac do technického detailu' not in advice:
    errors.append('RC10 Poradna expert-content handoff missing')
if 'Rozsah osvedčenia: E2A' not in home + rev:
    errors.append('RC10 E2A qualification must remain visible with a plain-language label')

# Historical regression chain.
for script in [
    ['tools/build-css.py', '--check'], ['tools/test-search-index.py'],
    ['tools/validate-v060.py'], ['tools/validate-v062.py'], ['tools/validate-v063.py'],
    ['tools/validate-v064.py'], ['tools/validate-v065.py'], ['tools/validate-v066.py'], ['tools/validate-v067.py']
]:
    run('Regression command ' + ' '.join(script), [sys.executable, str(ROOT / script[0]), *script[1:]])

# RC10 UX-only invariants: sticky desktop header, anchor clearance and revisions logo containment.
v040 = (ROOT / 'assets' / 'css' / 'v040.css').read_text(encoding='utf-8')
if '@media(min-width:901px)' not in v040 or 'position:sticky' not in v040 or '.site-header' not in v040:
    errors.append('RC10 desktop header must remain sticky')
if 'scroll-margin-top:calc(var(--header) + 18px)' not in v040:
    errors.append('RC10 fragment targets must retain sticky-header scroll clearance')
if '[data-prototype="service-revisions-a5"] .service-hero-logo{' not in v040 or 'aspect-ratio:2 / 3' not in v040 or 'overflow:hidden' not in v040:
    errors.append('RC10 revisions hero logo frame must use the source 2:3 portrait ratio and clip overflow')
if '[data-prototype="service-revisions-a5"] .service-hero-logo img{' not in v040 or 'object-fit:contain' not in v040:
    errors.append('RC10 revisions hero logo image must remain fully contained')
if '<h1>Revízie: rozsah, priebeh a cena</h1>' not in rev:
    errors.append('RC10 /revizie/ H1 must be distinct from the homepage service H1')
if '<h1>Revízie elektrických zariadení a inštalácií</h1>' not in home:
    errors.append('RC10 homepage direct service H1 must remain unchanged')
if '"dateModified":"2026-09-17"' not in rev:
    errors.append('RC10 /revizie/ dateModified must reflect the content change')


# RC10 visual-system + navigation UX guardrails.
for required in [
    'v0.6.8 RC10 — shared design DNA polish + targeted UX fixes',
    '--max:1160px',
    '--ds-r1:12px',
    '--ds-r2:16px',
    '--ds-r3:24px',
    'border-left:3px solid var(--c-accent);',
    '.service-intent-grid{grid-template-columns:repeat(2,minmax(0,1fr))',
    '#pripravovane-zameranie .service-scope{grid-template-columns:repeat(2,minmax(0,1fr))',
    '#kedy-a-ako-casto .service-checklist{grid-template-columns:repeat(2,minmax(0,1fr))',
    'grid-template-columns:repeat(2,minmax(0,1fr));\n    gap:.55rem 1.25rem;',
]:
    if required not in v040:
        errors.append(f'RC10 design-system guardrail missing: {required}')
main_js = text('assets/js/main.js')
for required in ['syncRevisionNavCurrent', '#kedy-a-ako-casto', '#cena', 'aria-current', 'hashchange', 'requestAnimationFrame', 'getBoundingClientRect']:
    if required not in main_js:
        errors.append(f'RC11 revision navigation state guardrail missing: {required}')
for required in ['trackedKeys', 'navigationIntent', 'startNavigationIntent', 'navigationIntentUntil', 'performance.now()', 'if (rect.top <= trigger) activeHash = item.key']:
    if required not in main_js:
        errors.append(f'RC12 stable Revisions navigation guardrail missing: {required}')
# RC14 homepage Contact semantics + retained RC13 mobile-dock state guardrails.
if '<section class="contact-section" id="kontakt"><div class="container"><div class="contact-section-head reveal"><h2>Kontakt</h2></div>' not in home:
    errors.append('RC14 homepage Contact must be a standalone semantic section and anchor destination')
if '<div class="contact-section-head reveal" id="kontakt">' in home:
    errors.append('RC14 contact anchor must live on the semantic section, not the heading wrapper')
if '<section class="section--compact expert-entry-section" id="kontakt">' in home:
    errors.append('RC14 contact anchor must not remain on the Practical questions section')
if '"dateModified":"2026-09-18"' not in home:
    errors.append('RC14 homepage must retain the RC13 content dateModified; semantic release hygiene alone does not advance it')
for required in ['syncHomeMobileContactCurrent', 'contactIntentUntil', 'a[href="/#kontakt"]', 'contactLink.setAttribute("aria-current", "location")']:
    if required not in main_js:
        errors.append(f'RC14 homepage Contact navigation guardrail missing: {required}')
for required in ['/* RC14 — semantic homepage Contact section, retaining RC13 visual destination. */', '.contact-section{\n  padding:0 0 clamp(2.25rem,4vw,3.25rem);\n  scroll-margin-top:calc(var(--header) + 18px);', '.contact-section-head{', 'border-top:1px solid var(--c-line);']:
    if required not in v040:
        errors.append(f'RC14 Contact visual/semantic guardrail missing: {required}')
for required in ['/* RC14 — remaining close controls meet the shared 44 px touch-target standard. */', '.site-search-close,\n.term-popover__close{', 'width:44px!important;', 'height:44px!important;', 'min-width:44px!important;', 'min-height:44px!important;', '.term-popover__bubble{padding-right:3.35rem}']:
    if required not in v040:
        errors.append(f'RC14 44px close-control guardrail missing: {required}')
readme = text('README.md')
if '# Bezpečná elektrika v0.6.8-rc16' not in readme or 'current release candidate v0.6.8-rc16' not in readme:
    errors.append('RC16 README current-release identity is stale')
release_notes = text('RELEASE-v0.6.8.md')
if 'uvádzajú STN 33 1630:2025 + STN EN 50699/50678' in release_notes:
    errors.append('RC14 release documentation still claims unpublished standards are visible on Revízie')
if '## RC14 — release hygiene + accessibility/contact semantics (2026-09-18)' not in release_notes:
    errors.append('RC14 release note missing')
if '## RC15 — credential viewer cold-start fit hardening (2026-09-18)' not in release_notes:
    errors.append('RC15 release note missing')

if '## RC16 — Search cache revalidation hardening (2026-09-18)' not in release_notes:
    errors.append('RC16 release note missing')

# RC16 Search index freshness: current editorial state must be revalidated,
# not indefinitely served from an older browser cache.
search_runtime = text('assets/js/search.js')
if 'cache: "force-cache"' in search_runtime:
    errors.append('RC16 Search runtime must not force-cache search-index.json')
if 'cache: "no-cache"' not in search_runtime:
    errors.append('RC16 Search runtime must revalidate search-index.json with no-cache')

# RC15 credential cold-start regression: open/measure the dialog before attaching the deferred
# full-resolution image, and make fit mode explicit while preserving the true 100 % dimensions.
viewer = text('assets/js/credential-viewer.js')
open_block_start = viewer.find('const open = (event) =>')
show_pos = viewer.find('dialog.showModal()', open_block_start)
raf_pos = viewer.find('requestAnimationFrame(() =>', open_block_start)
load_pos = viewer.find('ensureFullImage()', show_pos)
if min(open_block_start, show_pos, raf_pos, load_pos) < 0 or not (show_pos < raf_pos < load_pos):
    errors.append('RC15 credential cold-start ordering missing: dialog must open before deferred full image load')
credential_css = text('assets/css/components.css')
fit_rule = '.credential-viewer:not(.is-native) .credential-viewer__stage img{width:100%;height:100%;max-width:100%;max-height:100%;object-fit:contain}'
if fit_rule not in credential_css:
    errors.append('RC15 explicit credential fit-mode CSS missing')
if '.credential-viewer.is-native .credential-viewer__stage img{width:1097px;height:1536px;max-width:none;max-height:none' not in credential_css:
    errors.append('RC15 credential native 100% dimensions changed unexpectedly')

for required in [
    'v0.6.8 RC11 — shared authorial micro-UI/state language',
    '--ui-control-size:44px',
    '--ui-control-radius:12px',
    '--ui-active-bg:rgba(104,221,212,.08)',
    'box-shadow:inset 0 -2px 0 var(--ui-active-line)',
    '.mobile-bottom-nav a.active::before{display:none!important}',
    '.search-toggle[aria-expanded="true"]',
]:
    if required not in v040:
        errors.append(f'RC11 micro-UI guardrail missing: {required}')


if errors:
    print('V0.6.8 CHECK FAILED')
    for e in sorted(set(errors)):
        print(' -', e)
    raise SystemExit(1)
print('V0.6.8 CHECK OK · RC16 search cache revalidation + retained RC15 credential cold-start fit, navigation, design, a11y, safety and commercial guardrails')
