# Bezpečná elektrika v0.6.0 — prototyp A3

Testovací build „customer-first“ informačnej architektúry. Nie je určený ako produkčný release ani ako Commercial Switch.

## Čo sa testuje

- homepage hneď pomenúva, že ide o stránku pripravovaných služieb revízneho technika;
- kontakt k pripravovaným službám je dostupný priamo v hero bez falošného objednávania;
- používateľ začína svojou situáciou, nie technickou témou;
- Poradňa má nový vstup „Čo budete pri elektrorevízii riešiť?“ a situácie zákazníka;
- Glosár zostáva ľahko dostupný, ale odborné skratky LPS/RCD sa najprv vysvetlia v krátkom popovere a až potom ponúknu odkaz do Glosára;
- rovnaký zákaznícky kontakt sa objavuje na stránke Revízie a v detailoch Poradne;
- odborný obsah sa nemaže, iba sa posúva za praktickú zákaznícku cestu;
- komerčné služby zostávajú explicitne označené ako neprístupné / v príprave.

## Popovery pojmov

Na desktope sa krátke vysvetlenie môže ukázať pri hoveri; kliknutie/tap otvorí popover trvalo. Klávesnica používa tlačidlo s `aria-expanded`; po otvorení je dostupný samostatný odkaz „Podrobné vysvetlenie“ do Glosára. Samotný pojem už používateľa okamžite neodvedie zo zákazníckej stránky.

## MI 3102 BT

Stav zostáva pravdivý: Metrel MI 3102 BT EurotestXE je fyzicky k dispozícii, príslušenstvo bolo skontrolované a bolo overené zapnutie. Prototyp neuvádza reálne merania, výsledky ani tvrdenie o použití v praxi.

## Odporúčaný test

Testerovi nevysvetľovať účel webu. Po 5–10 sekundách sa opýtať: Čo sa tu pripravuje? Ako by ste sa ozvali? Kde by ste začali pri rekonštrukcii alebo kúpe domu? Čo urobíte, ak neviete, čo znamená LPS? Kde nájdete odborný detail?
