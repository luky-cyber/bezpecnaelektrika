# Production acceptance v0.6.8

Lokálny ZIP môže dosiahnuť **SOURCE PASS**. Až reálne nasadená doména môže dosiahnuť **PRODUCTION PASS**. Jeden stav nenahrádza druhý.

## SOURCE PASS

- `python tools/build-css.py --check`
- `python tools/test-search-index.py`
- `python tools/validate-podcasts.py`
- `python tools/validate-commercial-dry-run.py`
- commercial dry-run musí synchronizovať HTML + Search index + `llms.txt` + dry-run `version.json`;
- `python tools/validate-release.py`
- `python tools/validate-v060.py`
- `python tools/validate-v062.py`
- `python tools/validate-v063.py`
- `python tools/validate-v064.py`
- `python tools/validate-v065.py`
- `python tools/validate-v066.py`
- `python tools/validate-v067.py`
- `python tools/validate-v068.py`

## PRODUCTION PASS po deployi

Automatizovateľná časť:

- `python tools/validate-production-v068.py --expect-release <release>`; hodnotu `<release>` prevezmite z `config/release.json`;
- HTTP → HTTPS + www/legacy host → canonical cez permanentný 301/308 redirect;
- náhodná neexistujúca URL musí vrátiť skutočný HTTP 404;
- `/version.json` + viditeľný footer marker;
- robots/sitemap/RSS a `/hladat/` noindex;
- repository-only, root Markdown a `.build` artefakty nesmú byť verejne dostupné;
- security-header baseline + CSP/HSTS report + anti-framing signál (`frame-ancestors` alebo X-Frame-Options);
- cache/compression observations podľa triedy assetu vrátane CSS/JS/Search JSON;
- všetky publikované MP3: `audio/mpeg`, Range request, `206`, `Content-Range`.

Manuálna/field časť:

- Windows + Android smoke celého customer path;
- 200 % / 400 % zoom a reflow, keyboard/focus, credential viewer, consent;
- BE-005 prehratie, seek a transcript;
- Cloudflare Security Events/WAF: Googlebot, OAI-SearchBot a ChatGPT-User nesmú byť blokované legitímnym WAF pravidlom; GPTBot zostáva podľa robots policy zakázaný;
- CSP Report-Only violations vyhodnotiť pred prípadným enforce;
- HSTS `includeSubDomains`/preload iba po osobitnom rozhodnutí vrátane audio subdomény;
- Lighthouse/PageSpeed ako lab; Search Console/CrUX ako field dáta, ak sú dostupné.

## Stav pred deployom

- SOURCE ACCEPTANCE: musí byť PASS.
- PRODUCTION ACCEPTANCE: PENDING.

Po deployi sa release považuje za produkčne overený až vtedy, keď automatizovateľné kontroly prejdú a manuálne/field položky nemajú blocker.
