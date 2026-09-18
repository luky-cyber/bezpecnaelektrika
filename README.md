# Bezpečná elektrika v0.6.8-rc15

Static website for GitHub Pages / `bezpecnaelektrika.sk`, current release candidate v0.6.8-rc15 „Credential viewer cold-start fit hardening“.

## What is included
- Responsive desktop, iPhone/iPad and Android layout
- Sticky mobile-friendly navigation
- Reduced-motion support and keyboard focus states
- Apple/Android icons; web nie je zámerne prezentovaný ako inštalovateľná PWA
- Custom Open Graph image
- SEO canonical/meta and entity-oriented JSON-LD
- Canonical link to Lukáš Likavčan, PhD. identity on `likavcan.cz`
- Project status transparency: E2A exam passed; certificate issued; commercial services not yet launched
- Public redacted first-page copy of the E2/A certificate on `/o-projekte/`, with a watermark and no embedded source metadata
- Practical content: warning signs, revision intervals, LPS overview, employer section, insurance context, myths, FAQ
- Official-source links and visible update date
- Service-first `/poradna/`, `/podcast/`, `/o-projekte/` with pre-commercial guardrails
- Five published podcast episodes with standalone reviewed transcripts and editorial technical corrections
- Social links and podcast metadata without inventing engagement/listening statistics

## Before publishing
1. Preview locally with Live Server.
2. Confirm that `/assets/...` absolute paths work in your local setup or preview using a local web server rooted at this folder.
3. Upload the *contents* of this folder to the repository root, not the enclosing folder.
4. Keep `CNAME` in the repository root.
5. After deploy, test desktop + mobile and check GitHub Pages HTTPS.

## Important content note
Technical/legal text is an informational overview and includes links to official public sources. It is not a substitute for current standards, project documentation or professional assessment of a specific installation.

## v0.6.8 – Commercial readiness & release identity
RC14 keeps production strictly pre-commercial and retains the RC10–RC13 design/navigation work plus all earlier safety, privacy and accessibility guardrails. It closes release-documentation drift, aligns remaining close controls with the 44 px touch-target standard and makes the homepage Contact destination a standalone semantic section. Commercial Switch remains fail-closed and production acceptance remains a separate post-deploy step. Details: `RELEASE-v0.6.8.md`.



## v0.6.6 – Production hardening & accessibility
Technický hardening bez nového odborného obsahu: odložené načítanie plnej kópie osvedčenia, odolnejší a prístupnejší viewer pri zoome/reflow, deterministický návrat focusu v consent nastaveniach, kompaktnejší consent na mobile a nový source/production validačný workflow. Produkčné body (headers, cache, crawler/WAF, MP3 Range, CWV) sa definitívne overujú až po deployi. Podrobnosti: `RELEASE-v0.6.6.md`.

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

## v0.5.13 – Odborné súvislosti a praktické otázky
Nová Poradňa o hliníkovej elektroinštalácii, spevnenie PE/PEN provenance, konceptuálna HTML/CSS mapa RCD–RCCB–RCBO, klikateľné parent eyebrow odkazy, jemnejší homepage headline, foto-based homepage social preview a deterministický CSS build. Merania a MI 3102 BT zostávajú mimo tohto release. Podrobnosti: `RELEASE-v0.5.13.md`.


## v0.6.0 prototype A3 – customer-first test
Testovací build presúva zákaznícku situáciu pred odbornú tému: explicitne pomenúva pripravované revízne služby, dáva kontakt priamo do hero, prerába vstup Poradne podľa situácií a technické skratky LPS/RCD vysvetľuje krátkym popoverom pred voliteľným prechodom do Glosára. Nejde o produkčný release ani Commercial Switch. Podrobnosti: `PROTOTYPE-v0.6.0-A3.md`.


## v0.6.0 prototype A4 – compression pass
A4 zachováva customer-first smer A3, ale redukuje homepage na šesť hlavných blokov, spája priebeh s výstupom, intervaly s otázkou „kedy“, posúva cenu vyššie a výrazne zjednodušuje `/revizie/`. Hlavná navigácia je zákaznícka; Glosár a Meranie sú pod jasným vstupom „Odborný obsah“. Nejde o produkčný release ani Commercial Switch. Podrobnosti: `PROTOTYPE-v0.6.0-A4.md`.


## v0.6.0 prototype A5 – customer-language pass
A5 je posledný prototyp pred slepým používateľským testom. Zachováva architektúru A4, ale odstraňuje z homepage skorú technickú terminológiu, skracuje zákaznícku cestu, zjednocuje cenu a kontakt, upravuje Poradňu a O mne a dopĺňa accessibility guardraily. Nejde o produkčný release ani Commercial Switch. Podrobnosti: `PROTOTYPE-v0.6.0-A5.md`.


## v0.6.0-rc1 – Revízie na prvom mieste
Release candidate po ľudskom testovaní A5. Zachováva jednoduchú customer-first architektúru, spevňuje dôveryhodnosť, očakávania pri náleze nedostatku, consent-first customer-journey analytiku a produkčné regresné guardraily. Nejde o Commercial Switch. Podrobnosti: `RELEASE-v0.6.0-rc1.md`.


## v0.6.0 – Revízie na prvom mieste
Finálny service-first release po prototypoch A–A5 a RC1. Homepage, Revízie, Poradňa a O mne vedú zákazníka od konkrétnej situácie k priebehu, cene a kontaktu; odborný obsah zostáva v sekundárnej vrstve. Final-fix pass spevňuje pravdivosť pri MI 3102 BT, structured data, light-theme kontrast, obrázkové rozmery/výkon a analytické placementy. Komerčné služby stále nie sú spustené. Podrobnosti: `RELEASE-v0.6.0.md`.

## v0.6.1 – Desktop, responsive & social polish
Produkčný responsive/social polish po service-first redizajne.

## v0.6.2 – UX + discovery polish
Celý homepage portrét bez cropu, Enter v searchi, rozšírená Poradňa, responsive a light-theme hardening.

## v0.6.3 – Post-release UX hardening
Domov v navigácii, čitateľnejší light accent, bezpečnejšie popovery, odlíšený homepage hero, vCard/QR a stav `osvedčenie vydané`. Podrobnosti: `RELEASE-v0.6.3.md`.

## v0.6.4 – Stability & consent hardening
Consent regrant, bezpečný fallback bez `localStorage`, negatívne search testy, GA search privacy defense-in-depth, podcast error/selection semantics, mobilný popover/hamburger/QR polish, odstránenie copy-link UI pri zachovaní deep linkov, stručný sync `llms.txt`, deployment surface guardrail a verejný build fingerprint. Komerčné služby zostávajú nespustené. Podrobnosti: `RELEASE-v0.6.4.md`.



## v0.6.5 – Odborná spôsobilosť a overený odborný obsah

- Verejná redigovaná kópia osvedčenia E2/A + viewer fit/100 %.
- Samostatné stránky BE-001 až BE-004 s audio-overenými transcriptmi a odbornými spresneniami.
- PodcastEpisode/AudioObject schema, RSS, sitemap, search index a mapa obsahu synchronizované.
Verejná redigovaná 1. strana osvedčenia E2/A na stránke O mne, viewer fit/100 %, štyri samostatné podcastové stránky s audio-overenými transcriptmi, odbornými spresneniami a strojovo čitateľným podcast/credential kontextom. Commercial Switch je naďalej vypnutý. Podrobnosti: `RELEASE-v0.6.5.md`.




## v0.6.8 – Commercial readiness & release identity
Viditeľná release identita vo footeri z jedného zdroja pravdy, fail-closed predkomerčný manifest, izolovaný **full-state** commercial dry-run a GO/NO-GO checklist pre budúci v0.7.0 Commercial Switch. RC2 navyše v dry-rune transformuje predkomerčné statusové texty naprieč celým webom, zobrazuje neuzavreté obchodné rozhodnutia, kontroluje nulové protirečenia, oddeľuje podcastovú integritu do generického validátora a spevňuje publication/production checks. Verejná produkčná vrstva zostáva striktne pre-commercial. Paralelne pribúda BE-005 „TEST na prúdovom chrániči: čo overí a čo nie“ s audio-overeným transcriptom a odbornými spresneniami. Podrobnosti: `RELEASE-v0.6.8.md`.

## v0.6.7 – Content graph & query gaps

Lepšie využitie existujúceho odborného obsahu: content-graph audit a tooling, presnejšie search intent routing, kontextové prelinkovanie podcastov/Poradne/Glosára, selektívny Article.image pass, praktická Poradňa „Ako čítať revíznu správu?“ a väčší desktopový QR kontakt. Customer-first vrstva a predkomerčný stav zostávajú nezmenené. Podrobnosti: `RELEASE-v0.6.7.md`.
