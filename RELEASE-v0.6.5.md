# v0.6.5 – Odborná spôsobilosť a overený odborný obsah

Dátum: 11. 9. 2026

## Zmeny

- Stránka **O mne** obsahuje verejnú redigovanú 1. stranu osvedčenia E2/A; citlivé osobné údaje a podpis zostávajú redigované.
- Osvedčenie dostáva prístupný viewer: náhľad → prispôsobenie displeju → 100 % natívna veľkosť s posúvaním.
- Podcasty **BE-001 až BE-004** majú samostatné indexovateľné URL, audio, redakčne skontrolované transcripty s časmi a samostatné odborné spresnenia.
- Nejednoznačné miesta v transcriptoch boli porovnané s pôvodným audiom; verejný transcript neobsahuje interné značky `[OVERIŤ V AUDIU]` ani `[VECNE OVERIŤ]`.
- Každá epizóda uvádza pôvod transcriptu, dátum vecnej kontroly, súvisiaci obsah, zdroje a edukačný disclaimer.
- Podcast schema používa samostatné `PodcastEpisode` URL a `AudioObject`; RSS odkazy smerujú na kanonické stránky epizód.
- Podcast hub, sitemap, mapa obsahu, interné vyhľadávanie a `llms.txt` sú synchronizované s novými stránkami.

## Scope guardrails

- **Bez Commercial Switchu:** žiadne objednávanie, telefón, ceny, `LocalBusiness`, `Electrician`, `Service`, `Offer` ani `areaServed`.
- Verejná kópia osvedčenia je výslovne označená ako **1. strana** a nenahrádza originál dokumentu.
- Evidenčné číslo osvedčenia sa nepridáva ako samostatný textový údaj mimo samotnej verejnej kópie.
- Transcript zostáva verný hovorenému obsahu; odborné spresnenia sú vizuálne a sémanticky oddelené.
- `Zs ≠ Zline`; tlačidlo TEST na RCD sa neprezentuje ako overenie celej RCD ochrany alebo elektroinštalácie.
- `/hladat/` zostáva `noindex,follow` a mimo sitemapu.
