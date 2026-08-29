#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json, re, unicodedata

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "search-index.json"

EXCLUDE_PATHS = {
    "/hladat/", "/obsah/", "/ochrana-sukromia/"
}

# `aliases` are normally alternate names for a topic. A very small set on
# /revizie/ (cena/cennik/objednat) is intentionally used as safe intent routing:
# it sends the user to the truthful service-status page instead of implying that
# a price list or active booking exists. `relatedTerms` remain weaker associations.
CURATED = {
    "/": {"aliases": ["bezpecna elektrika"], "relatedTerms": ["elektricka bezpecnost", "revizie", "meranie"]},
    "/poradna/": {"aliases": ["poradna", "otazky"], "relatedTerms": ["revizia", "elektrika"]},
    "/glosar/": {"aliases": ["glosar", "slovnik", "pojmy"], "relatedTerms": ["knowledge base", "technicke pojmy"]},
    "/podcast/": {"aliases": ["podcast", "bezpecna elektrika do usi"], "relatedTerms": ["be-001", "be-002", "be-003"]},
    "/novinky/": {"aliases": ["novinky", "co nove v elektro"], "relatedTerms": ["normy", "stn", "iec"]},
    "/metodika/": {"aliases": ["metodika", "zdroje"], "relatedTerms": ["normy", "ai", "overovanie"]},
    "/o-projekte/": {"aliases": ["o projekte", "autor", "lukas likavcan"], "relatedTerms": ["bezpecna elektrika", "e2a"]},
    "/revizie/": {
        "aliases": ["revizia", "elektrorevizia", "revizie", "e2a", "vychodzia revizia", "pravidelna revizia", "revizia domu", "revizia bytu", "cena revizie", "ako casto revizia", "revizia bleskozvodu", "cena", "cennik", "objednat"],
        "relatedTerms": ["kontrola elektroinstalacie", "revízny technik", "rodinny dom", "byt", "rozvadzac", "revizna sprava"],
        "summary": "Pripravované revízie v rozsahu E2A. Skúška je úspešne absolvovaná, čakám na osvedčenie a komerčné služby zatiaľ neposkytujem."
    },
    "/glosar/rcd-prudovy-chranic/": {
        "aliases": ["rcd", "prudovy chranic", "chranic"],
        "relatedTerms": ["rccb", "rcbo", "test chranica", "rezidualny prud", "residual current", "idn", "i-delta-n", "vypina chranic"]
    },
    "/glosar/rccb-vs-rcbo/": {
        "aliases": ["rccb", "rcbo", "rccb vs rcbo"],
        "relatedTerms": ["rcd", "prudovy chranic", "nadprudova ochrana"]
    },
    "/glosar/impedancia-poruchovej-slucky-zs/": {
        "aliases": ["zs", "impedancia poruchovej slucky", "poruchova slucka"],
        "relatedTerms": ["zline", "z line", "impedancia siete", "automaticke odpojenie", "poruchovy prud"]
    },
    "/glosar/tn-c-tn-s-tn-c-s/": {
        "aliases": ["tn-c", "tn-s", "tn-c-s", "tn c", "tn s", "tn c s"],
        "relatedTerms": ["pen", "pe", "ochranny vodic", "nulak"]
    },
    "/glosar/pe-pen-ochranne-vodice/": {
        "aliases": ["pe", "pen", "ochranny vodic", "ochranne vodice"],
        "relatedTerms": ["nulak", "tn-c", "tn-c-s", "pospajanie"]
    },
    "/glosar/lps-ochrana-pred-bleskom/": {
        "aliases": ["lps", "ochrana pred bleskom"],
        "relatedTerms": ["bleskozvod", "hromozvod", "spd", "trieda lps", "62305", "zachytavacia sustava", "zvod", "uzemnenie"]
    },
    "/glosar/uzemnenie/": {
        "aliases": ["uzemnenie", "zemnic"],
        "relatedTerms": ["odpor uzemnenia", "lps", "bleskozvod", "zemnenie"]
    },
    "/glosar/izolacny-odpor/": {
        "aliases": ["izolacny odpor", "riso"],
        "relatedTerms": ["izolacia", "meranie izolacie", "megaohm"]
    },
    "/poradna/hlinikova-elektroinstalacia/": {
        "aliases": ["hlinik", "hlinikova elektroinstalacia", "hlinikove rozvody"],
        "relatedTerms": ["stara elektroinstalacia", "al cu", "al/cu", "prechod al cu", "spoj al cu", "hlinik med", "med", "cu", "svorka", "spoj"]
    },
    "/poradna/prudovy-chranic-opakovane-vypina/": {
        "aliases": ["vypina chranic", "chranic vypina", "rcd vypina"],
        "relatedTerms": ["prudovy chranic", "test chranica", "porucha"]
    },
    "/poradna/revizia-pri-kupe-starsieho-domu-alebo-bytu/": {
        "aliases": ["kupa domu", "kupa bytu", "revizia pri kupe", "starsi dom", "starsia nehnutelnost"],
        "relatedTerms": ["technicky stav", "dokumentacia", "revizia domu"]
    },
    "/poradna/elektrikar-prerobil-rozvadzac-co-nasleduje/": {
        "aliases": ["prerobeny rozvadzac", "elektrikar prerobil rozvadzac", "rozvadzac"],
        "relatedTerms": ["rekonstrukcia", "overenie", "revizna sprava"]
    },
    "/poradna/revizia-po-rekonstrukcii/": {
        "aliases": ["revizia po rekonstrukcii", "rekonstrukcia"],
        "relatedTerms": ["byt", "dom", "rozvadzac"]
    },
    "/poradna/co-obsahuje-revizna-sprava/": {
        "aliases": ["co obsahuje revizna sprava", "revizna sprava"],
        "relatedTerms": ["dokumentacia", "vysledok revizie"]
    },
    "/poradna/co-pripravit-pred-reviziou/": {
        "aliases": ["co pripravit pred reviziou", "co treba k revizii", "priprava na reviziu", "dokumenty k revizii"],
        "relatedTerms": ["projektova dokumentacia", "predchadzajuca revizna sprava", "pristup k rozvadzacu", "zmeny elektroinstalacie"]
    },
    "/meranie/": {
        "aliases": ["meranie", "elektricke meranie", "merania"],
        "relatedTerms": ["izolacny odpor", "riso", "kontinuita", "unikajuci prud", "zs", "rcd"]
    },
}


def normalize(value: str) -> str:
    value = re.sub(r"i\s*[Δδ]\s*n", " idn ", value, flags=re.I)
    value = value.replace("Δ", " delta ").replace("δ", " delta ")
    value = re.sub(r"z\s*[_-]?\s*s", " zs ", value, flags=re.I)
    value = value.lower().replace("ľ", "l").replace("ĺ", "l").replace("ŕ", "r")
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    value = re.sub(r"[–—_\-/]+", " ", value)
    value = re.sub(r"[^a-z0-9\s.]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()

class PageParser(HTMLParser):
    SKIP_TAGS = {"script","style","noscript","nav","footer","button"}
    SKIP_CLASSES = {"conversion-inline","consent-banner","mobile-bottom-nav","site-footer","advice-contact-cta"}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.skip_depth=0; self.in_main=False; self.main_depth=0
        self.h1=[]; self.headings=[]; self.current_h2=None; self.current_h2_id=None
        self.text=[]; self.meta_description=""; self.canonical=""; self.status_capture=None; self.status_text=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); classes=set((a.get("class") or "").split())
        self.stack.append((tag,a))
        if tag=="main": self.in_main=True; self.main_depth=len(self.stack)
        if tag in self.SKIP_TAGS or classes & self.SKIP_CLASSES: self.skip_depth += 1
        if tag=="meta" and a.get("name")=="description": self.meta_description=a.get("content","")
        if tag=="link" and a.get("rel")=="canonical": self.canonical=a.get("href","")
        if self.in_main and self.skip_depth==0 and tag=="h1": self.h1.append("")
        if self.in_main and self.skip_depth==0 and tag=="h2":
            target=a.get("id")
            if not target:
                for parent_tag,parent_attrs in reversed(self.stack[:-1]):
                    if parent_tag in {"section","aside","article"} and parent_attrs.get("id"):
                        target=parent_attrs["id"]; break
            self.current_h2=""; self.current_h2_id=target
        if self.in_main and self.skip_depth==0 and "status-banner" in classes and self.status_capture is None:
            self.status_capture=len(self.stack); self.status_text=[]
    def handle_endtag(self, tag):
        if self.current_h2 is not None and tag=="h2":
            text=re.sub(r"\s+"," ",self.current_h2).strip()
            if text and self.current_h2_id: self.headings.append({"id":self.current_h2_id,"text":text})
            self.current_h2=None; self.current_h2_id=None
        if self.status_capture is not None and len(self.stack)==self.status_capture and self.stack[-1][0]==tag:
            self.status_capture=-1
        if tag in self.SKIP_TAGS or (self.stack and set((self.stack[-1][1].get("class") or "").split()) & self.SKIP_CLASSES):
            self.skip_depth=max(0,self.skip_depth-1)
        if tag=="main": self.in_main=False
        if self.stack: self.stack.pop()
    def handle_data(self, data):
        if not self.in_main or self.skip_depth: return
        clean=re.sub(r"\s+"," ",data).strip()
        if not clean: return
        if self.h1 and not self.text and self.current_h2 is None: # h1 may still be open; harmless fallback below
            pass
        if self.stack and self.stack[-1][0]=="h1":
            if not self.h1: self.h1.append(clean)
            else: self.h1[-1]+= (" " if self.h1[-1] else "")+clean
        if self.current_h2 is not None:
            self.current_h2 += (" " if self.current_h2 else "") + clean
        if self.status_capture and self.status_capture != -1:
            self.status_text.append(clean)
        self.text.append(clean)


def page_type(path: str) -> str:
    if path.startswith("/poradna/") and path != "/poradna/": return "poradna"
    if path.startswith("/glosar/") and path != "/glosar/": return "kb"
    if path.startswith("/novinky/2026/"): return "novinka"
    if path == "/podcast/": return "podcast"
    if path == "/meranie/": return "meranie"
    if path == "/metodika/": return "metodika"
    return "hub"

def stable_id(path: str, typ: str) -> str:
    if path=="/": return "hub-home"
    slug=path.strip("/").split("/")[-1]
    return f"{typ}-{slug}"

def truncate(text: str, limit=180) -> str:
    text=re.sub(r"\s+"," ",text).strip()
    if len(text)<=limit: return text
    cut=text[:limit].rsplit(" ",1)[0]
    return cut.rstrip(".,;:") + "…"

records=[]
for p in sorted(ROOT.rglob("*.html")):
    rel=p.relative_to(ROOT).as_posix()
    if rel=="404.html": continue
    parser=PageParser(); raw=p.read_text(encoding="utf-8"); parser.feed(raw)
    if not parser.canonical: continue
    path=urlparse(parser.canonical).path or "/"
    if path in EXCLUDE_PATHS: continue
    if "noindex" in raw.lower(): continue
    title=" ".join(parser.h1).strip()
    if not title:
        m=re.search(r"<title>(.*?)</title>",raw,re.S|re.I); title=re.sub(r"<.*?>","",m.group(1)).strip() if m else path
    status=" ".join(parser.status_text) if parser.status_text else ""
    status=re.sub(r"^Stručne:\s*","",status,flags=re.I)
    curated=CURATED.get(path,{})
    summary=truncate(curated.get("summary") or status or parser.meta_description or " ".join(parser.text)[:250])
    typ=page_type(path)
    updated=""
    m=re.search(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})"',raw)
    if m: updated=m.group(1)
    records.append({
        "id": stable_id(path,typ),
        "url": path,
        "title": title,
        "type": typ,
        "summary": summary,
        "aliases": sorted({normalize(x) for x in curated.get("aliases",[]) if normalize(x)}),
        "relatedTerms": sorted({normalize(x) for x in curated.get("relatedTerms",[]) if normalize(x)}),
        "headings": parser.headings,
        "text": truncate(" ".join(parser.text), 6000),
        "updated": updated
    })

# One helpful anchored record for contact. It is an existing section of the homepage, not a new content page.
records.append({
    "id":"hub-kontakt","url":"/#kontakt","title":"Kontakt k pripravovaným revíznym službám","type":"hub",
    "summary":"Kontakt na projekt Bezpečná elektrika. Revízne služby sú zatiaľ v príprave.",
    "aliases":["email","kontakt"],"relatedTerms":["adresa","telefon"],"headings":[],"text":"kontakt pripravovane revizne sluzby bezpecna elektrika", "updated":"2026-08-25"
})

records.sort(key=lambda r:(r["type"],r["title"].lower()))
payload={"version":1,"generated":max((r.get("updated") or "" for r in records),default="2026-08-25"),"records":records}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"SEARCH INDEX OK · {len(records)} records · {OUT.relative_to(ROOT)}")
