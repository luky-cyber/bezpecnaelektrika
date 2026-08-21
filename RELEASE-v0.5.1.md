# Bezpečná elektrika v0.5.1

Konverzná, consent a analytická vrstva nad produkčným základom v0.5.0.

## Jemne silnejší marketing
- nový homepage callout: funkčnosť nie je dôkaz technického stavu,
- CTA stále používa „Kontakt k projektu“, keďže komerčné služby sú v príprave,
- Poradňa a odborné články majú kontextový kontakt iba tam, kde všeobecné vysvetlenie už nestačí.

## Google Analytics 4
- Measurement ID: `G-5W84N9FL5X`,
- Google tag sa nenačíta bez analytického súhlasu,
- reklamné consent signály zostávajú denied,
- vlastné udalosti: `contact_click` a `podcast_play`.

## Consent
- prvá návšteva: Povoliť analytiku / Len nevyhnutné / Nastavenia,
- voľba sa uchováva lokálne v `be-consent-v1`,
- používateľ môže voľbu kedykoľvek zmeniť cez pätičku,
- consent dialóg rozlišuje nevyhnutné a analytické použitie.

## Ochrana súkromia
- doplnené GA4, účel analytiky, Measurement ID, lokálna voľba súkromia,
- vysvetlené, že bez súhlasu sa Google Analytics skript nenačíta,
- reklamná personalizácia nie je súčasťou implementácie.

## Ďalší krok
Po nasadení: udeliť analytický súhlas na testovacej návšteve a následne použiť Google Analytics „Testovať inštaláciu“ + Realtime report.
