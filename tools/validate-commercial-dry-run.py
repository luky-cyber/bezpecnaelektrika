#!/usr/bin/env python3
"""Validate the isolated v0.7-style commercial dry-run without publishing it."""
from pathlib import Path
import json, shutil, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
errors = []
fixture = json.loads((ROOT / 'config/commercial-dry-run.json').read_text(encoding='utf-8'))
source_release = json.loads((ROOT / 'config/release.json').read_text(encoding='utf-8'))['release']

# Publication boundary is a prerequisite, not a substitute for noindex.
if (ROOT / '.nojekyll').exists():
    errors.append('.nojekyll must not exist: GitHub Pages exclusions depend on Jekyll processing')
config = (ROOT / '_config.yml').read_text(encoding='utf-8')
for needle in ['  - config/', '  - .build/', '  - tools/', '  - docs/']:
    if needle not in config:
        errors.append(f'Publication exclusion missing: {needle}')

out = Path(tempfile.mkdtemp(prefix='be-commercial-dry-run-')) / 'site'
try:
    r = subprocess.run(
        [sys.executable, str(ROOT / 'tools/build-commercial-dry-run.py'), '--output', str(out)],
        cwd=ROOT, capture_output=True, text=True, encoding='utf-8'
    )
    if r.returncode:
        errors.append('Dry-run build failed: ' + r.stdout.replace('\n', ' | ') + r.stderr.replace('\n', ' | '))
    else:
        html = sorted(out.rglob('*.html'))
        production_html = [p for p in ROOT.rglob('*.html') if '.build' not in p.parts]
        if len(html) != len(production_html):
            errors.append(f'Dry-run HTML count mismatch: {len(html)} vs production {len(production_html)}')
        for p in html:
            raw = p.read_text(encoding='utf-8')
            if 'noindex,nofollow' not in raw:
                errors.append(f'Dry-run noindex,nofollow missing: {p.relative_to(out)}')
            if fixture['banner'] not in raw:
                errors.append(f'Dry-run banner missing: {p.relative_to(out)}')
        for rel in ['index.html', 'revizie/index.html']:
            raw = (out / rel).read_text(encoding='utf-8')
            for needle in ['commercial-dry-run-inline', 'commercial-dry-run-sticky', 'commercial-dry-run-decisions', 'commercial-schema-candidate', fixture['ctaLead']]:
                if needle not in raw:
                    errors.append(f'Full-state commercial element missing in {rel}: {needle}')
            for key in ['businessIdentity', 'serviceScope', 'serviceArea', 'pricingModel', 'commercialContactPath', 'capacity', 'insuranceApplicability', 'schemaCandidate']:
                if fixture[key] not in raw:
                    errors.append(f'Unresolved decision not rendered in {rel}: {key}')
        all_html = '\n'.join(p.read_text(encoding='utf-8') for p in html)
        forbidden = [
            'Komerčné revízne služby zatiaľ nie sú spustené',
            'Komerčné služby zatiaľ neposkytujem', 'komerčné služby zatiaľ neposkytujem',
            'Komerčné služby ešte neposkytujem', 'komerčné služby ešte neposkytujem',
            'Komerčné služby ešte nie sú spustené', 'komerčné služby ešte nie sú spustené',
            'Služby zatiaľ nie sú spustené', 'služby zatiaľ nie sú spustené',
            'Služby pripravujem. Zákazky zatiaľ neprijímam',
            'Revízne služby zatiaľ pripravujem a zákazky ešte neprijímam',
            'Pripravované služby revízneho technika', 'pripravovaným revíziám',
            'Revízne služby sú zatiaľ v príprave', 'revízne služby sú zatiaľ v príprave',
            'Revízne služby projektu Bezpečná elektrika sú zatiaľ v príprave',
            'Pripravované revízne služby', 'pripravované revízne služby',
            'Pripravované revízie elektrických zariadení', 'pripravované revízie elektrických zariadení',
            'Kontakt k pripravovaným revíznym službám', 'k pripravovaným revíznym službám',
            'Pripravovaný rozsah', 'pripravovaný rozsah', 'pripravovanému rozsahu',
            'Po spustení sa chcem sústrediť', 'Po spustení je plánované zameranie',
            'Ceny budú zverejnené pri spustení služieb', 'Sú revízne služby už spustené?',
        ]
        for marker in forbidden:
            if marker in all_html:
                errors.append(f'Pre-commercial contradiction remains in dry-run HTML: {marker}')
        for rel in ['llms.txt', 'data/search-index.json']:
            path = out / rel
            if not path.is_file():
                errors.append(f'Dry-run public artifact missing: {rel}')
                continue
            raw = path.read_text(encoding='utf-8')
            for marker in forbidden:
                if marker in raw:
                    errors.append(f'Pre-commercial contradiction remains in {rel}: {marker}')
        try:
            idx = json.loads((out / 'data/search-index.json').read_text(encoding='utf-8'))
            if len(idx.get('records', [])) != 39:
                errors.append(f'Dry-run Search record count mismatch: {len(idx.get("records", []))}')
        except Exception as e:
            errors.append(f'Dry-run Search parse failed: {e}')
        try:
            version = json.loads((out / 'version.json').read_text(encoding='utf-8'))
            if version.get('release') != source_release or version.get('sourceRelease') != source_release:
                errors.append('Dry-run version.json source release mismatch')
            if version.get('channel') != 'local-dry-run':
                errors.append('Dry-run version.json channel mismatch')
            if version.get('commercialState') != 'commercial-simulation' or version.get('production') is not False:
                errors.append('Dry-run version.json commercial-simulation state mismatch')
        except Exception as e:
            errors.append(f'Dry-run version.json parse failed: {e}')
        manifest = json.loads((out / 'dry-run-manifest.json').read_text(encoding='utf-8'))
        if manifest.get('production') is not False or manifest.get('commercialSimulation') is not True:
            errors.append('Dry-run manifest state mismatch')
        if manifest.get('publicSurface') != ['HTML', 'data/search-index.json', 'llms.txt', 'version.json']:
            errors.append('Dry-run manifest publicSurface mismatch')
finally:
    shutil.rmtree(out.parent, ignore_errors=True)

# Production source must remain pre-commercial and free of dry-run UI/schema candidate.
prod = '\n'.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.html') if '.build' not in p.parts)
for bad in ['commercial-dry-run-sticky', 'commercial-dry-run-decisions', 'commercial-schema-candidate', 'DRY RUN – NEPUBLIKOVAŤ', 'Potrebujete revíziu?']:
    if bad in prod:
        errors.append(f'Dry-run marker leaked into production HTML: {bad}')
if (ROOT / '.build').exists():
    errors.append('.build must not be present in release candidate payload')

if errors:
    print('COMMERCIAL DRY-RUN CHECK FAILED')
    for e in sorted(set(errors)):
        print(' -', e)
    raise SystemExit(1)
print('COMMERCIAL DRY-RUN CHECK OK · full-surface transform + Search/llms/version sync + unresolved decisions + zero pre-commercial contradictions + publication isolation')
