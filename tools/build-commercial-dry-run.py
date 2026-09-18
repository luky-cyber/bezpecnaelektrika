#!/usr/bin/env python3
"""Build an isolated full-state commercial dry-run outside the production surface.

The output intentionally simulates the future commercial copy/CTA layer while keeping
all unresolved business decisions visible. It is never a production build.
"""
from pathlib import Path
from bs4 import BeautifulSoup
import argparse, json, re, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / '.build/commercial-dry-run'
SKIP = {'.git', '.build', 'docs', 'tools', 'config', '__pycache__'}
CUSTOMER_PATHS = {'index.html', 'revizie/index.html'}

# Status wording that would contradict a simulated commercial state. Keep this list
# narrow: generic editorial wording such as "pripravované epizódy" is not a commercial marker.
FORBIDDEN_DRY_RUN_MARKERS = [
    'Komerčné revízne služby zatiaľ nie sú spustené',
    'Komerčné služby zatiaľ neposkytujem',
    'komerčné služby zatiaľ neposkytujem',
    'Komerčné služby ešte neposkytujem',
    'komerčné služby ešte neposkytujem',
    'Komerčné služby ešte nie sú spustené',
    'komerčné služby ešte nie sú spustené',
    'Služby zatiaľ nie sú spustené',
    'Služby pripravujem. Zákazky zatiaľ neprijímam',
    'Revízne služby zatiaľ pripravujem a zákazky ešte neprijímam',
    'Pripravované služby revízneho technika',
    'pripravovaným revíziám',
    'služby zatiaľ nie sú spustené',
    'Služby sú zatiaľ v príprave',
    'služby sú zatiaľ v príprave',
    'Revízne služby sú zatiaľ v príprave',
    'revízne služby sú zatiaľ v príprave',
    'Pripravované revízne služby',
    'pripravované revízne služby',
    'Pripravované revízie elektrických zariadení',
    'pripravované revízie elektrických zariadení',
    'Kontakt k pripravovaným revíznym službám',
    'kontakt k pripravovaným revíznym službám',
    'k pripravovaným revíznym službám',
    'K pripravovaným službám',
    'k pripravovaným službám',
    'Pripravovaný rozsah',
    'pripravovaný rozsah',
    'pripravovanému rozsahu',
    'Po spustení sa chcem sústrediť',
    'Po spustení je plánované zameranie',
    'Ceny budú zverejnené pri spustení služieb',
    'Sú revízne služby už spustené?',
]

RAW_REPLACEMENTS = [
    ('Komerčné revízne služby zatiaľ nie sú spustené; obchodná identita budúcich služieb sa preto na tejto stránke nepredstiera ani nedopĺňa odhadom.',
     'V komerčnej simulácii sa identita a kontaktné údaje zobrazia iba podľa schváleného business/legal modelu; táto dry-run vrstva nič reálne nepublikuje.'),
    ('Komerčné revízne služby zatiaľ nie sú spustené.', 'Revízne služby sú v tomto dry-rune simulované ako dostupné.'),
    ('Bezpečná elektrika pripravuje revízne služby pre elektrické zariadenia a inštalácie a zároveň ponúka',
     'Bezpečná elektrika poskytuje revízne služby pre elektrické zariadenia a inštalácie a zároveň ponúka'),
    ('Bezpečná elektrika pripravuje revízne služby pre rodinné domy, byty a vybrané administratívne priestory.',
     'Bezpečná elektrika poskytuje revízne služby pre rodinné domy, byty a vybrané administratívne priestory.'),
    ('Pripravované revízie elektroinštalácií pre domy, byty a vybrané administratívne priestory.',
     'Revízie elektroinštalácií pre domy, byty a vybrané administratívne priestory.'),
    ('Pripravované revízne služby pre rodinné domy, byty a vybrané administratívne priestory.',
     'Revízne služby pre rodinné domy, byty a vybrané administratívne priestory.'),
    ('Pripravované revízne služby a odborný obsah o elektrickej bezpečnosti.',
     'Revízne služby a odborný obsah o elektrickej bezpečnosti.'),
    ('Revízne služby v rozsahu E2A sú v príprave. Skúška je úspešne absolvovaná, osvedčenie je vydané a komerčné služby zatiaľ neposkytujem.',
     'Odborná spôsobilosť E2/A je doložená vydaným osvedčením. Revízne služby sú v tomto dry-rune simulované ako dostupné.'),
    ('Pripravované revízie v rozsahu E2A. Skúška je úspešne absolvovaná, osvedčenie je vydané a komerčné služby zatiaľ neposkytujem.',
     'Revízie v rozsahu E2/A. Skúška je úspešne absolvovaná a osvedčenie je vydané.'),
    ('E2A skúška je úspešne absolvovaná, osvedčenie je vydané a komerčné služby zatiaľ neposkytujem.',
     'E2/A skúška je úspešne absolvovaná a osvedčenie je vydané.'),
    ('Skúška revízneho technika je úspešne absolvovaná a osvedčenie bolo vydané. Komerčné služby zatiaľ neposkytujem.',
     'Skúška revízneho technika je úspešne absolvovaná a osvedčenie bolo vydané. Revízne služby sú v tomto dry-rune simulované ako dostupné.'),
    ('Služby zatiaľ nie sú spustené.', 'Revízne služby sú dostupné.'),
    ('Služby pripravujem. Zákazky zatiaľ neprijímam.', 'Revízne služby sú dostupné.'),
    ('Revízne služby zatiaľ pripravujem a zákazky ešte neprijímam.', 'Revízne služby sú dostupné.'),
    ('Pripravované služby revízneho technika', 'Služby revízneho technika'),
    ('Máte otázku k pripravovaným revíziám?', 'Máte otázku k revíziám?'),
    ('Ak chcete vedieť, či sa budem venovať aj vašej situácii, napíšte mi.', 'Ak chcete overiť, či sa vaša situácia týka rozsahu služieb, napíšte mi.'),
    ('pripravovaným revíziám', 'revíziám'),
    ('Revízne služby sú zatiaľ v príprave.', 'Revízne služby sú dostupné.'),
    ('Projekt sa pripravuje na spustenie.', 'Revízne služby a odborný obsah.'),
    ('Pripravujem revízne služby pre elektrické zariadenia a inštalácie', 'Poskytujem revízne služby pre elektrické zariadenia a inštalácie'),
    ('komerčné služby zatiaľ nie sú spustené', 'revízne služby sú dostupné'),
    ('Revízne služby projektu Bezpečná elektrika sú zatiaľ v príprave.', 'Revízne služby projektu Bezpečná elektrika sú dostupné.'),
    ('Revízne služby sú dostupné. Revízne služby sú dostupné, ale otázku k rozsahu služieb môžete poslať e-mailom.', 'K revíznym službám môžete poslať otázku e-mailom.'),
    ('čo plánujem revidovať', 'čo revidujem'),
    ('Aktuálny stav pripravovaných služieb', 'Aktuálny stav revíznych služieb'),
    ('Komerčné služby ešte neposkytujem', 'Revízne služby sú dostupné'),
    ('komerčné služby ešte neposkytujem', 'revízne služby sú dostupné'),
    ('Komerčné služby ešte nie sú spustené. K pripravovaným službám sa môžete ozvať e-mailom.',
     'Revízne služby sú dostupné. Pre kontakt použite e-mail.'),
    ('Revízne služby sú zatiaľ v príprave. Komerčné služby ešte neposkytujem, ale otázku k pripravovanému rozsahu môžete poslať e-mailom.',
     'K revíznym službám môžete poslať otázku e-mailom.'),
    ('Komerčné služby zatiaľ neposkytujem. Ak chcete vedieť, či bude vaša situácia patriť do pripravovaného rozsahu, môžete sa ozvať.',
     'Ak chcete overiť, či vaša situácia patrí do rozsahu služieb, môžete sa ozvať.'),
    ('Komerčné služby zatiaľ neposkytujem; otázku k pripravovanému rozsahu môžete poslať e-mailom.',
     'K revíznym službám môžete poslať otázku e-mailom.'),
    ('Nie. Služby sú zatiaľ v príprave a komerčné služby zatiaľ neposkytujem.',
     'Revízne služby sú dostupné; konkrétny rozsah a podmienky sa potvrdia pri kontakte.'),
    ('Po spustení sa chcem sústrediť na situácie, ktoré sa dajú pomenovať podľa objektu a potreby zákazníka.',
     'Zameranie služieb vychádza z typu objektu a konkrétnej potreby zákazníka.'),
    ('Áno. Po spustení je plánované zameranie na rodinné domy a byty v príslušnom rozsahu.',
     'Áno. Zameranie služieb zahŕňa rodinné domy a byty v príslušnom rozsahu.'),
    ('Áno, plánované zameranie zahŕňa aj systém ochrany pred bleskom na rodinných domoch.',
     'Áno, zameranie služieb zahŕňa aj systém ochrany pred bleskom na rodinných domoch.'),
    ('Áno. Plánované zameranie zahŕňa elektrické spotrebiče a predlžovacie prívody používané v administratívnych priestoroch.',
     'Áno. Zameranie služieb zahŕňa elektrické spotrebiče a predlžovacie prívody používané v administratívnych priestoroch.'),
    ('Ceny budú zverejnené pri spustení služieb.', 'Cenový model je uvedený v internom dry-run rozhodovacom paneli.'),
    ('Sú revízne služby už spustené?', 'Ako sa objednáva revízia?'),
    ('Budete robiť revízie rodinných domov a bytov?', 'Robíte revízie rodinných domov a bytov?'),
    ('Budete robiť aj ochranu pred bleskom?', 'Robíte aj ochranu pred bleskom?'),
    ('Budete kontrolovať spotrebiče v kanceláriách?', 'Kontrolujete spotrebiče v kanceláriách?'),
    ('Máte otázku k pripravovaným revíznym službám?', 'Máte otázku k revíznym službám?'),
    ('Chcete sa ozvať k pripravovaným revíznym službám?', 'Chcete sa ozvať k revíznym službám?'),
    ('Kontakt k pripravovaným revíznym službám →', 'Kontakt k revíznym službám →'),
    ('K pripravovanému rozsahu sa môžete ozvať e-mailom.', 'K rozsahu služieb sa môžete ozvať e-mailom.'),
    ('Pozrite si pripravované zameranie revízií', 'Pozrite si zameranie revízií'),
    ('Ako prebieha odborné overovanie a čo pripravované služby zahŕňajú.', 'Ako prebieha odborné overovanie a čo revízne služby zahŕňajú.'),
    ('Pozrite si, ako sa zdroje, prehliadka, skúšanie, meranie a odborné vyhodnotenie prepájajú pri pripravovanom revíznom procese.',
     'Pozrite si, ako sa zdroje, prehliadka, skúšanie, meranie a odborné vyhodnotenie prepájajú pri revíznom procese.'),
    ('Autor a pripravované služby:', 'Autor a revízne služby:'),
    ('Pripravovaný rozsah LPS →', 'Rozsah LPS →'),
    ('Pripravovaný rozsah →', 'Rozsah služieb →'),
    ('Pripravované revízie →', 'Revízie →'),
    ('Pripravované revízie elektrických zariadení.', 'Revízie elektrických zariadení.'),
    ('Pripravované revízne služby', 'Revízne služby'),
    ('pripravované revízne služby', 'revízne služby'),
    ('pripravovaným revíznym službám', 'revíznym službám'),
    ('pripravovanému rozsahu', 'rozsahu služieb'),
    ('Pripravovaný rozsah', 'Rozsah služieb'),
    ('pripravovaný rozsah', 'rozsah služieb'),
]


def copy_public(out: Path):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for p in ROOT.rglob('*'):
        rel = p.relative_to(ROOT)
        if not rel.parts or any(x in SKIP for x in rel.parts):
            continue
        if p.is_dir():
            continue
        if p.suffix.lower() == '.md' or p.name.endswith('.zip'):
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)


def replace_customer_copy(raw: str) -> str:
    for old, new in RAW_REPLACEMENTS:
        raw = raw.replace(old, new)
    return raw


def force_noindex(soup: BeautifulSoup):
    if not soup.head:
        return
    tag = soup.find('meta', attrs={'name': 'robots'})
    if not tag:
        tag = soup.new_tag('meta')
        tag['name'] = 'robots'
        soup.head.append(tag)
    tag['content'] = 'noindex,nofollow'


def add_banner(soup: BeautifulSoup, fixture: dict):
    if not soup.body:
        return
    banner = soup.new_tag('div', attrs={'class': 'commercial-dry-run-banner', 'role': 'status'})
    banner.string = fixture['banner']
    soup.body.insert(0, banner)


def add_decision_panel(soup: BeautifulSoup, fixture: dict):
    main = soup.find('main')
    if not main:
        return
    panel = soup.new_tag('aside', attrs={'class': 'commercial-dry-run-decisions', 'aria-label': 'Neuzavreté rozhodnutia commercial dry-runu'})
    h = soup.new_tag('strong'); h.string = 'Commercial dry-run · rozhodnutia pred GO-LIVE'; panel.append(h)
    fields = [
        ('Obchodná identita', 'businessIdentity'),
        ('Finálny rozsah služieb', 'serviceScope'),
        ('Oblasť pôsobenia', 'serviceArea'),
        ('Cenový model', 'pricingModel'),
        ('Kontaktná cesta', 'commercialContactPath'),
        ('Kapacita', 'capacity'),
        ('Poistenie', 'insuranceApplicability'),
        ('Schema kandidát', 'schemaCandidate'),
    ]
    dl = soup.new_tag('dl')
    for label, key in fields:
        dt = soup.new_tag('dt'); dt.string = label; dl.append(dt)
        dd = soup.new_tag('dd'); dd.string = fixture[key]; dl.append(dd)
    panel.append(dl)
    first = main.find('section', recursive=False)
    if first:
        first.insert_after(panel)
    else:
        main.insert(0, panel)


def add_cta(soup: BeautifulSoup, fixture: dict):
    main = soup.find('main')
    if not main or not soup.body:
        return
    anchor = soup.new_tag('aside', attrs={'class': 'commercial-dry-run-inline', 'id': 'commercial-dry-run-anchor'})
    strong = soup.new_tag('strong'); strong.string = fixture['ctaLead']; anchor.append(strong)
    link = soup.new_tag('a', href='mailto:' + fixture['email']); link.string = fixture['ctaAction']; anchor.append(link)
    sections = main.find_all('section', recursive=False)
    target = sections[1] if len(sections) > 1 else (sections[0] if sections else None)
    if target:
        target.insert_after(anchor)
    else:
        main.append(anchor)

    sticky = soup.new_tag('aside', attrs={'class': 'commercial-dry-run-sticky', 'id': 'commercial-dry-run-sticky', 'hidden': ''})
    s = soup.new_tag('strong'); s.string = fixture['ctaLead']; sticky.append(s)
    a = soup.new_tag('a', href='mailto:' + fixture['email']); a.string = fixture['ctaAction']; sticky.append(a)
    soup.body.append(sticky)

    script = soup.new_tag('script')
    script.string = '''(()=>{const a=document.getElementById("commercial-dry-run-anchor"),s=document.getElementById("commercial-dry-run-sticky"),f=document.querySelector("footer");if(!a||!s)return;let passed=false,footer=false;const paint=()=>{s.hidden=!passed||footer};new IntersectionObserver(([e])=>{passed=!e.isIntersecting&&e.boundingClientRect.top<0;paint()},{threshold:0}).observe(a);if(f)new IntersectionObserver(([e])=>{footer=e.isIntersecting;paint()},{threshold:.05}).observe(f)})();'''
    soup.body.append(script)


def add_schema_candidate(soup: BeautifulSoup, fixture: dict):
    if not soup.head:
        return
    candidate = {
        'status': 'candidate-only-not-jsonld',
        'reason': 'Unresolved GO/NO-GO inputs must not become production structured data.',
        'candidate': {
            '@context': 'https://schema.org',
            '@type': 'Service',
            'name': 'Revízie elektrických zariadení a inštalácií',
            'provider': {'@type': 'Person', '@id': 'https://likavcan.cz/lukas/#lukas-likavcan'},
            'areaServed': fixture['serviceArea'],
            'offers': fixture['pricingModel'],
        },
        'decision': fixture['schemaCandidate'],
    }
    script = soup.new_tag('script', attrs={'type': 'application/json', 'id': 'commercial-schema-candidate'})
    script.string = json.dumps(candidate, ensure_ascii=False, separators=(',', ':'))
    soup.head.append(script)


def add_styles(soup: BeautifulSoup):
    if not soup.head:
        return
    style = soup.new_tag('style')
    style.string = '''
.commercial-dry-run-banner{position:fixed;z-index:10000;right:.6rem;bottom:.6rem;padding:.4rem .6rem;background:#721c24;color:#fff;font:700 12px/1.2 system-ui;border-radius:.45rem}
.commercial-dry-run-decisions{margin:1rem auto;padding:1rem;max-width:900px;border:2px solid #b86b00;background:#fff7e8;color:#2d2418;border-radius:.7rem}.commercial-dry-run-decisions>strong{display:block;margin-bottom:.6rem}.commercial-dry-run-decisions dl{display:grid;grid-template-columns:minmax(10rem,1fr) 2fr;gap:.35rem .8rem;margin:0}.commercial-dry-run-decisions dt{font-weight:700}.commercial-dry-run-decisions dd{margin:0;overflow-wrap:anywhere}
.commercial-dry-run-inline{margin:1rem auto;padding:.85rem 1rem;max-width:760px;border:1px dashed currentColor;display:flex;justify-content:space-between;gap:1rem;align-items:center}
.commercial-dry-run-sticky{position:fixed;z-index:150;top:var(--header,72px);left:50%;transform:translateX(-50%);width:min(calc(100% - 1rem),760px);padding:.65rem .85rem;background:var(--c-surface,#111923);border:1px solid var(--c-line,#334);border-radius:0 0 .7rem .7rem;box-shadow:0 8px 28px rgba(0,0,0,.2);display:flex;justify-content:space-between;gap:.8rem;align-items:center}.commercial-dry-run-sticky[hidden]{display:none}
@media(max-width:640px){.commercial-dry-run-sticky{font-size:.86rem}.commercial-dry-run-inline{margin-inline:.7rem}.commercial-dry-run-decisions{margin-inline:.7rem}.commercial-dry-run-decisions dl{grid-template-columns:1fr}.commercial-dry-run-decisions dd{margin:0 0 .45rem}}
'''
    soup.head.append(style)


def transform_html(path: Path, rel: str, fixture: dict):
    raw = replace_customer_copy(path.read_text(encoding='utf-8'))
    soup = BeautifulSoup(raw, 'html.parser')
    force_noindex(soup)
    add_banner(soup, fixture)
    add_styles(soup)
    if rel == 'index.html':
        if soup.h1:
            soup.h1.string = fixture['homepageH1']
        lead = soup.select_one('.service-hero-lead')
        if lead:
            lead.clear(); lead.string = fixture['homepageLead']
    if rel in CUSTOMER_PATHS:
        add_decision_panel(soup, fixture)
        add_cta(soup, fixture)
        add_schema_candidate(soup, fixture)
    if rel == 'revizie/index.html':
        price = soup.select_one('#cena .service-price-note strong')
        if price:
            price.string = 'Cenový model: ' + fixture['pricingModel']
        price_p = soup.select_one('#cena .service-price-note p')
        if price_p:
            price_p.string = 'Dry-run zámerne nezastiera, že finálny spôsob nacenenia ešte nie je GO rozhodnutie.'
    path.write_text(str(soup), encoding='utf-8')


def transform_llms(out: Path):
    path = out / 'llms.txt'
    if not path.is_file():
        raise RuntimeError('llms.txt missing from dry-run public surface')
    raw = replace_customer_copy(path.read_text(encoding='utf-8'))
    path.write_text(raw, encoding='utf-8')


def write_dry_version(out: Path, release: dict):
    public = {k: release[k] for k in ['project', 'version', 'release', 'date']}
    public.update({
        'channel': 'local-dry-run',
        'fingerprint': release['fingerprint'] + '-commercial-simulation',
        'commercialState': 'commercial-simulation',
        'sourceRelease': release['release'],
        'production': False,
    })
    (out / 'version.json').write_text(json.dumps(public, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def rebuild_search_index(out: Path):
    cmd = [
        sys.executable, str(ROOT / 'tools/build-search-index.py'),
        '--root', str(out),
        '--output', str(out / 'data/search-index.json'),
        '--include-noindex', '--commercial-simulation',
    ]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        raise RuntimeError('Dry-run Search rebuild failed: ' + r.stdout + r.stderr)


def assert_full_state(out: Path, fixture: dict):
    errors = []
    html = sorted(out.rglob('*.html'))
    for p in html:
        raw = p.read_text(encoding='utf-8')
        if 'noindex,nofollow' not in raw:
            errors.append(f'noindex,nofollow missing: {p.relative_to(out)}')
        if fixture['banner'] not in raw:
            errors.append(f'dry-run banner missing: {p.relative_to(out)}')
        for marker in FORBIDDEN_DRY_RUN_MARKERS:
            if marker in raw:
                errors.append(f'precommercial marker remains in {p.relative_to(out)}: {marker}')
    for rel in CUSTOMER_PATHS:
        raw = (out / rel).read_text(encoding='utf-8')
        for key in ['businessIdentity', 'serviceScope', 'serviceArea', 'pricingModel', 'commercialContactPath', 'capacity', 'insuranceApplicability', 'schemaCandidate']:
            if fixture[key] not in raw:
                errors.append(f'dry-run fixture field not rendered in {rel}: {key}')
        for needle in ['commercial-dry-run-inline', 'commercial-dry-run-sticky', 'commercial-schema-candidate', fixture['ctaLead']]:
            if needle not in raw:
                errors.append(f'commercial full-state element missing in {rel}: {needle}')
    public_text = {}
    for rel in ['llms.txt', 'data/search-index.json']:
        path = out / rel
        if not path.is_file():
            errors.append(f'dry-run public artifact missing: {rel}')
            continue
        public_text[rel] = path.read_text(encoding='utf-8')
        for marker in FORBIDDEN_DRY_RUN_MARKERS:
            if marker in public_text[rel]:
                errors.append(f'precommercial marker remains in {rel}: {marker}')
    try:
        idx = json.loads((out / 'data/search-index.json').read_text(encoding='utf-8'))
        if len(idx.get('records', [])) != 39:
            errors.append(f'dry-run Search record count mismatch: {len(idx.get("records", []))}')
    except Exception as e:
        errors.append(f'dry-run Search index parse failed: {e}')
    try:
        version = json.loads((out / 'version.json').read_text(encoding='utf-8'))
        if version.get('channel') != 'local-dry-run':
            errors.append('dry-run version.json channel must be local-dry-run')
        if version.get('commercialState') != 'commercial-simulation':
            errors.append('dry-run version.json commercialState must be commercial-simulation')
        if version.get('production') is not False:
            errors.append('dry-run version.json production must be false')
    except Exception as e:
        errors.append(f'dry-run version.json parse failed: {e}')
    if errors:
        raise RuntimeError('\n'.join(errors))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, default=DEFAULT)
    args = ap.parse_args()
    out = args.output.resolve()
    fixture = json.loads((ROOT / 'config/commercial-dry-run.json').read_text(encoding='utf-8'))
    if out == ROOT or (ROOT in out.parents and '.build' not in out.parts):
        print('Refusing to write dry-run into production tree outside .build', file=sys.stderr)
        return 2
    copy_public(out)
    release = json.loads((ROOT / 'config/release.json').read_text(encoding='utf-8'))
    for p in sorted(out.rglob('*.html')):
        transform_html(p, p.relative_to(out).as_posix(), fixture)
    try:
        transform_llms(out)
        write_dry_version(out, release)
        rebuild_search_index(out)
        assert_full_state(out, fixture)
    except RuntimeError as e:
        print('COMMERCIAL DRY RUN FAILED', file=sys.stderr)
        print(e, file=sys.stderr)
        return 1
    manifest = {
        'build': 'commercial-full-state-dry-run',
        'production': False,
        'robots': 'noindex,nofollow',
        'sourceVersion': release['release'],
        'commercialSimulation': True,
        'publicSurface': ['HTML', 'data/search-index.json', 'llms.txt', 'version.json'],
        'dryRunChannel': 'local-dry-run',
        'dryRunCommercialState': 'commercial-simulation',
        'unresolvedDecisionFields': [
            'businessIdentity', 'serviceScope', 'serviceArea', 'pricingModel',
            'commercialContactPath', 'capacity', 'insuranceApplicability', 'schemaCandidate'
        ],
    }
    (out / 'dry-run-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'COMMERCIAL FULL-SURFACE DRY RUN OK · {len(list(out.rglob("*.html")))} HTML + Search + llms.txt + version.json · {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
