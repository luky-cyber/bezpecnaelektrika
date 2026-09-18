# v0.6.8 – Commercial readiness & release identity

Dátum: 14. 9. 2026

## Cieľ

Pripraviť bezpečný, auditovateľný prechod k budúcemu Commercial Switchu bez toho, aby sa na verejnom webe predčasne aktivovala ponuka služieb. Zároveň spraviť release/build identitu viditeľnú priamo na každej stránke.

## RC9

- Release identita je `v0.6.8-rc9`; commercial state zostáva striktne `precommercial`, `goLiveAllowed=false`, `publicCommercialServices=false`.
- Homepage si ponecháva priamy service H1 `Revízie elektrických zariadení a inštalácií`; `/revizie/` má odlišný H1 `Revízie: rozsah, priebeh a cena`, aby obe zákaznícke vstupné stránky nepôsobili ako duplikát.
- Logo v hero `/revizie/` používa portrétový rám 2:3 podľa zdrojového assetu 256×384; celý wordmark vrátane riadku `ELEKTROREVÍZIE` musí zostať vnútri rámčeka na mobile aj desktope.
- Sticky desktop header, anchor clearance, RC7 humanizačný copy, privacy/safety guardraily a Commercial Switch sa nemenia.
- `/revizie/` je vecne zmenené 17. 9. 2026, preto sa synchronizuje jeho `dateModified`, sitemap `lastmod` a Search záznam.

## RC8

- Release identita je `v0.6.8-rc8`; commercial state zostáva striktne `precommercial`, `goLiveAllowed=false`, `publicCommercialServices=false`.
- RC8 je úzky UX patch nad RC7 bez obsahových zmien: desktopová horná navigácia zostáva pri scrollovaní dostupná cez `position: sticky`; mobilná navigácia zostáva nezmenená.
- Fragmentové odkazy a kompatibilitné anchor aliasy rešpektujú výšku sticky hlavičky, aby cieľový nadpis po navigácii nezostal prekrytý.
- Logo Bezpečná elektrika v hero sekcii `/revizie/` je na mobile aj desktope explicitne uzavreté do zaobleného rámčeka (`overflow: hidden`) a celý transparentný znak sa škáluje cez `object-fit: contain`.
- RC8 nemení customer copy RC7, odborné články, privacy/consent, safety guardraily, sitemap `lastmod` ani Commercial Switch.

## RC7

- Release identita je `v0.6.8-rc7`; commercial state zostáva striktne `precommercial`, `goLiveAllowed=false`, `publicCommercialServices=false`.
- RC7 je posledný úzky copy/humanization pass nad RC6. Vychádza z konkrétneho porovnania RC6 s alternatívnym zákazníckym copy návrhom; nepreberá jeho technické zmeny ani nemení architektúru webu.
- Homepage zachováva presný H1 `Revízie elektrických zariadení a inštalácií`; prvý fold je mierne odľahčený a kvalifikačný stav je formulovaný prirodzenejšie.
- Poradňa používa kratšie zákaznícke karty a vybrané boxy `Stručne` sú prepísané do 1–3 bežných viet bez oslabenia odborných a safety hraníc.
- RC7 zámerne nepreberá z návrhu zúžený H1 `Revízie pre domy a byty`, päťročný periodicity anchoring, inline FOUC script ani odstraňovanie `data-prototype` styling hookov.
- Odborné články, privacy/consent, podcastové korekcie, Zs ≠ Zline, RCD TEST a fail-closed Commercial Switch zostávajú stabilné.

## RC6

- Release identita je `v0.6.8-rc6`; commercial state zostáva striktne `precommercial`, `goLiveAllowed=false`, `publicCommercialServices=false`.
- RC6 je úzky customer-clarity/human-voice pass založený na zhode troch nezávislých UX auditov RC5. Nepridáva nové funkcie ani nemení odborné, safety, privacy alebo Commercial Switch guardraily.
- Homepage hovorí službu priamo v H1 (`Revízie elektrických zariadení a inštalácií`), nadpisuje predkomerčný stav ako pripravované služby revízneho technika a oddeľuje službu od sekundárneho odborného obsahu.
- E2A/E2/A zostáva zachované ako presný kvalifikačný údaj, ale na zákazníckych miestach je najprv vysvetlený jeho význam.
- Homepage, Revízie a Poradňa používajú menej administratívne formulácie; opakovaný precommercial status v článkoch je nahradený jednou prirodzenou kontaktnou vetou.
- Vybrané `Stručne` odpovede v Poradni boli preformulované do kratšieho jazyka bez zmeny odborných hraníc. Odborné články neprešli plošným prepisom a zachovávajú rozdielny rytmus tém.
- `Merať. Dokumentovať. Vysvetľovať.` zostáva zámerne zachované ako identita projektu.

## RC5

- Release identita je `v0.6.8-rc5`; commercial state zostáva striktne `precommercial`, `goLiveAllowed=false`, `publicCommercialServices=false`.
- RC5 je redakčný simplification pass nad RC4. Neoslabuje safety, privacy, accessibility ani Commercial Switch guardraily.
- `/poradna/` a `/obsah/` boli zjednodušené na orientáciu a navigáciu bez opakovania textu cieľových stránok.
- Praktické články o príprave na revíziu a hliníkovej elektroinštalácii boli skrátené a preformulované do prirodzenejšieho jazyka; odborné zdroje ostali zachované.
- Glosárové stránky Zs a LPS odstránili duplicitné interpretačné vrstvy, pričom zostali zachované kritické technické rozlíšenia vrátane `Zs ≠ Zline` a väzby triedy LPS na návrh a posúdenie rizika.
- Podcast hub, stránka Revízie a Meranie boli očistené od interného workflow jazyka, opakovaných FAQ a copywritingových sloganov.
- Opakovaný disclaimer/provenance boilerplate bol odstránený z jednotlivých Poradní a Glosára; metodika zostáva centralizovaná na `/metodika/`.

## RC4

- Release identita je `v0.6.8-rc4`; commercial state zostáva striktne `precommercial`, `goLiveAllowed=false`, `publicCommercialServices=false`.
- RC4 je hardening release bez Commercial Switchu: privacy/consent, WCAG, safety/human-factors, security/release, SEO, performance a UX.
- Privacy notice dopĺňa účely/právne základy, príjemcov/prenosy, retenčné kritériá, práva a dozorný orgán; obchodná identita, adresa ani telefón sa nevymýšľajú. Consent sa lokálne ukladá s `decidedAt` a `policyVersion` a obnovuje sa po zmene policy alebo približne po 12 mesiacoch.
- Mobilné menu pri otvorení presunie keyboard focus do navigácie; input borders majú AA non-text contrast; fixed consent banner vytvára focus/scroll clearance.
- Podcast hub má SSR zoznam epizód a audio sa nenačítava pred Play. BE-001 až BE-003 majú safety notice pred prehratím; BE-002 explicitne koriguje formuláciu „100 % v poriadku“ a raw transcript je vylúčený zo Search snippet textu. RSS upozorňuje na odborné spresnenia.
- Poradňa dopĺňa minimalistickú tiesňovú/escalation hranicu a článok o opakovanom vybavovaní RCD zakazuje zámerné reprodukovanie poruchy. RCD TEST má failure-closure formuláciu.
- Revízie rozlišujú spotrebiče/predlžovacie prívody od revízie pevnej inštalácie. Verejná stránka uvádza iba normové a metodické referencie, ktoré sú na nej skutočne zobrazené; širší interný normový kontext sa nevydáva za publikovaný obsah.
- Homepage LCP hero používa `fetchpriority=high` a už nie je skrytý reveal animáciou. Precommercial status je pred hlavným CTA; mailové CTA je pomenované transparentnejšie.
- `/podcast/` má server/build-renderovaný obsah; social metadata sú zjednotené, `FAQPage` markup odstránený a `/o-projekte/` používa `ProfilePage`/`Person`.
- Pribudol `.gitignore`, pinované validačné dependencies a GitHub Actions source gate. Ochrana `main` rulesetom/status checkom zostáva manuálnym GitHub nastavením pred deployom.
- Production validator preveruje permanentné canonical redirecty vrátane www/legacy variantov, skutočný 404, anti-framing signál a kompresiu reprezentatívnych textových assetov.

## RC3

- Release identita je `v0.6.8-rc3`; produkčný stav zostáva `precommercial` a `goLiveAllowed=false`.
- Commercial dry-run je dotiahnutý na **full-surface simuláciu**: okrem 42 HTML stránok regeneruje `data/search-index.json` z transformovaného dry-run HTML, synchronizuje komerčný orientačný stav v `llms.txt` a zapisuje dry-run `version.json` s `channel=local-dry-run` a `commercialState=commercial-simulation`.
- `tools/validate-commercial-dry-run.py` vyžaduje nulové predkomerčné statusové protirečenia v HTML, Search indexe aj `llms.txt` a kontroluje samostatný dry-run version/state.
- `tools/build-search-index.py` dostal explicitné parametre pre izolované dry-run zostavenie; bežný produkčný build a Search routing ostávajú nezmenené.
- Viditeľný release link vo footeri ostáva podľa zámeru projektu, ale už nepoužíva znižujúcu `opacity`; malý text tak zachováva kontrast farby `--c-subtle`.
- Commercial Switch špecifikácia explicitne vyžaduje pri v0.7 regeneráciu Search indexu, aktualizáciu `llms.txt`, prepnutie version/commercial state a kontrolu celého verejného povrchu, nielen HTML.
- Production validator navyše skúša, že root interné Markdown súbory `README.md`, `COMMERCIAL-GO-LIVE.md` a `RELEASE-v0.6.8.md` nie sú verejne dostupné.
- Android smoke RC2 pred vytvorením RC3 neodhalil blocker; RC3 nemení odborný obsah, sitemap `lastmod` ani zákaznícku informačnú architektúru.

## RC2

- `config/release.json` je jediný zdroj pravdy pre verziu, release channel, fingerprint a predkomerčný stav; RC2 zobrazuje `v0.6.8-rc2`.
- `config/commercial-state.json` zostáva fail-closed: `precommercial`, `goLiveAllowed=false`, `publicCommercialServices=false`.
- Commercial dry-run je rozšírený z CTA experimentu na **full-state simuláciu** budúceho v0.7: transformuje predkomerčné statusové formulácie naprieč všetkými HTML, simuluje customer CTA a zároveň viditeľne ukazuje neuzavreté rozhodnutia (business identita, finálny rozsah, service area, cenový model, kontakt, kapacita, poistenie a schema voľba).
- `tools/validate-commercial-dry-run.py` vyžaduje `noindex,nofollow` + banner na každej dry-run HTML stránke, nulové predkomerčné protirečenia, vykreslenie všetkých unresolved polí a neprítomnosť dry-run vrstvy v produkčnom HTML.
- Dry-run schema zostáva zámerne **candidate-only** v `application/json`, nie aktívne JSON-LD. `Service`, `Electrician`, `LocalBusiness`, `Offer` ani `areaServed` sa do produkcie nepublikujú pred GO.
- Publication boundary je explicitne chránená: `.nojekyll` nesmie existovať a `_config.yml` musí vylučovať `config/`, `.build/`, `tools/` a `docs/`. `noindex` nie je náhradou tejto hranice.
- Podcastová integrita je oddelená do generického `tools/validate-podcasts.py`, ktorý kontroluje všetky publikované epizódy cez page/audio/PodcastEpisode/AudioObject/RSS/search/sitemap/content-map väzby. BE-005 tak už nie je definujúcou logikou Commercial Readiness validatora.
- `tools/validate-production-v068.py` rozširuje post-deploy kontrolu o HTTP→HTTPS a canonical-host redirecty, crawler directives, security-header report, cache/compression signály a kontrolu, že repository-only/dry-run artefakty nie sú verejne dostupné.
- `docs/PRODUCTION-ACCEPTANCE-v0.6.8.md` formalizuje stav `SOURCE PASS` / `PRODUCTION PENDING|PASS`. Production acceptance zostáva samostatná od source acceptance: lokálny PASS nepredstiera výsledok Cloudflare/WAF, CSP reportov, cache politiky, Range/206 ani field CWV.

## BE-005

BE-005 **„TEST na prúdovom chrániči: čo overí a čo nie“** zostáva publikovaný so zostrihaným 5:17 audiom, audio-overeným transcriptom, tromi odbornými spresneniami a synchronizáciou RSS/schema/search/sitemap. Aktuálny R2 object key zostáva `BE-005-test-prudoveho-chranica.mp3`, pretože lowercase objekt zatiaľ nebol potvrdený ako existujúci; URL sa nesmie meniť naslepo.

## Commercial guardrail

Produkčný v0.6.8 RC8 zostáva striktne **pre-commercial**. Žiadny aktívny objednávkový/sticky service CTA, telefón, cenník, `LocalBusiness`, `Electrician`, `Service`, `Offer`, `areaServed` ani verejný commercial preview parameter sa nepridáva.

## Acceptance stav

- SOURCE ACCEPTANCE: overuje sa lokálnym validator chainom vrátane full-state dry-runu a podcast integrity.
- PRODUCTION ACCEPTANCE: vykoná sa až po reálnom deployi; do toho času zostáva samostatným pending krokom.


## RC10 — shared design DNA polish + targeted UX fixes (2026-09-17)

- Visual polish aligns the existing Bezpečná elektrika design system with the calmer technical design DNA of Likavcan.cz without copying its brand, content structure or identity.
- Text measure, typography scale and vertical rhythm are more compact; card radii, borders, buttons, navigation and footer use the same restrained 12/16/24-radius grammar observed in the supplied Likavcan.cz v0.2.4 RC while retaining the Bezpečná elektrika service layout.
- Four equivalent service/customer choices use readable 2×2 desktop grids; mobile remains single-column where appropriate.
- The pre-commercial status cards on Home and Revisions use balanced 50:50 desktop columns and a calm card treatment while preserving the exact service-status wording.
- Revisions fragment navigation now marks `Kedy revíziu` and `Cena` as current locations on desktop and in the mobile hamburger menu; the mobile bottom navigation continues to mark the parent Revízie destination.
- RC9 portrait 2:3 logo containment, sticky desktop navigation, safety/privacy guardrails and precommercial fail-closed state are retained.
- No expert claims, service scope, pricing statements, SEO metadata or content `dateModified` values were changed by this visual pass.

## RC11 — shared authorial micro-UI/state polish (2026-09-17)

- Extends RC10 visual harmonisation with the supplied Likavcan.cz v0.2.4 RC at the micro-UI level without copying its layout or brand identity.
- Navigation active/current states now share a calm selected grammar: stronger text, soft accent surface and a 2 px accent line.
- `/revizie/` contextual navigation is scroll-aware for `Revízie`, `Kedy revíziu` and `Cena`, while preserving hash/keyboard semantics and the parent Revízie state in the mobile bottom navigation.
- Search, theme, hamburger, expert-content toggle and back-to-top controls use a common 44 px / 12 px utility-control geometry with aligned border, hover, focus and open-state treatment.
- Mobile selected states, static tags/badges and CTA surfaces are visually consolidated so accent colour communicates state/meaning instead of decorating every small element.
- RC10 macro-layout changes, Home/Revisions balanced pre-commercial status cards, RC9 portrait-logo containment and all safety/privacy/commercial guardrails remain intact.
- No expert claims, service scope, pricing statements, SEO metadata or content `dateModified` values were changed by this micro-UI pass.

## RC16 — Search cache revalidation hardening (2026-09-18)

- Search runtime changes `data/search-index.json` fetching from `force-cache` to `no-cache`, so browsers revalidate the current Search index instead of indefinitely preferring an older locally cached editorial state.
- This closes the production finding where an existing mobile browser could still show the historical wording that the E2/A certificate was awaited even though the current Search index correctly states that the certificate has been issued.
- A v0.6.8 regression guardrail rejects `force-cache` for the Search index and requires the revalidation policy.
- Search records, expert claims, service scope, pricing, SEO metadata and content `dateModified` values are unchanged.
- RC15 credential cold-start hardening and all RC14/RC13/RC12 design, navigation, accessibility, safety, privacy and pre-commercial guardrails remain unchanged.

## RC15 — credential viewer cold-start fit hardening (2026-09-18)

- Fixes a reproducible first-open/cold-start credential-viewer race seen in Android/Acode WebView: the dialog is opened and measured before the deferred full-resolution certificate image receives its `src`.
- The fit mode now explicitly fills the measured viewer stage and uses `object-fit: contain`, so the first opening starts with the complete certificate page fitted to the display instead of exposing only the native-size upper-left area.
- The existing `100 %` mode remains unchanged at the real 1097 × 1536 px document size; returning to `Prispôsobiť` restores whole-page fit.
- Deferred loading is retained: the full-resolution certificate is still not downloaded merely by loading `/o-projekte/`.
- RC14 release hygiene/contact semantics, RC13 Contact navigation, RC12 stable Revisions navigation, RC11 micro-UI, RC10 design-DNA polish and all safety/privacy/commercial guardrails remain unchanged.
- No public expert claims, service scope, pricing statements, SEO metadata or content `dateModified` values change in this compatibility fix.

## RC14 — release hygiene + accessibility/contact semantics (2026-09-18)

- Synchronizes README/current-release documentation with the actual RC14 release identity and removes a stale release-note claim that implied unpublished standards were visible on `/revizie/`.
- Search overlay close and glossary term-popover close controls now meet the project-wide minimum 44 × 44 px touch-target standard; the term popover reserves matching space so the larger control does not cover text.
- Homepage `Kontakt` is now a standalone semantic `<section id="kontakt">` while retaining the RC13 visual separation, anchor destination and mobile `Domov`/`Kontakt` milestone behavior; the release structural guardrail is updated from six to seven top-level homepage sections to reflect this intentional semantic split.
- RC13 Contact navigation, RC12 stable Revisions contextual navigation, RC11 shared-author micro-UI, RC10 macro design-DNA polish, RC9 portrait-logo containment and all safety/privacy/commercial guardrails remain unchanged.
- No expert claims, service scope, pricing statements, SEO metadata or content `dateModified` values change in this release-hygiene/accessibility pass.

## RC13 — distinct Contact destination + mobile navigation state (2026-09-18)

- Homepage now separates the real contact area from `Praktické otázky` with a visible `Kontakt` H2 after the expert-content strip and before the email/VCF/QR contact block.
- The `#kontakt` anchor moves to that heading, so desktop and mobile `Kontakt` links land on the actual contact area rather than the advice cards above it.
- Homepage mobile bottom navigation now treats `Kontakt` as an in-page milestone: `Domov` remains current above the Contact heading; `Kontakt` becomes current from that heading to the end of the page and is selected immediately during direct `/#kontakt` navigation.
- A short intent lock prevents `Domov` from flashing while the browser scrolls to the Contact anchor.
- RC12 stable Revisions navigation, RC11 shared-author micro-UI, RC10 macro design-DNA polish, RC9 portrait-logo containment and all safety/privacy/commercial guardrails remain unchanged.
- Homepage `dateModified`/sitemap/search date moves to 2026-09-18 because `Kontakt` is a visible structural content change; expert claims, scope, pricing and safety wording are unchanged.

## RC12 — stable Revisions contextual navigation (2026-09-17)

- Fixes a reproducible desktop/mobile contextual-navigation regression on `/revizie/`: manual scrolling no longer falls back to `Revízie` in the content gaps after `Kedy revíziu` or after `Cena`.
- Scroll-spy now treats `Kedy revíziu` and `Cena` as ordered milestones: the latest reached milestone remains current until the next tracked milestone is reached; scrolling upward reverses the same sequence cleanly.
- Direct clicks/hash navigation use a short navigation-intent lock so smooth scrolling from `Kedy revíziu` to `Cena` (and back) cannot briefly flash the parent `Revízie` item.
- The same contextual model is shared by desktop navigation and the mobile hamburger; the persistent mobile bottom navigation intentionally continues to mark the parent `Revízie` destination across the whole page.
- RC11 shared-author micro-UI, RC10 macro-layout/design-DNA polish, RC9 portrait-logo containment and all safety/privacy/commercial guardrails remain unchanged.
- No expert claims, service scope, pricing statements, SEO metadata or content `dateModified` values changed in this RC.
