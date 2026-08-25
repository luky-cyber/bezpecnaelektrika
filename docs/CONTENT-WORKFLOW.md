# Content workflow

Recommended publication flow:
1. Current, trustworthy primary or official sources.
2. Gemini Notebook for source-grounded study, questions and audio preparation.
3. Additional web/deep research when freshness or cross-checking is needed.
4. Human rewrite into the Bezpečná elektrika tone: simple, clear, occasionally witty.
5. Technical review by Lukáš before publication.
6. Publish with visible source list and update date for technical/legal content.

`dateModified` je redakčný údaj, nie build alebo deploy timestamp. Ak je na stránke použitý, mení sa iba pri významnej zmene samotného obsahu, odborného záveru alebo používateľsky podstatnej informácie. Samotná zmena CSS/JS, obrázka bez zmeny významu, tooling, release balenie alebo technický deploy dátum nemenia. Toto pravidlo platí pre celý web, nielen pre Novinky.

Validator môže kontrolovať formát a vnútornú konzistenciu dátumov, ale nesmie automaticky prepisovať `dateModified` na dátum release.
XML sitemap `<lastmod>` je samostatný crawl signál. Môže sa zmeniť pri významnej zmene samotnej stránky, metadát alebo prezentácie aj vtedy, keď sa redakčný `dateModified` odborného textu nemení; tieto dve hodnoty sa nesmú automaticky zväzovať.

## Novinky

1. Článok vzniká až po reálnej, overiteľnej udalosti alebo zmene s praktickým odborným významom.
2. Primárny zdroj overiť pred publikovaním a odlíšiť fakt od interpretácie.
3. Dátum udalosti, vydania alebo účinnosti normy nie je dátumom publikovania článku.
4. `datePublished` znamená prvé reálne zverejnenie článku. Historický čas spätne nevymýšľať.
5. Viditeľný byline má primárne komunikovať autora a publikovanie; `Aktualizované` zobraziť iba pri významnej zmene a iba ak sa líši od publikovania.
6. Pre `dateModified` platí celowebové pravidlo vyššie; pri Novinke sa mení iba pri významnej redakčnej alebo odbornej zmene.
7. `Stav informácií overený k` evidovať oddelene od dátumu publikovania a dátumu udalosti a zobrazovať ho v odbornom/provenance bloku, nie v hlavnom byline.
8. `Article` používať pre odbornú analýzu alebo oneskorený komentár; `NewsArticle` iba pre skutočne čerstvú, časovo citlivú udalosť.
   Pri budúcom `NewsArticle` evidovať reálny publication timestamp s časovým pásmom `Europe/Bratislava`; offset nesmie byť natvrdo predpokladaný, pretože sa mení medzi zimným a letným časom. Existujúce historické články bez overeného času zostávajú date-only.
9. Canonical editorial headline držať konzistentne v H1, `Article.headline`/`NewsArticle.headline`, `og:title`, Twitter title a texte odkazu z `/novinky/`. HTML `<title>` môže mať suffix `| Bezpečná elektrika`.
10. Relevantný article image má byť viditeľný aj v článku; generické logo nepoužívať ako hlavný obrázok významnej Novinky.
11. Pri skutočnom `NewsArticle` spustiť News sitemap builder; v News sitemap zostávajú iba články z posledných dvoch dní.

Google News je možný distribučný kanál, nie publikačný cieľ. Nevyrábať obsah, fiktívne timestampy ani umelú čerstvosť kvôli algoritmu.

For audio:
- Separate professional sources from the audio-generation tool.
- Use the label: "Zvuk vytvorený pomocou Gemini Notebook."
- Do not publish copyrighted source material or stale technical guidance without checking rights and current validity.
