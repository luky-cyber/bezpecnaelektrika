# Bezpečná elektrika v0.5.11 – Vyhľadávanie a orientácia v obsahu

Dátum: 25. 08. 2026

## Hlavný cieľ

v0.5.11 nepridáva ďalšiu odbornú vrstvu. Zlepšuje orientáciu v tom, čo už na webe existuje: používateľ môže nájsť konkrétny pojem, preskočiť na presnú sekciu, skopírovať jej odkaz a pokračovať do ručne vybraných súvisiacich tém.

## Stabilné odkazy na sekcie

- dlhšie odborné stránky a samostatné články dostali stabilné anchor ID;
- ID sú oddelené od redakčného znenia nadpisu a po publikovaní sa nemajú svojvoľne meniť;
- pri odborných nadpisoch je nenápadné tlačidlo na kopírovanie odkazu na konkrétnu sekciu;
- pri detailných článkoch možno skopírovať aj odkaz na celý článok.

## „Na tejto stránke“

Statický obsah stránky pribudol na dlhších URL:

- RCD / prúdový chránič;
- impedancia poruchovej slučky Zs;
- LPS / ochrana pred bleskom;
- Revízie;
- Meranie v praxi;
- Zdroje a metodika.

Na desktope je obsah priamo viditeľný, na mobile je kompaktne zbalený v `<details>`.

## Mapa obsahu

Nová indexovateľná stránka:

- `/obsah/` – **Mapa obsahu**.

Obsahuje čistú HTML navigáciu cez Revízie, Poradňu, Knowledge Base, Meranie, Podcast, Novinky, O projekte a Metodiku. Funguje aj bez JavaScriptu a je prelinkovaná z footeru.

## Full-text vyhľadávanie

Nová statická vyhľadávacia vrstva bez externého backendu a bez vyhľadávacej knižnice:

- `/data/search-index.json`;
- `tools/build-search-index.py`;
- `assets/js/search.js`;
- lupa v hlavičke;
- vyhľadávací overlay;
- `/hladat/?q=...` ako adresovateľný používateľský stav;
- maximálne 8 hlavných výsledkov.

Search prechádza názvy, H2 sekcie, krátke popisy, hlavný text a ručne kontrolované technické termíny.

## Slovenčina a technické zápisy

Vyhľadávanie normalizuje:

- malé/veľké písmená;
- diakritiku (`chranic` → `chránič`);
- pomlčky a medzery (`TN-C-S` ↔ `TN C S`);
- vybrané technické zápisy (`Z_s` ↔ `Zs`, `IΔn` ↔ `idn` / `i-delta-n`).

Ručne kurátorované polia `aliases` a `relatedTerms` sú oddelené: súvisiaci termín pomáha nájsť obsah, ale nevytvára falošnú terminologickú rovnosť. Niekoľko bezpečných navigačných výrazov (napr. `cena`, `cennik`, `objednat`) je zámerne vedených ako routing alias pre `/revizie/`; nejde o tvrdenie, že na webe existuje cenník alebo aktívne objednávanie.

## Výsledky na konkrétnu sekciu

Ak dopyt lepšie zodpovedá konkrétnemu nadpisu než celej stránke, výsledok môže smerovať priamo na `URL#sekcia`. Výsledky zároveň zobrazujú krátky kontextový snippet a pri priamej zhode zvýraznia hľadaný výraz.

## Search UX a prístupnosť

- `/` otvorí vyhľadávanie mimo textových polí;
- `Ctrl+K` / `Cmd+K` je doplnková skratka;
- `Escape` zatvára overlay;
- šípky umožňujú prechádzať výsledkami;
- Enter otvorí vybraný výsledok;
- fokus sa po zatvorení vracia na pôvodný ovládací prvok;
- výsledkový stav používa `aria-live`;
- modal má `role="dialog"` a `aria-modal="true"`.

## 404

Stránka 404 teraz používa rovnaké vyhľadávanie a ako počiatočný dopyt vie použiť poslednú časť neexistujúcej URL. Automaticky nepresmerúva na prvý výsledok – voľba zostáva na používateľovi.

## „Pokračovať v téme“

Existujúce ručne kurátorované bloky sú zjednotené pod navigačným názvom **Pokračovať v téme**. Nejde o odporúčania podľa sledovania používateľa ani algoritmické „ľudia tiež čítali“.

## Ochrana súkromia a analytika

Po analytickom súhlase možno zaznamenať iba technické udalosti:

- `search_used`;
- `search_no_results`;
- `search_result_click` s typom výsledku.

**Text používateľského vyhľadávacieho dopytu sa do Google Analytics neposiela.** `search_used` sa po debounce zaznamená ako jedno reálne použitie vyhľadávania, nie pri každom medzistave písania; `search_no_results` sa vyhodnocuje až po rovnakom debounce. Stránka Ochrana súkromia bola o túto informáciu doplnená.

## Indexácia

- `/obsah/` je indexovateľná a je v sitemap;
- `/hladat/` používa `noindex,follow` a nie je v sitemap;
- query varianty `/hladat/?q=...` nevytvárajú nové indexovateľné obsahové stránky.

## Quality control

Release tooling kontroluje:

- unikátnosť anchor ID;
- platnosť TOC odkazov;
- povinné stabilné kotvy na referenčných stránkach;
- kontrakt Search indexu;
- prepojenie Search URL so sitemap;
- ručne kurátorované related bloky;
- pravidlo `cena` → `/revizie/` bez fiktívneho cenníka;
- privacy-safe analytiku;
- automatický smoke test kľúčových dopytov vrátane RCD, Zs, TN-C-S, LPS, kúpy domu, revíznej správy, ceny a telefónu;
- regresné deep-link testy pre `TEST RCD` → `#tlacidlo-test`, `Zline` / `Zs ≠ Zline` → `#zs-nie-je-zline`, `IΔn` a `trieda LPS`;
- integritný test `hlinik`: Search nemá predstierať samostatný odborný obsah, ktorý zatiaľ neexistuje.

## Čo v0.5.11 zámerne nepridáva

- nové odborné články iba kvôli počtu URL;
- chatbot alebo AI sumarizovanie interného Searchu;
- používateľské účty, komentáre alebo hviezdičky;
- newsletter a popupy;
- personalizované/trackingové odporúčania;
- PWA;
- ďalšie `llms.txt`, schema alebo crawler experimenty.
