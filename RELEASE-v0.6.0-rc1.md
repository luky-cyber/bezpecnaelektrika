# Bezpečná elektrika v0.6.0-rc1 — Revízie na prvom mieste

Release candidate postavený na používateľsky otestovanom prototype A5. Nejde o Commercial Switch: komerčné služby zatiaľ nie sú spustené.

## Čo rc1 spevňuje

- customer-first informačnú architektúru A5 bez ďalšieho redesignu;
- kompaktný dôveryhodnostný signál s autorom a odkazom na kvalifikáciu/profil;
- praktické očakávanie „čo ak sa pri revízii nájde problém“;
- konzistentné CTA „Opýtať sa na revíziu“ bez predstierania objednávky;
- consent-first customer-journey udalosti: `service_interest_click`, `price_interest_click`, `service_situation_click`, `expert_content_click`;
- privacy text pre nové udalosti bez odosielania obsahu e-mailu alebo voľného textu;
- SEO/social snippet pass pre homepage a Poradňu;
- regresné guardraily pre service-first homepage, navigáciu, predkomerčný stav a technickú hĺbku mimo hlavnej zákazníckej cesty.

## Predkomerčný stav

Revízne služby v rozsahu E2A sú v príprave. Skúška je úspešne absolvovaná, čakám na osvedčenie a komerčné služby zatiaľ neposkytujem. rc1 nepridáva telefón, oblasť pôsobenia, cenník, booking ani `LocalBusiness` / `Electrician` / `Service` / `Offer` schema.

## Meracia technika

Metrel MI 3102 BT EurotestXE je fyzicky k dispozícii; bolo skontrolované príslušenstvo a overené zapnutie. rc1 nepridáva tvrdenia o reálnych meraniach alebo použití prístroja v praxi.

## Pred ostrým v0.6.0

Overiť reálny mobil, klávesnicu, 5-sekundové pochopenie služby, CTA, cenu, Poradňu a prechod do odbornej vrstvy. Commercial Switch zostáva samostatný krok až po splnení reálnych formálnych a prevádzkových podmienok.
