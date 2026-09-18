#!/usr/bin/env python3
"""Post-deploy v0.6.6 production smoke.

Network/Cloudflare/CDN checks cannot be proven by the ZIP. Run after deployment.
Exit 1 = functional production failure. Security/cache recommendations are WARN until
Cloudflare policy is intentionally configured and reviewed.
"""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import urljoin
import argparse,re,sys

DEFAULT_BASE='https://bezpecnaelektrika.sk/'
PAGES=['','revizie/','o-projekte/','podcast/','hladat/']
MP3=[
'https://audio.bezpecnaelektrika.sk/podcast/2026/be-001-preco-nestaci-ze-elektrina-funguje.mp3',
'https://audio.bezpecnaelektrika.sk/podcast/2026/be-002-merat-nie-hadat.mp3',
'https://audio.bezpecnaelektrika.sk/podcast/2026/be-003-namerana-hodnota-este-nie-je-vysledok.mp3',
'https://audio.bezpecnaelektrika.sk/podcast/2026/be-004-revizna-sprava-nie-je-len-papier.mp3',
]

def fetch(url,method='GET',headers=None):
    req=Request(url,method=method,headers={'User-Agent':'BezpecnaElektrika-v066-production-validator/1.0',**(headers or {})})
    return urlopen(req,timeout=20)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--base',default=DEFAULT_BASE)
    ap.add_argument('--expect-version',default='0.6.6')
    args=ap.parse_args()
    base=args.base.rstrip('/')+'/'
    errors=[]; warnings=[]

    # Main pages and canonical/noindex behavior.
    for rel in PAGES:
        url=urljoin(base,rel)
        try:
            with fetch(url) as r:
                body=r.read().decode('utf-8','replace')
                if r.status!=200: errors.append(f'{url} HTTP {r.status}')
                if rel=='hladat/':
                    if 'noindex,follow' not in body: errors.append('/hladat/ lost noindex,follow')
                elif '<link' in body and 'rel="canonical"' not in body: warnings.append(f'Canonical not detected in {url}')
                if rel=='':
                    for h in ['x-content-type-options','referrer-policy','permissions-policy','strict-transport-security','content-security-policy','content-security-policy-report-only']:
                        if not r.headers.get(h): warnings.append(f'Header not present on homepage: {h}')
        except Exception as e: errors.append(f'{url}: {e}')

    # Public machine-readable files.
    for rel in ['robots.txt','sitemap.xml','podcast/feed.xml','version.json']:
        url=urljoin(base,rel)
        try:
            with fetch(url) as r:
                body=r.read().decode('utf-8','replace')
                if r.status!=200: errors.append(f'{url} HTTP {r.status}')
                if rel=='version.json' and f'"version": "{args.expect_version}"' not in body:
                    errors.append(f'Production version.json is not {args.expect_version}')
                if rel=='sitemap.xml' and '/hladat/' in body: errors.append('/hladat/ leaked into production sitemap')
        except Exception as e: errors.append(f'{url}: {e}')

    # Crawler policy source. WAF acceptance still needs Cloudflare Security Events review.
    try:
        with fetch(urljoin(base,'robots.txt')) as r: robots=r.read().decode('utf-8','replace')
        for block in ['User-agent: OAI-SearchBot\nAllow: /','User-agent: ChatGPT-User\nAllow: /','User-agent: GPTBot\nDisallow: /']:
            if block not in robots: errors.append('robots.txt crawler policy mismatch: '+block.replace('\n',' / '))
    except Exception: pass

    # MP3 CDN: headers + byte range. urllib raises HTTPError for non-2xx, but 206 is normal success.
    for url in MP3:
        try:
            with fetch(url,headers={'Range':'bytes=0-1'}) as r:
                ctype=(r.headers.get('Content-Type') or '').split(';',1)[0].lower()
                if r.status!=206: errors.append(f'MP3 range request did not return 206: {url} -> {r.status}')
                if ctype!='audio/mpeg': errors.append(f'MP3 Content-Type mismatch: {url} -> {ctype or "missing"}')
                if not r.headers.get('Content-Range'): errors.append(f'MP3 Content-Range missing: {url}')
                if not r.headers.get('Content-Length'): warnings.append(f'MP3 Content-Length missing: {url}')
                if 'bytes' not in (r.headers.get('Accept-Ranges') or '').lower(): warnings.append(f'MP3 Accept-Ranges: bytes not advertised: {url}')
        except Exception as e: errors.append(f'MP3 range check failed {url}: {e}')

    print('PRODUCTION v0.6.6 AUDIT')
    for w in warnings: print(' WARN',w)
    if errors:
        for e in errors: print(' FAIL',e)
        return 1
    print(' OK functional production smoke passed')
    print(' NOTE review Cloudflare Security Events/WAF, CSP Report-Only reports, cache policy and field CWV manually.')
    return 0

if __name__=='__main__': sys.exit(main())
