# Bezpečná elektrika v0.6.0 – Revízie na prvom mieste

Dátum: 2026-08-26

## Hlavná zmena
v0.6.0 mení informačnú hierarchiu webu z content-first na service-first. Návštevník najprv vidí pripravované revízne služby, typické situácie, kedy revíziu riešiť, čo ovplyvňuje cenu, priebeh a výsledok. Poradňa zostáva praktickým mostom a Glosár, Meranie, Novinky, Podcast a Metodika tvoria sekundárnu odbornú vrstvu.

## Final-fix pass po RC1
- MI 3102 BT sa v Glosári neprezentuje ako už reálne použitý prístroj; názvy prístrojov/metód označujú technickú väzbu na overenie a reálne merania sa dokumentujú osobitne.
- `/revizie/` má odlíšený search title od homepage.
- `publisher` v structured data už nesmeruje na entitu typu `Project`; používa stabilnú Person identitu autora.
- FAQ structured data na `/revizie/` zodpovedá viditeľným otázkam a odpovediam.
- Project description je zjednotený na service-first formuláciu.
- Light-theme sekundárny text má vyšší kontrast.
- 491 kB logo nie je používané v malých profilových kartách; používa sa optimalizovaný WebP.
- Hero a technické diagramy majú intrinsic dimensions na obmedzenie layout shiftu.
- Alternatívne situačné karty už nepoužívajú číslovanie 01–04; číslovanie ostáva pri skutočnom procese.
- Poradňa má konzistentný active state, analytics placementy sú presnejšie a breadcrumb `/o-projekte/` používa názov „O mne“.

## Predkomerčný stav
Revízne služby v rozsahu E2A sú stále v príprave. Skúška revízneho technika je úspešne absolvovaná, čaká sa na vydanie osvedčenia a komerčné služby zatiaľ nie sú poskytované. Release nepridáva telefón, oblasť pôsobenia, reálny cenník, booking ani LocalBusiness/Electrician/Service/Offer schema.

## Meracia technika
Metrel MI 3102 BT je fyzicky k dispozícii; príslušenstvo bolo skontrolované a bolo overené zapnutie. v0.6.0 nepublikuje reálne merania vykonané týmto prístrojom ani ich nepredstiera.
