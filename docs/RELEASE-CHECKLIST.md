# Release checklist

1. Spustiť `python tools/validate-release.py`.
2. Overiť, že `index.html` a `CNAME` sú priamo v koreňovom adresári.
3. Otestovať homepage, Revízie, Podcast, Meranie, consent a footer cez Live Server.
4. V produkcii otestovať BE-001 aj BE-002 a prepnutie epizódy: po prepnutí musí byť tlačidlo Play, nie Pause.
5. Po pushi overiť GitHub Pages pred vytvorením tagu/releasu.
