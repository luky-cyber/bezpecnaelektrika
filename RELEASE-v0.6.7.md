# v0.6.7 – Content graph & query gaps

Dátum: 11. 9. 2026

## Cieľ

Zvýšiť hodnotu existujúceho odborného obsahu bez návratu k encyklopedickému rastu webu: jednoznačnejšie hlavné destinácie pre konkrétne otázky, prirodzené interné prepojenia a lepšie search routing.

## Zmeny

- Desktopový QR kontakt na `/o-projekte/` je väčší pre praktické skenovanie z FullHD monitora; mobilná veľkosť zostáva zachovaná.
- Pridaný opakovateľný `tools/audit-content-graph.py` a generovaný report `docs/CONTENT-GRAPH-REPORT-v0.6.7.md`.
- Query-gap audit potvrdzuje existujúce kanonické destinácie pre Zs/Zline a TEST RCD; nevznikajú duplicitné nové URL pre už pokryté intenty.
- Nová Poradňa `Ako čítať revíznu správu?` rieši samostatný praktický intent oproti existujúcej odpovedi `Čo obsahuje revízna správa?`.
- Zs a RCD sú kontextovo prepojené s BE-003; revízna správa s BE-004; Meranie smeruje na konkrétne podcastové epizódy namiesto všeobecného podcast hubu tam, kde je intent jasný.
- RCD, Zs a LPS Article JSON-LD používajú vlastný relevantný `image`; generický obrázok sa plošne nepridáva.
- Search index rozlišuje generické `revízna správa` od intentu `ako čítať revíznu správu` a zachováva deep routing Zline/TEST RCD.
- Nový `validate-v067.py` stráži content graph, Article.image, search destinácie, QR desktop sizing a všetky predkomerčné guardraily.

## Query-gap rozhodnutia

- `Zs ≠ Zline` → existujúca `/glosar/impedancia-poruchovej-slucky-zs/#zs-nie-je-zline`; bez novej URL.
- `TEST RCD` → existujúca `/glosar/rcd-prudovy-chranic/#tlacidlo-test`; bez novej URL.
- `nameraná hodnota ≠ odborný záver` → `/meranie/` + BE-003; bez novej URL.
- `čo obsahuje revízna správa` → existujúca Poradňa; bez zmeny intentu.
- `ako čítať revíznu správu` → nový samostatný praktický intent a jedna nová indexovateľná URL.

## Scope guardrails

- Customer-first homepage a hlavná servisná cesta sa nerozširujú.
- Žiadny Commercial Switch: žiadny telefón, aktívny cenník, `LocalBusiness`, `Electrician`, `Service`, `Offer` ani `areaServed`.
- `/hladat/` zostáva `noindex,follow` a mimo sitemapu.
- `llms.txt` zostáva stručnou orientáciou; nemení sa na druhý sitemap.
