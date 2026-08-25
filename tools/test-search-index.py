#!/usr/bin/env python3
from pathlib import Path
import json,re,unicodedata,sys
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'data/search-index.json').read_text('utf8'))['records']

def norm(v=''):
 v=re.sub(r'i\s*[Δδ]\s*n',' idn ',str(v),flags=re.I).replace('Δ',' delta ').replace('δ',' delta ')
 v=re.sub(r'z\s*[_-]?\s*s',' zs ',v,flags=re.I).lower().replace('ľ','l').replace('ĺ','l').replace('ŕ','r')
 v=unicodedata.normalize('NFD',v); v=''.join(c for c in v if unicodedata.category(c)!='Mn')
 v=re.sub(r'[–—_\-/]+',' ',v); v=re.sub(r'[^a-z0-9\s.]+',' ',v); return re.sub(r'\s+',' ',v).strip()

def score(r,q):
 q=norm(q); title=norm(r['title']); summary=norm(r['summary']); body=norm(r['text']); aliases=[norm(x) for x in r.get('aliases',[])]; related=[norm(x) for x in r.get('relatedTerms',[])]; headings=[{**h,'norm':norm(h['text'])} for h in r.get('headings',[])]
 s=0; best=None; query_tokens=[x for x in q.split() if len(x)>1]
 if title==q:s=max(s,120)
 if q in aliases:s=max(s,100)
 if title.startswith(q) and title!=q:s=max(s,80)
 if any(a.startswith(q) and a!=q for a in aliases):s=max(s,70)
 for h in headings:
  hn=h['norm']
  if not hn: continue
  if hn==q:
   s=max(s,58); best=h
  elif q in hn or hn in q:
   if s<50: best=h
   s=max(s,50)
  elif len(query_tokens)>1 and all(x in hn for x in query_tokens):
   if s<50: best=h
   s=max(s,50)
 if q in summary:s=max(s,30)
 if any(t==q or q in t or t in q for t in related):s=max(s,20)
 if q in body:s=max(s,10)
 searchable=' '.join([title,summary,body,*aliases,*related,*[h['norm'] for h in headings]]); s+=min(sum(1 for x in query_tokens if x in searchable)*6,24)
 if (re.match(r'^(preco|co|co ak|potrebujem|ako|kedy|mozem|da sa)\b',q) or '?' in q) and r['type']=='poradna':s+=15
 if q.replace(' ','') in {'rcd','rccb','rcbo','zs','lps','pen','pe'} and r['type']=='kb':s+=15
 target=r['url'] + ('#'+best['id'] if best and '#' not in r['url'] else '')
 return s,target

def top(q):
 ranked=sorted(((score(r,q)[0],score(r,q)[1],r) for r in records), key=lambda x:(-x[0], 0 if x[2]['type']=='kb' else 1, x[2]['title']))
 return ranked[0] if ranked and ranked[0][0]>0 else (0,None,None)

tests={
 'RCD':'/glosar/rcd-prudovy-chranic/','prudovy chranic':'/glosar/rcd-prudovy-chranic/','prúdový chránič':'/glosar/rcd-prudovy-chranic/',
 'vypina chranic':'/poradna/prudovy-chranic-opakovane-vypina/','Zs':'/glosar/impedancia-poruchovej-slucky-zs/','poruchova slucka':'/glosar/impedancia-poruchovej-slucky-zs/','Zline':'/glosar/impedancia-poruchovej-slucky-zs/',
 'TN C':'/glosar/tn-c-tn-s-tn-c-s/','TN-C-S':'/glosar/tn-c-tn-s-tn-c-s/','PEN':'/glosar/pe-pen-ochranne-vodice/','LPS':'/glosar/lps-ochrana-pred-bleskom/','bleskozvod':'/glosar/lps-ochrana-pred-bleskom/',
 'kupa domu':'/poradna/revizia-pri-kupe-starsieho-domu-alebo-bytu/','revizna sprava':'/poradna/co-obsahuje-revizna-sprava/','rozvadzac':'/poradna/elektrikar-prerobil-rozvadzac-co-nasleduje/','izolacny odpor':'/glosar/izolacny-odpor/','cena':'/revizie/','telefon':'/#kontakt'
}
errors=[]
for q,expected in tests.items():
 s,target,r=top(q); got=r['url'] if r else None
 print(f'{q:22} -> {target if r else None} ({s})')
 if got!=expected: errors.append(f'{q!r}: expected {expected}, got {got}')

deep_tests={
 'TEST RCD':'/glosar/rcd-prudovy-chranic/#tlacidlo-test',
 'Zline':'/glosar/impedancia-poruchovej-slucky-zs/#zs-nie-je-zline',
 'Zs ≠ Zline':'/glosar/impedancia-poruchovej-slucky-zs/#zs-nie-je-zline',
 'IΔn':'/glosar/rcd-prudovy-chranic/',
 'trieda LPS':'/glosar/lps-ochrana-pred-bleskom/#trieda-lps',
}
for q,expected in deep_tests.items():
 s,target,r=top(q)
 print(f'{q:22} -> {target if r else None} ({s})')
 if target!=expected: errors.append(f'{q!r}: expected target {expected}, got {target}')

s,target,r=top('hlinik')
print(f'{"hlinik":22} -> {target if r else None} ({s})')
if r: errors.append(f"'hlinik' must not invent a dedicated result, got {r['url']}")
if errors:
 print('SEARCH SMOKE TEST FAILED')
 for e in errors:print('-',e)
 sys.exit(1)
print('SEARCH SMOKE TEST OK')
