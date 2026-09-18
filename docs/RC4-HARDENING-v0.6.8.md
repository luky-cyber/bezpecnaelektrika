# v0.6.8 RC4 hardening acceptance

RC4 nemení commercial state. `precommercial`, `goLiveAllowed=false` a `publicCommercialServices=false` sú release invariant.

## Source acceptance

- celý historický validator chain + `validate-v068.py`;
- Search index rebuild bez raw podcast transcript snippets;
- podcast/RSS/schema/search/sitemap integrita;
- commercial dry-run ostáva izolovaný mimo release ZIP;
- žiadny `LocalBusiness`, `Electrician`, `Service`, `Offer`, `areaServed`, `tel:` ani vymyslený commercial detail;
- `.build/`, `__pycache__/` a `*.pyc` nesmú byť v release ZIP;
- footer/version musia byť presne `v0.6.8-rc4`.

## Manual RC4 acceptance

- Windows: keyboard navigation, otvorenie mobil/responsive menu, focus return, Esc, Search, consent, credential viewer, podcast, 200 % a 400 % zoom;
- Android: touch, menu, consent, search, QR, podcast; TalkBack smoke na homepage/search/consent/podcast;
- overiť, že consent banner nezakrýva aktuálny keyboard focus;
- BE-001/002/003: safety notice musí byť viditeľný pred Play a BE-002 correction musí byť čitateľná;
- RCD active-fault stránka musí mať escalation boundary pred diagnostickými krokmi;
- homepage/revízie musia komunikovať precommercial stav pred mailovým CTA.

## GitHub/production manual setup

- vyžadovať GitHub Actions status check `validate` pre `main` a podľa možnosti zakázať direct push/force-push; toto je account/repository setting a ZIP ho nemôže zapnúť sám;
- po final deployi spustiť `validate-production-v068.py`;
- Cloudflare: security headers, CSP Report-Only, HSTS decision, cache/compression, WAF/crawlers;
- DNS/account: MFA/passkey, least-privilege tokeny, DNSSEC a SPF/DKIM/DMARC overiť mimo source ZIP.

## Legal decision intentionally unresolved

Aplikácia § 4 zákona č. 22/2004 Z. z. na konkrétny predkomerčný model zostáva právnym/business rozhodnutím pred final/commercial GO. RC4 preto naslepo nepridáva domácu adresu, telefón ani podnikateľské schema.
