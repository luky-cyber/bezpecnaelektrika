# v0.6.3 – Post-release UX hardening

Dátum: 31. 08. 2026

## Zmeny
- Light theme zjednocuje starší `--accent` token s AA-safe akcentom `#137672`, aby boli malé uppercase/kicker texty čitateľné aj na svetlých povrchoch.
- Hlavná navigácia obsahuje explicitný odkaz `Domov` na desktope aj v mobilnom hamburger menu.
- Term popovery v Poradni majú explicitné tlačidlo na zatvorenie, pričom zostáva zachované zatváranie cez `Esc`, klik mimo a viewport anchoring do 1100 px.
- Logo v hero bloku `/revizie/` má väčšiu vizuálnu váhu na desktope aj mobile bez zmeny štruktúry hero sekcie.
- Dialóg Nastavenia analytiky má explicitný accessible name cez `aria-labelledby`.
- Homepage je nad foldom jasne odlíšená od `/revizie/`: brand lockup s logom a H1 `Viac než revízie elektrických zariadení` zachováva revízie ako primárny CTA cieľ a zároveň komunikuje odborný obsah webu.
- Homepage kontakt ponúka stiahnuteľnú vCard s rozpoznateľným názvom súboru a kompaktný QR kód v rovnakom princípe ako likavcan.cz; QR smeruje na `/bezpecna-elektrika-lukas-likavcan.vcf` a neobsahuje Commercial Switch údaje.
- vCard používa rovnaký UTF-8 profil ako priložená karta z likavcan.cz: vCard 3.0, CRLF, bez BOM, `CHARSET=utf-8` a bez `QUOTED-PRINTABLE`. Kompatibilita s Classic Outlookom zostáva predmetom manuálneho testu; ak zlyhá, ďalší krok bude samostatný Outlook import fallback, nie ďalšie miešanie kódovaní v hlavnej vCard.
- Keďže sa významne mení homepage copy, homepage `dateModified` a sitemap `lastmod` sú aktualizované na 2026-08-31.

- Hubové H1 mimo homepage a `/revizie/` sú na desktopoch zmenšené, aby nepôsobili monumentálnejšie než hlavný homepage nadpis.
- CTA `Profesijný profil →` na stránke O mne má výraznejšiu, stále nekomerčnú vizuálnu váhu.

## Scope guardrails
- Bez novej homepage sekcie; zostáva šesť hlavných top-level sekcií a service-first funnel.
- Bez zmeny title/description/OG stratégie, bez nových Poradní alebo SEO doorway obsahu.
- Bez zmeny GA4/consent logiky a bez zásahu do podcast MP3 delivery.
- Bez Commercial Switch prvkov: žiadne aktívne objednávanie, cenník, telefón, `areaServed` ani LocalBusiness/Electrician/Service/Offer schema.

- Stránka O mne má kompaktný kontaktný blok: e-mail, vCard a QR bez ďalšej samostatnej sekcie.
- Stav kvalifikácie je aktualizovaný: E2A skúška absolvovaná, osvedčenie vydané; komerčné služby zostávajú nespustené.
- Hlavný vCard súbor `bezpecna-elektrika-lukas-likavcan.vcf` kopíruje UTF-8 profil z likavcan.cz (vCard 3.0, CRLF, bez BOM, `CHARSET=utf-8`); `/kontakt.vcf` zostáva len ako kompatibilný alias.
