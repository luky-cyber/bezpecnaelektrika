# v0.6.4 – Stability & consent hardening

Dátum: 01. 09. 2026

## Zmeny
- Consent logika oddeľuje jednorazové načítanie GA4 skriptu od každej zmeny `granted`/`denied`, takže cyklus povoliť → odmietnuť → znovu povoliť funguje aj bez reloadu stránky.
- `localStorage` pre tému aj súhlas je chránený `try/catch`; pri zablokovanom úložisku zostáva web funkčný a analytika sa predvolene nepovolí.
- Pri odvolaní analytiky sa odošle `analytics_storage: denied` a dostupné first-party `_ga*` cookies sa best-effort odstránia.
- Interný search drží používateľsky užitočné `?q=` URL, ale GA4 dostáva redigovaný `page_location` a redigovaný interný `page_referrer`; pred `history.replaceState` sa nastaví bezpečná analytická URL.
- Search scoring už nepridáva Poradňa/KB intent bonus bez reálnej vecnej zhody. Negatívne dopyty typu `ako xyzqwerty` vracajú nulu a zamietnutý fetch indexu sa dá pri ďalšom pokuse zopakovať.
- Viditeľný odkaz na osobný profil používa `https://likavcan.cz/lukas/`; stabilné Person `@id` `https://likavcan.cz/lukas/#lukas-likavcan` zostáva nezmenené v structured data.
- Podcastové karty používajú presnú akciu `Vybrať epizódu`; samotné prehrávanie ostáva na hlavnom Play tlačidle. Chyba načítania/prehrávania audia sa zobrazí používateľovi, nie iba v konzole.
- README je zosúladený s aktuálnym stavom: E2A skúška absolvovaná, osvedčenie vydané, komerčné služby ešte nespustené.
- `_config.yml` oddeľuje verejný GitHub Pages povrch od repo-only `docs/`, `tools/` a Markdown release/prototype dokumentácie.
- Verejný `/version.json` poskytuje jednoduchý deployment fingerprint pre production smoke test.
- `validate-release.py` spúšťa vnorený search smoke test v UTF-8 aj na Windows, takže znak `≠` už nespôsobí falošný fail cez CP1250 subprocess.
- Mobilný hamburger už neopakuje utility odkazy `Zdroje a metodika` a `Mapa obsahu`; zostávajú dostupné v pätičke a v desktopovom menu `Odborný obsah`.
- QR kontakt na stránke O mne je na úzkych displejoch väčší a skladá sa pod kontaktné údaje pre jednoduchšie skenovanie.
- Na touch/coarse zariadeniach prvý tap mimo otvoreného term popoveru iba zavrie vysvetlenie a neaktivuje odkaz alebo ovládací prvok pod tapom; iný odborný termín sa môže otvoriť priamo.
- Verejné ovládacie prvky na kopírovanie odkazov na sekcie/články a súvisiaci toast boli odstránené; stabilné HTML `id` a existujúce fragmentové deep linky zostávajú zachované.
- `llms.txt` je stručne zosúladený so stavom kvalifikácie: E2A skúška absolvovaná, osvedčenie vydané, komerčné revízne služby zatiaľ nespustené.

## Scope guardrails
- Bez nového obsahu Poradne, Glosára alebo Noviniek.
- Bez verejných podcast transcriptov a bez nových URL epizód; tie patria do samostatného content/accessibility passu.
- Bez zmeny sitemap `lastmod` a obsahových `dateModified`, pretože release je technický hardening.
- Bez regiónu služby, cien, telefónu, LocalBusiness/Electrician/Service/Offer schema alebo iného Commercial Switch prvku.
- Bez CSS consolidation/redesignu.

## Overenie pred vydaním
- `python tools/build-css.py --check`
- `python tools/test-search-index.py`
- `python tools/validate-release.py`
- `python tools/validate-v060.py`
- `python tools/validate-v062.py`
- `python tools/validate-v063.py`
- `python tools/validate-v064.py`
- manuálne: consent grant → deny → grant + reload, `/hladat/?q=RCD` GA payload, blocked-storage fallback, podcast error/selection semantics a `/version.json` po deployi.
