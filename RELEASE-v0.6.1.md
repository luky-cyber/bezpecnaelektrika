# Bezpečná elektrika v0.6.1 — Desktop, responsive & social polish

Dátum vydania: 28. august 2026

v0.6.1 je údržbový release nad service-first základom v0.6.0. Nejde o Commercial Switch a nemení stav poskytovania služieb. Cieľom je lepšie využitie priestoru na väčších monitoroch, bezpečnejšie správanie na tabletoch a jasnejší náhľad pri zdieľaní odkazu na homepage.

## Hlavné zmeny

### Homepage
- opravená HTML štruktúra hero sekcie tak, aby desktopový grid skutočne používal dva stĺpce;
- text a stav služby zostávajú vľavo, fotografia je na širokých obrazovkách vpravo;
- obmedzená výška hero fotografie, aby zbytočne neodsúvala sekciu „Čo potrebujete riešiť?“;
- pri šírkach do približne 840 px sa hero skladá do jedného stĺpca, aby zostal prirodzený na tabletoch;
- mobilný layout zostáva zachovaný.

### Revízie
- kompaktnejší desktop hero na `/revizie/`;
- menší vizuálny tlak H1 a efektívnejšie využitie prvého viewportu pri 1600×900 a 1920×1080;
- obsah, rozsah služby a predkomerčný stav sa nemenia.

### Poradňa
- opravený horizontálny overflow informačných term-popoverov na tabletových šírkach;
- bez zmeny správania na bežnom desktope a mobile.

### Ultra-wide / 4K
- pri veľmi širokých CSS viewportoch sa jemne zväčší základná typografia a maximálna šírka kontajnera;
- bežné desktopové rozmery 1600×900, 1920×1080 a 2560×1440 zostávajú bez plošného rozťahovania od okraja k okraju.

### Social preview
- nový branded OG obrázok pre homepage: `assets/img/og/og-home-revizie-v3.jpg`;
- nový social title: `Bezpečná elektrika – Revízie`;
- nový social description:
  `Pripravované revízie elektroinštalácií pre domy, byty a vybrané administratívne priestory.`;
- synchronizované Open Graph a Twitter metadata;
- hero fotografia na samotnej stránke zostáva nezmenená.

### Podcast a aktuálny obsah
- release snapshot obsahuje aj aktuálne publikovanú epizódu BE-004 „Revízna správa nie je len papier“ a súvisiace podcastové dáta/feed.

### Validácia
- aktualizovaný release validator pre nový social preview a nové responsive guardraily;
- zachované service-first a pre-commercial guardraily z v0.6.0.

## Overené kontroly

Pred vytvorením release archívu prešli:

- CSS build check;
- deterministický Search index — 33 záznamov;
- Search smoke test;
- News sitemap — 0 oprávnených článkov, bez generovania súboru;
- release validator — 36 HTML stránok;
- v0.6.0 service-first / pre-commercial baseline validator;
- JavaScript syntax check;
- vizuálny audit hlavných šablón na 1600×900, 1920×1080, 2560×1440, 3840×2160, 768×900 a 390×844.

## Bez zmeny

v0.6.1 stále nie je komerčné spustenie služieb. Release nepridáva:

- aktívne objednávanie;
- telefón;
- reálny cenník;
- oblasť pôsobenia;
- LocalBusiness/Electrician/Service/Offer schema;
- tvrdenie, že služby sú už spustené.

Commercial Switch zostáva samostatným budúcim krokom až po splnení reálnych podmienok.
