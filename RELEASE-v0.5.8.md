# Bezpečná elektrika v0.5.8

## AI/Search + Identity + UX/Performance cleanup
- `OAI-SearchBot` zostáva povolený pre vyhľadávanie a citácie; `GPTBot` je v `robots.txt` zablokovaný.
- `ChatGPT-User` zostáva povolený pre používateľom vyžiadané načítanie stránky.
- Viditeľné prepojenie kontaktu na profesijný profil autora `https://likavcan.cz/lukas/`.
- Audit a zjednotenie identity `Person ↔ Project`, stabilných `@id`, `sameAs`, `knowsAbout` a relevantných `dateModified`.
- Jemne skrátená homepage: odstránené dve redundantné sekcie opakujúce už vysvetlenú hlavnú tézu.
- Znížené opakovanie statusu pripravovaných služieb na stránke Revízie.
- Pridané kontextové CTA na O projekte, Meraní, Glosári, Novinkách a Metodike.
- Posilnené interné odkazy na existujúce odpovede v Poradni a detail izolačného odporu v Knowledge Base.
- Opravené zavádzajúce `#faq` odkazy v Poradni; Uzemnenie/LPS vedú na konkrétne stránky a spotrebiče na relevantnú sekciu Revízií.
- Opravená nesprávne aktívna položka „O projekte“ v mobilnej navigácii Metodiky.
- Produkčný `style.css` už nepoužíva reťaz `@import`; zdrojové CSS moduly ostávajú zachované pre údržbu.
- Jemný audit title/OG title pre Poradňu, Meranie a Glosár.
- `llms.txt` zostáva zámerne stručný; FAQ schema sa ďalej nerozširuje.
- Release validator rozšírený o crawler policy, CSS importy, autorov profil, Metodiku, Poradňu a CTA kontroly.

## Čo sa zámerne nemení
- Bez newsletter/lead formulára.
- Bez lokality, cien, telefónu a `LocalBusiness`/`Service` schémy pred reálnym spustením služieb.
- Bez fiktívnych referencií alebo prípadových štúdií.

## Manuálna kontrola po deploymente
Cloudflare/WAF môže crawler zablokovať nezávisle od `robots.txt`. Po nasadení preto treba overiť, že `OAI-SearchBot` nie je blokovaný pravidlami Cloudflare.
