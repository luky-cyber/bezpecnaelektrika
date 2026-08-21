# Bezpečná elektrika v0.5.0

Produkčná vrstva po uzavretí dizajnovej vetvy 0.4.x.

## SEO a strojová čitateľnosť
- zjednotený head na verejných stránkach,
- Open Graph + social metadata,
- konzistentné canonical URL,
- JSON-LD pre WebSite, Project, Person, WebPage, Article, PodcastSeries, PodcastEpisode a BreadcrumbList,
- osoba používa kanonický identifikátor https://likavcan.cz/lukas/#lukas-likavcan,
- 404 dostala noindex.

## Technická typografia a Glosár
- RISO → R_ISO,
- Zs → Z_s,
- Zline → Z_line,
- explicitné vysvetlenie rozdielu Z_line ≠ Z_s,
- slugy a anchory zostali jednoduché (#riso, #zs, #zline).

## PWA a súkromie
- vypnutá inštalovateľnosť PWA odstránením aktívneho manifestu,
- pridaná stránka Ochrana súkromia,
- bez cookie bannera, pretože web zatiaľ nepoužíva analytické ani reklamné cookies,
- dokumentovaná iba lokálna preferencia témy a technická infraštruktúra.

## Čo nové v elektro
Existujúce tri články sú rozšírené:
- STN EN IEC 62305-3:2026 – oficiálne významné technické zmeny + praktický/revízny kontext,
- STN EN IEC 62305-4:2026 – nové prílohy E/F/G/H, SPD, PV, rozdelenie bleskového prúdu a presnejšie prechodné obdobie,
- RCCB vs. RCBO – rozdiel funkcií + významné zmeny IEC 61008-1:2024 / IEC 61009-1:2024.

## Technický cleanup
- main.js má jednu konzistentnú inicializáciu navigácie, témy, animácií a back-to-top,
- produkčná chybová správa podcastu už nespomína Acode,
- robots.txt zjednodušený,
- sitemap aktualizovaná,
- verejný build marker odstránený,
- odstránený nepoužívaný externý structured-data súbor.

## Zatiaľ bez externých služieb
Google Search Console, Bing Webmaster Tools a analytika sa pripájajú až po otestovaní a release tejto verzie.
