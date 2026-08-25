# Bezpečná elektrika v0.5.10 – Odborná autorita a vlastné vizuály II

Dátum: 25. 08. 2026

## Hlavný cieľ

v0.5.10 pokračuje v štandarde v0.5.9: menej nových vrstiev, viac hĺbky existujúcich tém, vlastné technické diagramy a transparentná proveniencia.

## Odborný obsah

- výrazne prehĺbená stránka **LPS / ochrana pred bleskom**;
- dôsledne zachovaná hranica, že typ budovy sám neurčuje triedu LPS;
- aktualizovaný rámec na IEC 62305-1/-2/-3/-4:2024;
- rozšírená proveniencia na RCCB/RCBO, TN sústavách, uzemnení a izolačnom odpore.

## Vlastné diagramy

- **BE-DIAG-03 – Zs ≠ Zline**;
- **BE-DIAG-04 – RCCB vs RCBO**;
- **BE-DIAG-05 – TN-C → TN-C-S**;
- diagramy sú didaktické a neslúžia ako realizačné návody.

## Poradňa

Nová samostatná odpoveď:

- **Čo znamená, keď prúdový chránič opakovane vypína?**

Text výslovne oddeľuje pozorovaný jav od diagnózy a vysvetľuje, prečo tlačidlo TEST nenahrádza odborné overenie.

## OG / social vizuály

Doplnené vlastné vizuály pre:

- Glosár / Knowledge Base;
- Meranie v praxi;
- Podcast;
- RCD;
- Zs;
- LPS.

## Interné prelinkovanie

Posilnené tematické clustre RCD ↔ RCCB/RCBO ↔ Poradňa a Zs ↔ Zline ↔ TN sústavy.

## Čo v0.5.10 zámerne nerobí

- nepridáva LocalBusiness/Service schema;
- nepridáva lokalitu, ceny, telefón ani objednávkový formulár;
- nerozširuje llms.txt ani crawler experimenty;
- nevytvára fiktívne case studies alebo merania.
## Finálny pre-deploy polish

- odstránené nechcené trojstranné čiarkované orámovanie pri objednanom MI 3102 BT; stav zostáva komunikovaný textom a štítkom;
- optimalizované malé logo používané v hlavičke (samostatný WebP asset, veľký PNG originál zostáva zachovaný);
- všetky detailné odpovede Poradne používajú spoločný OG vizuál Poradne;
- RCD, Zs a LPS majú dorovnané `og:image:alt` a `twitter:image`;
- zjednotené viditeľné dátumy dvoch nových odpovedí Poradne s `dateModified`;
- pridaný priamy interný odkaz z Revízií na odpoveď o prerobenom rozvádzači;
- doplnené editovateľné SVG zdroje pre novšie OG karty;
- release validator kontroluje nový vizuálny a metadata štandard.

