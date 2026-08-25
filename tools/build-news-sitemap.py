#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import argparse, json, re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'news-sitemap.xml'
PUBLICATION_NAME='Bezpečná elektrika'
LANGUAGE='sk'
WINDOW=timedelta(days=2)
NS_SM='http://www.sitemaps.org/schemas/sitemap/0.9'
NS_NEWS='http://www.google.com/schemas/sitemap-news/0.9'
ET.register_namespace('',NS_SM); ET.register_namespace('news',NS_NEWS)

def parse_iso_datetime(value):
    if not value or 'T' not in value: return None
    try: dt=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError: return None
    return dt if dt.tzinfo is not None else None

def canonical_from_html(text):
    m=re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']|<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']',text,re.I)
    return (m.group(1) or m.group(2)) if m else None

def jsonld_graphs(text):
    for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',text,re.S|re.I):
        try: data=json.loads(m.group(1))
        except Exception: continue
        if isinstance(data,dict): yield data

def build(as_of):
    if as_of.tzinfo is None: raise ValueError('--as-of must include a timezone')
    as_of_utc=as_of.astimezone(timezone.utc); eligible=[]
    for path in sorted((ROOT/'novinky').glob('[0-9][0-9][0-9][0-9]/*/index.html')):
        text=path.read_text(encoding='utf-8'); canonical=canonical_from_html(text)
        for data in jsonld_graphs(text):
            nodes=data.get('@graph',[])
            for node in nodes if isinstance(nodes,list) else []:
                if not isinstance(node,dict) or node.get('@type')!='NewsArticle': continue
                published=parse_iso_datetime(str(node.get('datePublished','')))
                if not published: continue
                age=as_of_utc-published.astimezone(timezone.utc)
                if age<timedelta(0) or age>WINDOW: continue
                url=canonical or node.get('url'); headline=str(node.get('headline','')).strip()
                if not url or not headline: continue
                parsed=urlparse(url)
                if parsed.scheme!='https' or parsed.netloc!='bezpecnaelektrika.sk': continue
                eligible.append({'url':url,'published':published.isoformat(),'headline':headline})
    return eligible

def write_sitemap(items):
    if not items:
        if OUT.exists(): OUT.unlink()
        print('NEWS SITEMAP OK · 0 eligible articles · no file written'); return
    root=ET.Element(ET.QName(NS_SM,'urlset'))
    for item in items:
        url=ET.SubElement(root,ET.QName(NS_SM,'url')); ET.SubElement(url,ET.QName(NS_SM,'loc')).text=item['url']
        news=ET.SubElement(url,ET.QName(NS_NEWS,'news')); pub=ET.SubElement(news,ET.QName(NS_NEWS,'publication'))
        ET.SubElement(pub,ET.QName(NS_NEWS,'name')).text=PUBLICATION_NAME
        ET.SubElement(pub,ET.QName(NS_NEWS,'language')).text=LANGUAGE
        ET.SubElement(news,ET.QName(NS_NEWS,'publication_date')).text=item['published']
        ET.SubElement(news,ET.QName(NS_NEWS,'title')).text=item['headline']
    tree=ET.ElementTree(root); ET.indent(tree,space='  '); tree.write(OUT,encoding='utf-8',xml_declaration=True)
    print(f'NEWS SITEMAP OK · {len(items)} eligible article(s)')

def main():
    ap=argparse.ArgumentParser(description='Build Google News sitemap from true NewsArticle pages published in the last two days.')
    ap.add_argument('--as-of',help='ISO 8601 reference time with timezone; defaults to current UTC time.')
    args=ap.parse_args(); as_of=datetime.fromisoformat(args.as_of.replace('Z','+00:00')) if args.as_of else datetime.now(timezone.utc)
    write_sitemap(build(as_of))
if __name__=='__main__': main()
