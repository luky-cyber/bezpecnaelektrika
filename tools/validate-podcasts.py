#!/usr/bin/env python3
"""Generic integrity checks for all published Bezpečná elektrika podcast episodes."""
from pathlib import Path
from bs4 import BeautifulSoup
import json, re, sys, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://bezpecnaelektrika.sk'
errors = []

def iso_duration(mmss: str) -> str:
    m, s = [int(x) for x in mmss.split(':', 1)]
    return f'PT{m}M{s}S'

def jsonld_nodes(raw: str):
    soup = BeautifulSoup(raw, 'html.parser')
    nodes = []
    for sc in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(sc.string or '')
        except Exception:
            continue
        if isinstance(data, dict) and isinstance(data.get('@graph'), list):
            nodes.extend(data['@graph'])
        elif isinstance(data, dict):
            nodes.append(data)
    return nodes

try:
    pdata = json.loads((ROOT / 'data/podcasts.json').read_text(encoding='utf-8'))
    episodes = [e for e in pdata.get('episodes', []) if e.get('published')]
except Exception as e:
    print('PODCAST CHECK FAILED\n - data/podcasts.json: ' + str(e))
    raise SystemExit(1)
if not episodes:
    errors.append('No published podcast episodes found')
ids = [e.get('id') for e in episodes]
if len(ids) != len(set(ids)):
    errors.append('Duplicate podcast episode IDs in data/podcasts.json')
if sum(1 for e in episodes if e.get('featured')) > 1:
    errors.append('More than one published podcast episode is featured')

# RSS lookup.
try:
    tree = ET.parse(ROOT / 'podcast/feed.xml')
    channel = tree.getroot().find('channel')
    rss_items = {}
    for item in channel.findall('item') if channel is not None else []:
        guid = item.findtext('guid') or ''
        rss_items[guid.strip()] = item
except Exception as e:
    rss_items = {}
    errors.append(f'RSS parse failed: {e}')

sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
content_map = (ROOT / 'obsah/index.html').read_text(encoding='utf-8')
llms = (ROOT / 'llms.txt').read_text(encoding='utf-8')
search = json.loads((ROOT / 'data/search-index.json').read_text(encoding='utf-8')).get('records', [])
search_urls = {x.get('url') for x in search}
hub = (ROOT / 'podcast/index.html').read_text(encoding='utf-8')
hub_nodes = jsonld_nodes(hub)

ITUNES = '{http://www.itunes.com/dtds/podcast-1.0.dtds}'
# Existing feed uses a namespace URI without /dtds in ElementTree depending on parser input.
ITUNES_ALT = '{http://www.itunes.com/dtds/podcast-1.0.dtd}'

def itunes_text(item, local):
    for ns in (ITUNES, ITUNES_ALT):
        el = item.find(ns + local)
        if el is not None and el.text:
            return el.text.strip()
    # Namespace fallback for future feed namespace changes.
    for el in list(item):
        if el.tag.endswith('}' + local) and el.text:
            return el.text.strip()
    return None

for ep in episodes:
    eid = ep.get('id') or ''
    page = ep.get('page') or ''
    title = ep.get('title') or ''
    audio = ep.get('audio') or ''
    duration = ep.get('duration') or ''
    m = re.fullmatch(r'BE-(\d{3})', eid)
    if not m:
        errors.append(f'Invalid episode ID: {eid!r}')
        continue
    number = int(m.group(1))
    if not re.fullmatch(r'\d+:\d{2}', duration):
        errors.append(f'{eid} invalid duration: {duration!r}')
        continue
    if not page.startswith('/podcast/') or not page.endswith('/'):
        errors.append(f'{eid} invalid page path: {page!r}')
        continue
    p = ROOT / page.lstrip('/') / 'index.html'
    if not p.is_file():
        errors.append(f'{eid} page missing: {page}')
        continue
    raw = p.read_text(encoding='utf-8')
    soup = BeautifulSoup(raw, 'html.parser')
    h1 = soup.find('h1')
    if not h1 or h1.get_text(' ', strip=True) != title:
        errors.append(f'{eid} H1/title mismatch')
    for needle in [audio, 'Gemini Notebook', 'id="prepis"', 'id="odborne-spresnenia"', 'id="zdroje"']:
        if needle not in raw:
            errors.append(f'{eid} page integrity marker missing: {needle}')
    nodes = jsonld_nodes(raw)
    pe = next((x for x in nodes if x.get('@type') == 'PodcastEpisode'), None)
    ao = next((x for x in nodes if x.get('@type') == 'AudioObject'), None)
    if not pe:
        errors.append(f'{eid} PodcastEpisode JSON-LD missing')
    else:
        if pe.get('episodeNumber') != number:
            errors.append(f'{eid} episodeNumber mismatch: {pe.get("episodeNumber")}')
        if pe.get('duration') != iso_duration(duration):
            errors.append(f'{eid} PodcastEpisode duration mismatch')
    if not ao:
        errors.append(f'{eid} AudioObject JSON-LD missing')
    else:
        if ao.get('contentUrl') != audio:
            errors.append(f'{eid} AudioObject URL mismatch')
        if ao.get('encodingFormat') != 'audio/mpeg':
            errors.append(f'{eid} AudioObject encodingFormat mismatch')
        if ao.get('duration') and ao.get('duration') != iso_duration(duration):
            errors.append(f'{eid} AudioObject duration mismatch')

    guid = 'bezpecnaelektrika-' + eid.lower()
    item = rss_items.get(guid)
    if item is None:
        errors.append(f'{eid} RSS item missing ({guid})')
    else:
        expected_link = BASE + page
        if (item.findtext('link') or '').strip() != expected_link:
            errors.append(f'{eid} RSS link mismatch')
        enclosure = item.find('enclosure')
        if enclosure is None or enclosure.get('url') != audio or enclosure.get('type') != 'audio/mpeg':
            errors.append(f'{eid} RSS enclosure mismatch')
        rss_duration = itunes_text(item, 'duration')
        if rss_duration != duration:
            errors.append(f'{eid} RSS duration mismatch: {rss_duration!r}')
        rss_number = itunes_text(item, 'episode')
        if rss_number != str(number):
            errors.append(f'{eid} RSS episode number mismatch: {rss_number!r}')
        if ao and enclosure is not None and ao.get('contentSize') and enclosure.get('length') != str(ao.get('contentSize')):
            errors.append(f'{eid} RSS length / AudioObject contentSize mismatch')

    full_page = BASE + page
    if full_page not in sitemap:
        errors.append(f'{eid} missing from sitemap')
    if page not in search_urls:
        errors.append(f'{eid} missing from search index')
    if page not in content_map:
        errors.append(f'{eid} missing from content map')
    if page in llms:
        errors.append(f'{eid} individual URL must not be enumerated in concise llms.txt')
    hub_id = full_page + '#episode'
    hub_ep = next((x for x in hub_nodes if x.get('@type') == 'PodcastEpisode' and x.get('@id') == hub_id), None)
    if not hub_ep:
        errors.append(f'{eid} PodcastEpisode missing from podcast hub JSON-LD')
    else:
        media = hub_ep.get('associatedMedia') or {}
        if media.get('contentUrl') != audio:
            errors.append(f'{eid} podcast hub audio URL mismatch')

if len(rss_items) != len(episodes):
    errors.append(f'RSS item count {len(rss_items)} != published episode count {len(episodes)}')

if errors:
    print('PODCAST CHECK FAILED')
    for e in sorted(set(errors)):
        print(' -', e)
    raise SystemExit(1)
print(f'PODCAST CHECK OK · {len(episodes)} published episodes · page/audio/schema/RSS/search/sitemap/content-map integrity')
