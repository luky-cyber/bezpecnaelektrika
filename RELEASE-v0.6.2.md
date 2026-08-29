# v0.6.2 – UX + discovery polish

Dátum: 29. 08. 2026

## Zmeny
- Homepage hero zobrazuje celý portrét bez orezania na desktope, tablete aj mobile.
- `/revizie/` má väčší a proporčne vyváženejší brand mark v hero bloku.
- Vyhľadávanie podporuje Enter na otvorenie prvého výsledku v overlayi aj na `/hladat/`; pomocný text klávesových skratiek je spresnený.
- Existujúca Poradňa `/poradna/co-pripravit-pred-reviziou/` bola rozšírená ako prvý information-intent/discovery pilot. Pôvodná canonical URL zostáva zachovaná, aby nevznikala duplicitná konkurujúca stránka.
- Poradňa dopĺňa praktickú prípravu dokumentácie, informácií o zmenách, prístupu, možného prerušenia napájania a postup pri chýbajúcich podkladoch.
- Doplnený je overený odborný základ: IEC 60364-6:2016 a slovenská vyhláška 508/2009 Z. z. s opatrnou interpretáciou rozsahu.
- Search index má nové intent aliasy pre prípravu pred revíziou; sitemap `lastmod` sa mení iba pri obsahovo upravenej Poradni.
- Predkomerčný status zostáva nezmenený. GA4/Search Console konfigurácia sa v súboroch nemení.
- Predpublikačný audit dopĺňa tri malé hardening opravy: Novinky sa pri 320 px bezpečne zmršťujú a metadata sa zalomia, term popovery v Poradni používajú viewport anchoring až do 1100 px a light-theme sekundárny/akcentový text má WCAG AA kontrast minimálne 4,5:1 na používaných svetlých povrchoch.

## Release guardrails
- Bez Commercial Switch prvkov: žiadne aktívne objednávanie, cenník, telefón, areaServed ani LocalBusiness/Electrician/Service/Offer schema.
- `validate-v060.py` zostáva baseline guardrail; v0.6.2 pridáva `validate-v062.py`.
