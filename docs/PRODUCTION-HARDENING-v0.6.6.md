# Production hardening v0.6.6

Tento checklist oddeľuje kontroly zdrojového balíka od vlastností reálnej produkcie. ZIP nemôže sám potvrdiť Cloudflare, CDN, WAF, HTTP headers, CrUX ani stav indexácie.

## SOURCE PASS
- `python tools/build-css.py --check`
- `python tools/test-search-index.py`
- `python tools/validate-release.py`
- `python tools/validate-v060.py`
- `python tools/validate-v062.py`
- `python tools/validate-v063.py`
- `python tools/validate-v064.py`
- `python tools/validate-v065.py`
- `python tools/validate-v066.py`

## PRODUCTION PASS po deployi
- `python tools/validate-production-v066.py`
- Windows + Android smoke.
- Viewer osvedčenia: preview → fit → 100 % → fit → close → reopen; 200 % a 400 % zoom/reflow.
- Consent: banner, Povoliť, Len nevyhnutné, Nastavenia, Esc, close, focus return, grant → deny → grant.
- Podcasty BE-001–004: prehratie a seek.
- Cloudflare Security Events: povolené legitímne crawlers; robots a WAF sa navzájom nepopierajú.
- CSP: začať Report-Only; enforce až po vyhodnotení legitímnych violations.
- HSTS: rozhodnúť až po kontrole všetkých relevantných subdomén.
- Lighthouse/PSI lab + Search Console/CrUX field, ak sú dáta.
