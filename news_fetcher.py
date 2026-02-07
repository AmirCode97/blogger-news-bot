
import random
import sys
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
import json
import os
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin

# Import config
from config import NEWS_SOURCES, FILTER_KEYWORDS, USE_PROXY, PROXY_URL, FREE_PROXIES

def safe_print(text):
    try:
        print(text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    except:
        print(text.encode('utf-8', errors='replace').decode('utf-8'))

class NewsFetcher:
    def __init__(self):
        self.cache_file = "news_cache.json"
        self.seen_ids = set()
        self.seen_titles = set()
        self._load_cache()
        self.seen_news = self.seen_ids
        self.current_proxy = None
        self._setup_session()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.seen_ids = set(data.get('seen_ids', []))
                    self.seen_titles = set(data.get('seen_titles', []))
            except: pass

    def _save_cache(self):
        data = {
            'seen_ids': list(self.seen_ids),
            'seen_titles': list(self.seen_titles)
        }
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def _generate_news_id(self, title: str, link: str) -> str:
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        unique_string = f"{clean_title}_{link}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def is_duplicate(self, title: str, news_id: str) -> bool:
        return news_id in self.seen_ids or title in self.seen_titles

    def mark_as_seen(self, title: str, news_id: str):
        self.seen_ids.add(news_id)
        self.seen_titles.add(title)
        self._save_cache()

    def _setup_session(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        })

    def _get_proxy(self) -> Optional[Dict]:
        if not USE_PROXY: return None
        if PROXY_URL: return {'http': PROXY_URL, 'https': PROXY_URL}
        if FREE_PROXIES:
            proxy = random.choice(FREE_PROXIES)
            self.current_proxy = proxy
            return {'http': proxy, 'https': proxy}
        return None

    def _make_request(self, url: str, use_proxy: bool = False, timeout: int = 30) -> Optional[requests.Response]:
        proxies = self._get_proxy() if use_proxy else None
        if proxies:
            try:
                response = self.session.get(url, proxies=proxies, timeout=timeout, verify=False)
                response.raise_for_status()
                return response
            except: pass
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except: return None

    def fetch_from_rss(self, source: dict) -> List[Dict]:
        news_items = []
        url = source.get('rss_url', source.get('url'))
        try:
            safe_print(f"[RSS] Fetching from {source['name']}...")
            feed = feedparser.parse(url)
            for entry in feed.entries[:source.get('max_items', 5)]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                news_id = self._generate_news_id(title, link)
                if self.is_duplicate(title, news_id): continue
                
                pub_date = None
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6])
                
                news_items.append({
                    'id': news_id,
                    'title': title.strip(),
                    'link': link,
                    'source': source['name'],
                    'published': pub_date.isoformat() if pub_date else None,
                    'image_url': None
                })
        except Exception as e:
            safe_print(f"  [Error] RSS: {e}")
        return news_items

    def fetch_from_scrape(self, source: dict) -> List[Dict]:
        news_items = []
        try:
            safe_print(f"[Scrape] Fetching from {source['name']}...")
            response = self._make_request(source['url'], use_proxy=True)
            if not response: return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            selectors = source.get('selectors', {})
            articles = soup.select(selectors.get('articles', 'article'))
            
            for art in articles[:source.get('max_items', 5)]:
                title_el = art.select_one(selectors.get('title', 'h2, h3, a'))
                if not title_el: continue
                title = title_el.get_text().strip()
                link = urljoin(source['url'], title_el.get('href') if title_el.name == 'a' else art.select_one('a').get('href'))
                
                news_id = self._generate_news_id(title, link)
                if self.is_duplicate(title, news_id): continue
                
                # Simple Image Extraction (Clean)
                image_url = None
                img = art.find('img')
                if img:
                     src = img.get('src') or img.get('data-src')
                     if src: image_url = urljoin(source['url'], src)

                news_items.append({
                    'id': news_id,
                    'title': title,
                    'link': link,
                    'source': source['name'],
                    'published': datetime.now().isoformat(),
                    'image_url': image_url
                })
        except Exception as e:
            safe_print(f"  [Error] Scrape: {e}")
        return news_items

    def fetch_all_news(self, max_items: int = 10) -> List[Dict]:
        all_news = []
        for source in NEWS_SOURCES:
            if not source.get('enabled', True): continue
            if source.get('type') == 'rss':
                all_news.extend(self.fetch_from_rss(source))
            else:
                all_news.extend(self.fetch_from_scrape(source))
        return all_news[:max_items]

    def fetch_full_article(self, url: str, source_name: str) -> Dict:
        response = self._make_request(url, use_proxy=True)
        if response:
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = [p.get_text() for p in soup.find_all('p')]
                
                # Image Extraction Logic
                main_image = None
                og_image = soup.find('meta', property='og:image')
                if og_image: main_image = og_image.get('content')
                
                return {'success': True, 'full_content': "\n\n".join(paragraphs[:10]), 'main_image': main_image}
            except: pass
        return {'success': False, 'full_content': '', 'main_image': None}


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
