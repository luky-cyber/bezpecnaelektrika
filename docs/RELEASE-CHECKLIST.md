# Release checklist

1. Spustiť `python tools/validate-release.py`.
2. Overiť, že `index.html` a `CNAME` sú priamo v koreňovom adresári.
3. Otestovať homepage, Revízie, Podcast, Meranie, consent a footer cez Live Server.
4. V produkcii otestovať BE-001, BE-002 aj BE-003 a prepnutie epizódy: po prepnutí musí byť tlačidlo Play, nie Pause.
5. Overiť `/robots.txt`: OAI-SearchBot = Allow, GPTBot = Disallow.
6. V Cloudflare skontrolovať, že OAI-SearchBot nedostáva blokáciu/WAF challenge.
7. Skontrolovať homepage kontakt, CTA na hlbších stránkach a mobilnú navigáciu Metodiky.
8. Po pushi overiť GitHub Pages pred vytvorením tagu/releasu.
