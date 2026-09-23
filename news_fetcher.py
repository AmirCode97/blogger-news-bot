"""Fetch only configured sources, with RSS/API fallbacks and current selectors."""
import hashlib
import json
import os
import re
from itertools import zip_longest
from urllib.parse import urljoin, urlsplit
import feedparser
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import NEWS_SOURCES, USE_PROXY, PROXY_URL
from article_utils import atomic_json, canonical_url, parse_datetime, plain_article_text, utc_now
from article_images import article_image_candidates, verified_image

def safe_print(value):
    print(re.sub(r'(https?://)[^:@/]+:[^:@/]+@', r'\1***:***@', str(value)))

def _is_ok_response(response):
    return response is not None and response.status_code == 200

class NewsFetcher:
    def __init__(self, cache_file='news_cache.json'):
        self.cache_file = cache_file
        self.seen_ids, self.seen_titles = set(), set()
        if os.path.exists(cache_file):
            with open(cache_file, encoding='utf-8') as stream:
                data = json.load(stream)
            self.seen_ids = set(data.get('seen_ids', []))
            self.seen_titles = set(data.get('seen_titles', []))
        self.source_health = []
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (compatible; BloggerNewsBot/2.0)'
        retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                      allowed_methods=['GET'], respect_retry_after_header=True)
        self.session.mount('https://', HTTPAdapter(max_retries=retry))
        self.cf_session = None

    def _save_cache(self):
        atomic_json(self.cache_file, {'seen_ids': sorted(self.seen_ids), 'seen_titles': sorted(self.seen_titles)})

    def _generate_news_id(self, title, link):
        # Retain compatibility with the pre-upgrade cache.
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        return hashlib.md5(f'{clean_title}_{link}'.encode()).hexdigest()

    def is_duplicate(self, title, news_id):
        return news_id in self.seen_ids or title in self.seen_titles

    def mark_as_seen(self, title, news_id):
        self.seen_ids.add(news_id)
        self.seen_titles.add(title)
        self._save_cache()

    def _make_request(self, url, use_proxy=True, timeout=25):
        proxies = {'http': PROXY_URL, 'https': PROXY_URL} if USE_PROXY and PROXY_URL and use_proxy else None
        response = None
        try:
            response = self.session.get(url, timeout=timeout, proxies=proxies)
            if response.status_code not in (403, 503):
                return response
        except requests.RequestException as exc:
            safe_print(f'[HTTP] {urlsplit(url).hostname}: {type(exc).__name__}')
        try:
            if self.cf_session is None:
                import cloudscraper
                self.cf_session = cloudscraper.create_scraper()
            response = self.cf_session.get(url, timeout=timeout, proxies=proxies)
        except (ImportError, requests.RequestException) as exc:
            safe_print(f'[HTTP fallback] {urlsplit(url).hostname}: {type(exc).__name__}')
        return response

    def _item(self, source, title, link, description='', published=None, image=None, full=False):
        title = BeautifulSoup(title or '', 'html.parser').get_text(' ', strip=True)
        original_link = urljoin(source['url'], link or '')
        link = canonical_url(original_link)
        if not link or urlsplit(link).hostname != urlsplit(canonical_url(source['url'])).hostname or len(title) < 8:
            return None
        legacy_links = {original_link, link}
        if not urlsplit(link).query:
            legacy_links.add(link.rstrip('/') + '/')
        if title in self.seen_titles or any(self._generate_news_id(title, u) in self.seen_ids for u in legacy_links):
            return None
        date = parse_datetime(published)
        return {'id': self._generate_news_id(title, link), 'title': title, 'link': link,
                'description': plain_article_text(description), 'source': source['name'],
                'source_category': source.get('category', 'حقوق بشر'), 'language': source.get('language', 'fa'),
                'published': date.isoformat() if date else None, 'fetched_at': utc_now().isoformat(),
                'image_url': image, 'has_full_content': full}

    def fetch_from_rss(self, source):
        response = self._make_request(source.get('rss_url') or source['rss_fallback'])
        if not _is_ok_response(response):
            raise RuntimeError(f'RSS HTTP {response.status_code if response is not None else "network error"}')
        feed = feedparser.parse(response.content)
        if not feed.entries:
            raise RuntimeError('RSS returned no entries (possibly an HTML block page)')
        items = []
        for entry in feed.entries:
            full = entry.get('content', [])
            body = full[0].get('value', '') if full else entry.get('summary', '')
            media = entry.get('media_content') or entry.get('media_thumbnail') or [{}]
            item = self._item(source, entry.get('title'), entry.get('link'), body,
                              entry.get('published') or entry.get('updated'), media[0].get('url'), bool(full))
            if item:
                items.append(item)
        return items

    def fetch_from_wordpress(self, source):
        response = self._make_request(source['api_url'])
        if not _is_ok_response(response):
            raise RuntimeError(f'WordPress HTTP {response.status_code if response is not None else "network error"}')
        posts = response.json()
        if not isinstance(posts, list) or not posts:
            raise RuntimeError('WordPress returned no posts')
        items = []
        for post in posts:
            media = post.get('_embedded', {}).get('wp:featuredmedia', [{}])
            image = media[0].get('source_url') if media else None
            item = self._item(source, post.get('title', {}).get('rendered'), post.get('link'),
                              post.get('content', {}).get('rendered'),
                              (post.get('date_gmt') or '') + 'Z', image, True)
            if item:
                items.append(item)
        return items

    def fetch_from_scrape(self, source):
        response = self._make_request(source['url'])
        if not _is_ok_response(response):
            raise RuntimeError(f'Listing HTTP {response.status_code if response is not None else "network error"}')
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.select(source.get('selectors', {}).get('articles', 'article'))
        items, links = [], set()
        found = 0
        for article in articles:
            title = article.select_one('.entry-title a, .jeg_post_title a, h2 a, h3 a, h4 a')
            if not title:
                continue
            link = canonical_url(urljoin(source['url'], title.get('href', '')))
            if link in links:
                continue
            links.add(link)
            found += 1
            date = article.select_one('time[datetime]')
            image = article.select_one('img')
            item = self._item(source, title.get_text(' ', strip=True), link, '',
                              date.get('datetime') if date else None,
                              urljoin(source['url'], image.get('data-src') or image.get('src') or '') if image else None)
            if item:
                items.append(item)
        if not found:
            raise RuntimeError('Listing contained no recognizable article links')
        return items

    def fetch_all_news(self, max_items=20):
        groups = []
        self.source_health = []
        for source in NEWS_SOURCES:
            if not source.get('enabled', True):
                continue
            methods = []
            if source.get('api_url'):
                methods.append(self.fetch_from_wordpress)
            if source.get('rss_url') or source.get('rss_fallback'):
                methods.append(self.fetch_from_rss)
            methods.append(self.fetch_from_scrape)
            errors, items, successful = [], [], False
            for method in methods:
                try:
                    items = method(source)
                    successful = True
                    break
                except (requests.RequestException, ValueError, RuntimeError) as exc:
                    errors.append(str(exc))
            unique = {item['link']: item for item in items}
            items = sorted(unique.values(), key=lambda x: x.get('published') or '', reverse=True)
            groups.append(items[:source.get('max_items', 5)])
            health = {'source': source['name'], 'ok': successful, 'new_candidates': len(unique), 'errors': errors}
            self.source_health.append(health)
            safe_print('[SOURCE] ' + json.dumps(health, ensure_ascii=False))
        combined, seen = [], set()
        for row in zip_longest(*groups):
            for item in row:
                if item and item['link'] not in seen:
                    combined.append(item)
                    seen.add(item['link'])
        return combined[:max_items]

    def fetch_full_article(self, url, source_name=''):
        response = self._make_request(url)
        if not _is_ok_response(response):
            return {'success': False, 'full_content': '', 'main_image': None, 'published': None}
        soup = BeautifulSoup(response.content, 'html.parser')
        container = soup.select_one('.single-post-content, .entry-content, .td-post-content, .content-inner, article.single, .post-content, article')
        body = plain_article_text(str(container)) if container else ''
        if not body:
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    data = json.loads(script.string or '')
                    nodes = data.get('@graph', [data]) if isinstance(data, dict) else data
                    for node in nodes:
                        if isinstance(node, dict) and node.get('articleBody'):
                            body = plain_article_text(node['articleBody'])
                            break
                except (ValueError, TypeError):
                    continue
        images = article_image_candidates(soup, url)
        date = soup.select_one('meta[property="article:published_time"], meta[name="date"], time[datetime]')
        published = parse_datetime(date.get('content') or date.get('datetime')) if date else None
        return {'success': len(body) >= 150, 'full_content': body,
                'main_image': images[0] if images else None, 'image_candidates': images,
                'published': published.isoformat() if published else None}

    def resolve_article_image(self, item, full):
        candidates = full.get('image_candidates') or [full.get('main_image'), item.get('image_url')]
        candidates = [url for url in candidates if url]
        if not candidates:
            # RSS/WordPress may supply full text without featured media.
            detail = self.fetch_full_article(item['link'], item.get('source', ''))
            candidates = detail.get('image_candidates') or [detail.get('main_image')]
        return verified_image(candidates, self.session)
