#!/usr/bin/env python3
from pathlib import Path
import argparse,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'config/release.json'
MARK_RE=re.compile(r'<div class="container footer-release" data-release-version="[^"]+">.*?</div>',re.S)
OLD_COPY='<p>© 2026 Bezpečná elektrika</p>'

def load():
    data=json.loads(CFG.read_text(encoding='utf-8'))
    need=['project','version','release','channel','date','fingerprint','commercialState']
    missing=[k for k in need if not data.get(k)]
    if missing: raise SystemExit('Missing release keys: '+', '.join(missing))
    return data

def marker(data):
    rel=data['release']
    return (f'<div class="container footer-release" data-release-version="{rel}">' 
            f'<span>© 2026 Bezpečná elektrika</span><span aria-hidden="true">·</span>'
            f'<a aria-label="Informácie o verzii {rel}" href="/version.json">{rel}</a></div>')

def sync_html(data,check=False):
    want=marker(data); changed=[]; errors=[]
    for p in sorted(ROOT.rglob('*.html')):
        if any(x in p.parts for x in ('.build',)):
            continue
        raw=p.read_text(encoding='utf-8')
        new=raw.replace(OLD_COPY,'')
        if MARK_RE.search(new):
            new=MARK_RE.sub(want,new)
        elif '</footer>' in new:
            new=new.replace('</footer>',want+'</footer>',1)
        elif '</body>' in new:
            footer='<footer class="site-footer">'+want+'</footer>'
            new=new.replace('</body>',footer+'</body>',1)
        else:
            errors.append(f'No body/footer target: {p.relative_to(ROOT)}'); continue
        if check:
            if new!=raw: errors.append(f'Release identity stale: {p.relative_to(ROOT)}')
        elif new!=raw:
            p.write_text(new,encoding='utf-8'); changed.append(str(p.relative_to(ROOT)))
    return changed,errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
    data=load()
    public={k:data[k] for k in ['project','version','release','channel','date','fingerprint','commercialState']}
    want=json.dumps(public,ensure_ascii=False,indent=2)+'\n'
    vp=ROOT/'version.json'
    errors=[]
    if args.check:
        if not vp.exists() or vp.read_text(encoding='utf-8')!=want: errors.append('version.json is stale')
    else: vp.write_text(want,encoding='utf-8')
    changed,html_errors=sync_html(data,args.check); errors.extend(html_errors)
    if errors:
        print('RELEASE IDENTITY CHECK FAILED'); [print(' -',e) for e in errors]; return 1
    print(('RELEASE IDENTITY CHECK OK' if args.check else 'RELEASE IDENTITY SYNC OK')+f" · {data['release']} · {len(changed)} HTML updated")
    return 0
if __name__=='__main__': raise SystemExit(main())
