# Bezpečná elektrika v0.4.5

Posledná obsahová a UX iterácia vetvy 0.4.x pred produkčnou vrstvou 0.5.

## Hlavné zmeny

### Jasnejšie vstupné cesty na homepage
Pôvodný šesťprvkový rýchly navigátor nahrádza trojica ciest podľa zámeru návštevníka:
- Potrebujem riešiť revíziu
- Chcem pochopiť problém alebo výsledok
- Chcem ísť do technického detailu

Zmena nepridáva ďalšiu sekciu; existujúcu orientáciu zjednodušuje a znižuje vizuálnu hustotu homepage.

### Glosár ako znalostná sieť
Doplnené kurátorované väzby „Súvisí s“ pri kľúčových pojmoch:
RCD, RCCB, RCBO, PE, RISO, Zs, SPD, LPS a odpor uzemnenia.

Cieľom nie je vytvoriť komplikovaný graf, ale pomôcť návštevníkovi pokračovať k súvisiacemu pojmu, meraniu, revízii alebo aktuálnemu článku.

### Budúce prípadové štúdie
Pridaná interná redakčná šablóna `docs/CASE-STUDY-TEMPLATE.md`:
Situácia → Prehliadka → Skúšanie a meranie → Vyhodnotenie → Náprava → Kontrolné meranie → Výsledok.

Šablóna nie je verejnou rubrikou a neobsahuje fiktívne prípady.

## Bez zmeny
- status projektu a právne formulácie,
- podcast BE-001 a R2 infraštruktúra,
- vizuálny systém v0.4.x,
- hlavná štruktúra Revízií, Poradne, Merania, Podcastu, Noviniek, O projekte a Metodiky.

## Ďalší krok
Po vizuálnej kontrole na mobile a desktope môže byť v0.4.5 posledným release vetvy 0.4.x.
v0.5.0 je plánovaná ako produkčná vrstva: jednotné metadata, Open Graph, structured data, sitemap/robots audit, privacy/cookies a následné napojenie vyhľadávacích a analytických nástrojov.

## Hotfix po vizuálnej kontrole
- hero označenie „O projekte“ sa už neláme na dva riadky na mobile ani desktope,
- podcastový workflow používa formuláciu „aspoň tri varianty“.
