# Release checklist

1. Spustiť `python tools/build-search-index.py`.
2. Spustiť `python tools/test-search-index.py` a overiť `SEARCH SMOKE TEST OK`.
3. Spustiť `python tools/build-news-sitemap.py`. Ak nie je čerstvý `NewsArticle`, očakávaný výsledok je `0 eligible articles` a žiadny `news-sitemap.xml`.
4. Spustiť `python tools/validate-release.py` a `python tools/validate-v060.py`.
5. Overiť, že `index.html` a `CNAME` sú priamo v koreňovom adresári.
6. Cez Live Server otestovať homepage, Revízie, RCD, Zs, LPS, Meranie a Metodiku – TOC, anchor odkazy a „Kopírovať odkaz“.
7. Otestovať vyhľadávanie s diakritikou aj bez nej: `RCD`, `prudovy chranic`, `Zs`, `TN-C-S`, `PEN`, `LPS`, `kupa domu`, `revizna sprava`, `cena`, `telefon`, `hlinik`.
8. Otestovať Search overlay: lupa, `/`, Ctrl/Cmd+K, Escape, šípky, Enter a návrat fokusu.
9. Otestovať `/hladat/?q=tn-c`, `/obsah/` a 404 s neexistujúcou URL.
10. Overiť, že `/hladat/` má `noindex,follow` a nie je v sitemap; `/obsah/` v sitemap je.
11. Overiť consent a privacy-safe udalosti Searchu; text dopytu sa do GA4 neposiela.
12. V produkcii otestovať BE-001, BE-002 aj BE-003 a prepnutie epizódy: po prepnutí musí byť tlačidlo Play, nie Pause.
13. Overiť `/robots.txt`: OAI-SearchBot = Allow, GPTBot = Disallow.
14. V Cloudflare skontrolovať, že OAI-SearchBot nedostáva blokáciu/WAF challenge.
15. Po pushi overiť GitHub Pages pred vytvorením tagu/releasu.
16. Novinky: skontrolovať viditeľný byline s `Publikované` a podmieneným `Aktualizované`; `Stav informácií overený k` patrí do provenance bloku, nie medzi publication metadata. Dátum udalosti nesmie byť zamenený za dátum článku. Lead image musí byť inline, relevantný, 16:9/≥1200 px a zhodný s preferovaným article/OG image; `max-image-preview:large` musí byť povolené.
17. Novinky: H1 = Article/NewsArticle headline = OG/Twitter title = text odkazu z `/novinky/`; `<title>` môže mať suffix `| Bezpečná elektrika`.
18. Novinky: existujúce odborné analýzy zostávajú `Article`; `NewsArticle` použiť iba pri skutočne čerstvej časovo citlivej udalosti s reálnym timezone-aware timestampom.
19. Ak existuje `news-sitemap.xml`, musí obsahovať iba články z posledných dvoch dní a `robots.txt` ho musí uvádzať; ak súbor neexistuje, `robots.txt` ho nesmie inzerovať.
## v0.5.13
- [ ] `python tools/build-css.py --check` prejde a `style.css` sa needituje ručne.
- [ ] Poradňa obsahuje 12 detailov a `hlinik` smeruje na novú praktickú odpoveď.
- [ ] PE/PEN provenance je založená iba na overených zdrojoch; odborné tvrdenia prešli manuálnym review.
- [ ] RCD mini-mapa jasne hovorí, že RCCB/RCBO sú iba vybrané typy, nie úplná taxonómia RCD.
- [ ] Glosár/Poradňa eyebrow funguje myšou aj klávesnicou.
- [ ] Homepage H1 je vizuálne overený pri 100 %, 125 % a 150 % zoom; zmena je izolovaná cez `.page-hero--home`.
- [ ] Homepage share preview používa nový `og-home-photo-v2.jpg`; po deployi preveriť cache sociálnej platformy.



## v0.6.0
- [ ] Service-first homepage má 6 hlavných sekcií, priamo pomenúva revízie a nevracia technické skratky do hlavnej zákazníckej cesty.
- [ ] Homepage a `/revizie/` majú rozdielne `<title>` a `/revizie/` používa jednotný anchor `#cena`.
- [ ] Predkomerčný status je pravdivý: žiadne objednávanie, telefón, lokalita, reálny cenník ani LocalBusiness/Electrician/Service/Offer schema.
- [ ] MI 3102 BT nie je v Glosári prezentovaný ako už prakticky použitý na reálnych meraniach.
- [ ] Light-theme `--subtle` spĺňa minimálne 4.5:1 voči svetlému pozadiu pre malý text.
- [ ] Malé profilové karty nepoužívajú veľký PNG asset; všetky lokálne `<img>` majú intrinsic `width` a `height`.
- [ ] FAQ JSON-LD na `/revizie/` zodpovedá viditeľnému FAQ.
- [ ] Article/Podcast publisher používa Person alebo je vynechaný; `Project` sa nepoužíva ako publisher.
- [ ] Otestovať reálny mobil: hero/fold, Cena, Poradňa, Kontakt, Odborný obsah, light theme a focus/Escape.


## v0.6.2
- [ ] `python tools/build-css.py --check`, `python tools/test-search-index.py`, `python tools/validate-release.py`, `python tools/validate-v060.py` a `python tools/validate-v062.py` prejdú bez chyby.
- [ ] Homepage hero pri 390, 768, 1600, 1920, 2560 a 3840 px zobrazuje celý zdrojový obrázok bez cropu; viditeľná je hlava aj merací prístroj.
- [ ] `/revizie/` má vyváženejší brand mark bez zväčšenia celého hero bloku.
- [ ] Search overlay aj `/hladat/`: po zadaní dotazu Enter otvorí prvý výsledok; `/` a Ctrl/Cmd+K zostávajú skratky na otvorenie mimo textového poľa a Esc zatvára overlay.
- [ ] Poradňa `co-pripravit-pred-reviziou` používa pôvodnú canonical URL, má aktualizovaný obsah a `dateModified`/sitemap `lastmod` 2026-08-28.
- [ ] Nová poradenská úprava nepridáva aktívnu službu, cenu, lokalitu, telefón ani LocalBusiness/Electrician/Service/Offer schema.
- [ ] `/novinky/` nemá horizontálny overflow pri 320 px; `.news-card` sa môže zmenšiť a `.news-meta` sa môže zalomiť.
- [ ] Term popover v Poradni nevytvára horizontálny overflow pri 768, 1024 ani 1100 px.
- [ ] Light-theme `--c-subtle` a `--c-accent` spĺňajú aspoň 4,5:1 voči `--c-bg`, `--c-surface`, `--c-surface-2` a `--c-surface-3` pre malý text.
