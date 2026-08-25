# Bezpečná elektrika v0.5.9 – Odborná autorita a vlastné vizuály

Dátum: 25. 08. 2026

## Hlavný cieľ

v0.5.9 presúva ďalší vývoj od technického AI/SEO polishu k hĺbke existujúceho odborného obsahu, viditeľnému autorstvu a vlastným technickým vizuálom.

## Odborný obsah

- výrazne prehĺbená stránka **RCD / prúdový chránič**;
- výrazne prehĺbená stránka **Impedancia poruchovej slučky Zs**;
- nový jednotný spôsob práce s hranicami tvrdenia: všeobecne / v praxi / závisí od kontextu / čo nemožno automaticky vyvodiť;
- pilotný komponent **Odborný a normatívny základ** s vysvetlením, čo konkrétny zdroj podporuje a čo je praktická interpretácia;
- pri IEC 60364-6 sa vedome neprezentuje predbežná verzia 2026 ako už vydaná finálna norma.

## Vlastné diagramy

- **BE-DIAG-01 – Ako sa overuje elektrická inštalácia**: Prehliadka → Skúšanie → Meranie → Vyhodnotenie → Dokumentácia;
- responzívny desktop a mobile variant;
- **BE-DIAG-02 – Čo tvorí poruchovú slučku Zs?**;
- diagramy sú didaktické interpretácie, nie reprodukcie normových obrázkov;
- SVG obsahuje title/desc a stránky obsahujú aj HTML figcaption/provenienciu.

## Poradňa

Dve nové samostatné odpovede:

1. **Potrebujem revíziu pri kúpe staršieho domu alebo bytu?**
2. **Elektrikár prerobil rozvádzač – čo nasleduje?**

Druhá otázka bola zvolená bez tvrdenia, že ju podporil Search Console baseline; v dostupnom build prostredí nebol prístup k týmto dátam.

## Viditeľné autorstvo

- standalone stránky Poradne a Knowledge Base zobrazujú autora **Ing. Lukáš Likavčan, PhD.**;
- meno smeruje na `https://likavcan.cz/lukas/`;
- dátumy zostávajú viazané na skutočnú aktualizáciu jednotlivých stránok.

## OG / social vizuálny systém

Prvé tri vlastné OG obrázky:

- `og-home-v1.jpg`;
- `og-revizie-v1.jpg`;
- `og-poradna-v1.jpg`.

Zdrojové SVG šablóny ostávajú v `assets/img/og-src/`.

## Interné prelinkovanie

Posilnené sú najmä cesty medzi Revíziami, Meraním a odpoveďami o revíznej správe, rozdiele elektrikár/revízia, možnostiach overenia bez rozoberania a funkčnej zásuvke.

## Merateľnosť

- pridaný interný checklist `docs/ANALYTICS-BASELINE-v0.5.8.md`;
- baseline treba vyplniť **pred nasadením v0.5.9**;
- nejde o novú analytickú vrstvu webu.

## Čo v0.5.9 zámerne nerobí

- nepridáva LocalBusiness/Service schema;
- nepridáva lokalitu, ceny, telefón ani lead formulár;
- nerozširuje llms.txt;
- nevytvára fiktívne case studies;
- neprehĺbuje ešte LPS – táto téma zostáva na ďalší release.
