#!/usr/bin/env python3
"""Post-deploy v0.6.8 production acceptance checks.

This intentionally separates source acceptance from live Cloudflare/GitHub Pages behavior.
"""
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
import argparse, json, sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = 'https://bezpecnaelektrika.sk/'
PAGES = ['', 'revizie/', 'o-projekte/', 'podcast/', 'podcast/be-005-test-prudoveho-chranica/', 'hladat/']
UA = 'BezpecnaElektrika-v068-production-validator/2.0'

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

NO_REDIRECT = build_opener(NoRedirect)

def request(url, headers=None):
    return Request(url, headers={'User-Agent': UA, **(headers or {})})

def fetch(url, headers=None):
    return urlopen(request(url, headers), timeout=20)

def redirect_probe(url):
    try:
        with NO_REDIRECT.open(request(url), timeout=20) as r:
            return r.status, r.headers.get('Location')
    except HTTPError as e:
        return e.code, e.headers.get('Location')

def unavailable_or_not_200(url):
    try:
        with fetch(url) as r:
            return r.status != 200, r.status
    except HTTPError as e:
        return True, e.code
    except Exception:
        return True, None

def main():
    local = json.loads((ROOT / 'version.json').read_text(encoding='utf-8'))
    pods = json.loads((ROOT / 'data/podcasts.json').read_text(encoding='utf-8'))
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default=DEFAULT_BASE)
    ap.add_argument('--expect-release', default=local['release'])
    args = ap.parse_args()
    base = args.base.rstrip('/') + '/'
    errors, warnings = [], []

    # Transport/canonical redirect matrix. Canonicalization must be permanent for production.
    if base == DEFAULT_BASE:
        redirect_matrix = [
            'http://bezpecnaelektrika.sk/',
            'http://www.bezpecnaelektrika.sk/',
            'https://www.bezpecnaelektrika.sk/',
            'http://bezpecna-elektrika.sk/',
            'https://bezpecna-elektrika.sk/',
        ]
        for probe in redirect_matrix:
            status, loc = redirect_probe(probe)
            if status not in (301, 308) or not (loc or '').startswith('https://bezpecnaelektrika.sk/'):
                errors.append(f'Permanent canonical redirect mismatch: {probe} -> {status} {loc!r}')
        missing_url = urljoin(base, '__be-nonexistent-v068-404-probe__/')
        try:
            with NO_REDIRECT.open(request(missing_url), timeout=20) as r:
                errors.append(f'Nonexistent URL returned {r.status}, expected real HTTP 404: {missing_url}')
        except HTTPError as e:
            if e.code != 404: errors.append(f'Nonexistent URL returned {e.code}, expected 404: {missing_url}')
        except Exception as e:
            errors.append(f'404 probe failed: {e}')

    home_headers = None
    for rel in PAGES:
        url = urljoin(base, rel)
        try:
            with fetch(url) as r:
                body = r.read().decode('utf-8', 'replace')
                if r.status != 200:
                    errors.append(f'{url} HTTP {r.status}')
                if rel == '':
                    home_headers = r.headers
                if rel == 'hladat/' and 'noindex,follow' not in body:
                    errors.append('/hladat/ lost noindex,follow')
                if rel != 'hladat/' and rel and 'rel="canonical"' not in body:
                    warnings.append(f'Canonical not detected: {url}')
                if rel != 'hladat/' and f'data-release-version="{args.expect_release}"' not in body:
                    errors.append(f'Visible release marker mismatch: {url}')
                if any(x in body for x in ['DRY RUN – NEPUBLIKOVAŤ', 'commercial-dry-run-sticky', 'commercial-schema-candidate']):
                    errors.append(f'Dry-run marker leaked to production: {url}')
        except Exception as e:
            errors.append(f'{url}: {e}')

    # Baseline live security headers. CSP/HSTS are reported separately because rollout may be staged.
    if home_headers is not None:
        if (home_headers.get('X-Content-Type-Options') or '').lower() != 'nosniff':
            errors.append('X-Content-Type-Options: nosniff missing on homepage')
        if not home_headers.get('Referrer-Policy'):
            errors.append('Referrer-Policy missing on homepage')
        if not home_headers.get('Permissions-Policy'):
            errors.append('Permissions-Policy missing on homepage')
        csp = home_headers.get('Content-Security-Policy') or ''
        csp_ro = home_headers.get('Content-Security-Policy-Report-Only') or ''
        if not (csp_ro or csp):
            warnings.append('CSP / CSP Report-Only not detected')
        framing_signal = 'frame-ancestors' in (csp + ';' + csp_ro).lower() or bool(home_headers.get('X-Frame-Options'))
        if not framing_signal:
            warnings.append('Anti-framing signal not detected (CSP frame-ancestors or X-Frame-Options)')
        if not home_headers.get('Strict-Transport-Security'):
            warnings.append('HSTS not detected; enable only after the HTTPS/subdomain decision is confirmed')

    # Robots/sitemap/feed/version.
    for rel in ['robots.txt', 'sitemap.xml', 'podcast/feed.xml', 'version.json']:
        url = urljoin(base, rel)
        try:
            with fetch(url) as r:
                body = r.read().decode('utf-8', 'replace')
                if rel == 'version.json' and f'"release": "{args.expect_release}"' not in body:
                    errors.append(f'Production version.json is not {args.expect_release}')
                if rel == 'sitemap.xml' and '/hladat/' in body:
                    errors.append('/hladat/ leaked into sitemap')
                if rel == 'robots.txt':
                    for block in ['User-agent: OAI-SearchBot\nAllow: /', 'User-agent: ChatGPT-User\nAllow: /', 'User-agent: GPTBot\nDisallow: /']:
                        if block not in body:
                            errors.append('robots.txt crawler directive missing: ' + block.replace('\n', ' / '))
        except Exception as e:
            errors.append(f'{url}: {e}')

    # Repository-only and dry-run artifacts must not be publicly retrievable.
    for rel in ['config/release.json', 'config/commercial-state.json', 'tools/validate-v068.py', 'docs/COMMERCIAL-SWITCH-v0.7.0.md', '.build/commercial-dry-run/dry-run-manifest.json', 'README.md', 'COMMERCIAL-GO-LIVE.md', 'RELEASE-v0.6.8.md']:
        url = urljoin(base, rel)
        hidden, status = unavailable_or_not_200(url)
        if not hidden:
            errors.append(f'Repository-only artifact is publicly available: {url}')
        elif status not in (None, 403, 404, 410):
            warnings.append(f'Repository-only path returned unusual non-200 status {status}: {url}')

    # Cache/compression observations by asset class.
    probes = [
        ('html', base),
        ('css', urljoin(base, 'assets/css/style.css')),
        ('js', urljoin(base, 'assets/js/main.js')),
        ('search-json', urljoin(base, 'data/search-index.json')),
        ('version-json', urljoin(base, 'version.json')),
        ('versioned-image', urljoin(base, 'assets/img/osvedcenie-e2a-lukas-likavcan-verejna-kopia-preview.webp')),
    ]
    for label, url in probes:
        try:
            with fetch(url, {'Accept-Encoding': 'br, gzip'}) as r:
                r.read(8)
                cc = r.headers.get('Cache-Control') or ''
                ce = r.headers.get('Content-Encoding') or ''
                if not cc:
                    warnings.append(f'{label}: Cache-Control missing')
                if label in ('html', 'css', 'js', 'search-json') and 'immutable' in cc.lower():
                    errors.append(f'{label}: immutable cache is unsafe for unhashed/changeable asset')
                if label in ('css', 'js', 'search-json') and not ce:
                    warnings.append(f'{label}: compression Content-Encoding not detected')
        except Exception as e:
            warnings.append(f'{label} cache/compression probe failed: {e}')

    # All published podcast audio must support seeking through HTTP byte ranges.
    for ep in [x for x in pods['episodes'] if x.get('published')]:
        url = ep['audio']
        try:
            with fetch(url, {'Range': 'bytes=0-1'}) as r:
                ctype = (r.headers.get('Content-Type') or '').split(';', 1)[0].lower()
                if r.status != 206:
                    errors.append(f'{ep["id"]} Range -> {r.status}, expected 206')
                if ctype != 'audio/mpeg':
                    errors.append(f'{ep["id"]} Content-Type -> {ctype or "missing"}')
                if not r.headers.get('Content-Range'):
                    errors.append(f'{ep["id"]} Content-Range missing')
                if 'bytes' not in (r.headers.get('Accept-Ranges') or '').lower():
                    warnings.append(f'{ep["id"]} Accept-Ranges: bytes not advertised')
        except Exception as e:
            errors.append(f'{ep["id"]} audio range check failed: {e}')

    print('PRODUCTION v0.6.8 ACCEPTANCE')
    for w in warnings:
        print(' WARN', w)
    if errors:
        for e in errors:
            print(' FAIL', e)
        print(' SOURCE PASS does not imply PRODUCTION PASS.')
        return 1
    print(' OK automated production acceptance passed')
    print(' NOTE Cloudflare/WAF access for real Google/OpenAI crawlers, CSP violation review, Windows/Android, 200/400% zoom and field CWV remain manual/field observations.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
