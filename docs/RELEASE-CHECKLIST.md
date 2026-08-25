# Release checklist

1. Spustiť `python tools/build-search-index.py`.
2. Spustiť `python tools/test-search-index.py` a overiť `SEARCH SMOKE TEST OK`.
3. Spustiť `python tools/build-news-sitemap.py`. Ak nie je čerstvý `NewsArticle`, očakávaný výsledok je `0 eligible articles` a žiadny `news-sitemap.xml`.
4. Spustiť `python tools/validate-release.py`.
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
