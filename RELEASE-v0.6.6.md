# v0.6.6 – Production hardening & accessibility

Dátum: 11. 9. 2026

## Source changes

- Plná verejná kópia osvedčenia sa nenačítava pri obyčajnej návšteve `/o-projekte/`; `src` sa nastaví až pri prvom otvorení vieweru. No-JS odkaz na plný WebP zostáva zachovaný.
- Viewer osvedčenia explicitne používa `display:grid` iba pri `[open]` a zatvorený `<dialog>` má obranné `display:none`; tlačidlo × aj natívny `Esc` tak skutočne odstránia viewer z layoutu.
- Viewer osvedčenia používa reflow-safe grid (`auto / minmax(0,1fr) / auto`) namiesto pevného odpočtu výšky, má minimálne 44 px ovládacie prvky, explicitný stav zoomu a návrat focusu na opener.
- Consent nastavenia si pamätajú opener a po zavretí deterministicky vracajú focus. Mobilný banner je kompaktnejší bez zmeny consent-first logiky alebo rovnocennosti volieb.
- v0.6.5 validator je forward-compatible, aby celý guardrail chain ostal použiteľný v ďalších releaseoch.
- Pridaný `validate-v066.py` a samostatný `validate-production-v066.py` pre kontroly, ktoré sa nedajú pravdivo potvrdiť iba zo ZIPu.

## Production acceptance after deploy

- Live canonical/redirect/sitemap/RSS/search/podcast/certificate smoke.
- MP3: `audio/mpeg`, `Content-Length`, byte-range request a `206 Partial Content`, seekovanie v prehrávači.
- Cloudflare crawler/WAF cesta pre Googlebot, OAI-SearchBot a ChatGPT-User; crawler policy zostáva OAI Search + ChatGPT User allow, GPTBot disallow.
- Security headers audit; CSP najprv Report-Only. HSTS `includeSubDomains`/`preload` iba po samostatnom overení všetkých relevantných subdomén.
- Cache/compression audit podľa triedy assetu; nehashované CSS/JS nedostanú bezhlavo dlhý `immutable`.
- Lighthouse/PSI ako lab baseline; Search Console/CrUX ako field baseline iba ak sú dostupné dáta.
- Praktický WCAG 2.2 AA pass: keyboard, focus, 200/400 % zoom/reflow, large text, reduced motion, dialogs, mobile navigation, audio a transcript.

## Scope guardrails

- Žiadny nový odborný obsah ani redesign.
- Bez Commercial Switchu: žiadny telefón, ceny, `LocalBusiness`, `Electrician`, `Service`, `Offer` ani `areaServed`.
- `/hladat/` zostáva `noindex,follow` a mimo sitemapu.
- `dateModified` a sitemap `lastmod` sa nemenia kvôli technickému hardeningu.
