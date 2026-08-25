# Bezpečná elektrika v0.5.12 – Novinky: autor, čas, dôveryhodnosť

Pracovný release. Google News je vedľajší distribučný kanál, nie cieľ ani dôvod meniť publikačnú kadenciu.

## Scope
- viditeľný autor na článkoch v `/novinky/`;
- jednoznačné oddelenie dátumu publikovania, významnej aktualizácie, vecného overenia a dátumu udalosti;
- jednotný editorial headline naprieč H1, structured data, OG/Twitter a hubom;
- `Article` zostáva na existujúcich odborných analýzach; `NewsArticle` iba pre skutočne čerstvé udalosti;
- Google-compatible author markup (`name` bez titulov, honorifics oddelene);
- relevantné 16:9 lead/OG images pre hub a existujúce Novinky, pričom article image je viditeľný inline;
- metodika „Ako vznikajú Novinky“;
- pripravený generátor News sitemap bez vkladania starých článkov;
- `max-image-preview:large` pre Novinky;
- validátor redakčných metadát, headline guardrails, lead-image integrity, site-name/favicon signálov a News sitemap;
- celowebové pravidlo, že `dateModified` je redakčný údaj a nesmie sa hromadne prepisovať build/release dátumom.

## Nie je súčasťou
- nový článok iba kvôli Google News;
- Publisher Center submission;
- nové GA4 eventy;
- zmena Search rankingu;
- NewsMediaOrganization alebo predstieranie redakcie;
- RSS/Atom pre Novinky;
- automatický GitHub Action na dvojdňové News sitemap okno.
