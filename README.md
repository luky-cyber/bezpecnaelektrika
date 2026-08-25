# Bezpečná elektrika v0.5.12

Release-candidate static website for GitHub Pages / `bezpecnaelektrika.sk`.

## What is included
- Responsive desktop, iPhone/iPad and Android layout
- Sticky mobile-friendly navigation
- Reduced-motion support and keyboard focus states
- Apple/Android icons; web nie je zámerne prezentovaný ako inštalovateľná PWA
- Custom Open Graph image
- SEO canonical/meta and entity-oriented JSON-LD
- Canonical link to Lukáš Likavčan, PhD. identity on `likavcan.cz`
- Project status transparency: E2A exam passed; certificate pending; business not yet launched
- Practical content: warning signs, revision intervals, LPS overview, employer section, insurance context, myths, FAQ
- Official-source links and visible update date
- Future-ready `/poradna/`, `/podcast/`, `/o-projekte/`
- Social-content placeholders without inventing fake posts
- Podcast placeholders without inventing listening statistics

## Before publishing
1. Preview locally with Live Server.
2. Confirm that `/assets/...` absolute paths work in your local setup or preview using a local web server rooted at this folder.
3. Upload the *contents* of this folder to the repository root, not the enclosing folder.
4. Keep `CNAME` in the repository root.
5. After deploy, test desktop + mobile and check GitHub Pages HTTPS.

## Important content note
Technical/legal text is an informational overview and includes links to official public sources. It is not a substitute for current standards, project documentation or professional assessment of a specific installation.


## Novinky v0.3.1
- sekcia **AI ako druhý pár očí**
- princípy: *merať, nie hádať · dokumentovať, nie spoliehať sa na pamäť · vysvetľovať, nie strašiť*
- príklady moderného AI + človek workflowu a budúcich success stories
- mini glosár + `/glosar/`
- samostatná stránka `/metodika/`
- mini changelog projektu
- vCard kontakt a QR kód
- pripravená infraštruktúra pre ďalší obsah bez preťaženia homepage


## v0.4.x
Vetva 0.4.x prináša nový vizuálny systém a informačnú architektúru. v0.4.0 je prvý živý prototyp nového dizajnu.


## v0.4.1
Prvá publikovaná podcastová epizóda BE-001 je načítaná z Cloudflare R2; pridaný je redakčný/AI disclaimer a prvý polish nového dizajnu.


## v0.4.3
Obsahová integračná a UX iterácia: RCCB/RCBO v Glosári, priame anchor odkazy, súvisiace pojmy/články, prepojenie Poradne a Merania s Glosárom, podcast selected state a accessibility/focus polish.


## v0.4.4
Final cleanup vetvy 0.4.x: menej vývojových placeholderov, zjednotená identita, odstránené duplicitné dátové súbory a jemný UX polish pred externou kontrolou.

## v0.4.5
Posledný obsahový/UX polish vetvy 0.4.x: jasnejšie používateľské cesty, prepojenejší Glosár a interná šablóna pre budúce anonymizované prípadové štúdie.

## v0.5.0
Produkčná vrstva: jednotné metadata a structured data, technická typografia, privacy bez zbytočného cookie banneru, rozšírené odborné Novinky a technický cleanup.

## v0.5.1
Jemná konverzná vrstva, voliteľná GA4 analytika s consentom a aktualizovaná ochrana súkromia.


## v0.5.2
Podcast BE-002 „Merať, nie hádať“, rozšírené Meranie v praxi a prepojenie prehliadky, skúšania, merania a odborného vyhodnotenia.

## v0.5.3
AI/Search a budúca servisná vrstva: podcast RSS, robots/llms doplnky, entity-oriented JSON-LD, sociálna identita, rozšírená stránka Revízie, UTM/analytics infraštruktúra, release validator a oprava stavu podcast playera pri zmene epizódy.

## v0.5.4
Quality & consistency release: zjednotený footer, stabilné Facebook/Instagram identity, social tracking, verejný metodický version cleanup a rozšírené predrelease kontroly.


## v0.5.5
Poradňa & Answer Engine: 8 samostatných odpovedí na konkrétne otázky, konzistentný „Stručne“ formát, hranice tvrdení, interné prelinkovanie, `dateModified`, `knowsAbout` cleanup a jednotný status projektu.


## v0.5.6
Knowledge Base Foundation: 8 samostatných odborných stránok pre RCD, RCCB/RCBO, Zs, PE/PEN, TN systémy, izolačný odpor, uzemnenie a LPS; hub-and-spoke prelinkovanie, zdroje/proveniencia, dátumy a konzistentná hranica medzi definíciou, meraním a odborným záverom.


## v0.5.7
Podcast BE-003 „Nameraná hodnota ešte nie je výsledok“: publikovanie tretej epizódy z Cloudflare R2, aktualizácia RSS, PodcastEpisode JSON-LD a homepage latest-content karty.


## v0.5.8
AI/Search + Identity + UX/Performance polish: OAI-SearchBot allow / GPTBot disallow, prepojenie autora s likavcan.cz v kontakte, mäkké CTA na hlbších stránkach, interné prelinkovanie, homepage/status deduplikácia, opravy Poradne a Metodiky, `dateModified` cleanup a odstránenie produkčných CSS `@import`.


## v0.5.9 – Odborná autorita a vlastné vizuály I

Prehĺbené RCD a Zs, prvé vlastné technické SVG diagramy, dve nové odpovede Poradne, viditeľné autorstvo a prvá časť vlastného OG vizuálneho systému. Podrobnosti: `RELEASE-v0.5.9.md`.

## v0.5.10 – Odborná autorita a vlastné vizuály II

Prehĺbené LPS, diagramy Zs ≠ Zline, RCCB vs RCBO a TN-C → TN-C-S, nová Poradňa o opakovanom vypínaní RCD, rozšírená proveniencia a ďalšie vlastné OG vizuály. Podrobnosti: `RELEASE-v0.5.10.md`. Finálny pre-deploy polish dorovnáva OG metadata, interné prelinkovanie, dátumy, header logo a stavovú kartu MI 3102 BT.


## v0.5.11 – Vyhľadávanie a orientácia v obsahu

Stabilné permalinky na sekcie, obsah „Na tejto stránke“, Mapa obsahu `/obsah/`, statický full-text Search bez externej závislosti, normalizácia slovenčiny a technických zápisov, Search na 404, ručne kurátorované „Pokračovať v téme“ a privacy-safe analytické udalosti bez odosielania raw query. Podrobnosti: `RELEASE-v0.5.11.md`.

## v0.5.12 – Novinky: autor, čas, dôveryhodnosť

Redakčná transparentnosť sekcie „Čo nové v elektro“: jednoznačné publication metadata, viditeľný autor, jednotné titulky, relevantné 16:9 lead/OG obrázky, metodika Noviniek, konzistentná Person identita a pripravený News sitemap workflow pre budúce skutočne čerstvé `NewsArticle`. Google News je možný distribučný kanál, nie publikačný cieľ. Podrobnosti: `RELEASE-v0.5.12.md`.
