"""
News Fetcher Module
ماژول دریافت اخبار از منابع مختلف
پشتیبانی از RSS، Web Scraping و Proxy
"""

import sys
import io
import random

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
import json
import os
from typing import List, Dict, Optional
from urllib.parse import urljoin

# Import config
from config import NEWS_SOURCES, FILTER_KEYWORDS, USE_PROXY, PROXY_URL, FREE_PROXIES


class NewsFetcher:
    """Fetches and filters news from various sources (RSS + Web Scraping + Proxy)"""
    
    def __init__(self):
        self.cache_file = "news_cache.json"
        self.seen_news = self._load_cache()
        self.current_proxy = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with optional proxy"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _get_proxy(self) -> Optional[Dict]:
        """Get proxy configuration"""
        if not USE_PROXY:
            return None
        
        # Use custom proxy if set
        if PROXY_URL:
            self.current_proxy = PROXY_URL
            return {'http': PROXY_URL, 'https': PROXY_URL}
        
        # Use random free proxy
        if FREE_PROXIES:
            proxy = random.choice(FREE_PROXIES)
            self.current_proxy = proxy
            return {'http': proxy, 'https': proxy}
        
        return None
    
    def _make_request(self, url: str, use_proxy: bool = False, timeout: int = 30) -> Optional[requests.Response]:
        """Make HTTP request with optional proxy and retry logic"""
        proxies = self._get_proxy() if use_proxy else None
        
        # Try with proxy first if enabled
        if proxies:
            try:
                print(f"  [Proxy] Using: {self.current_proxy[:50]}...")
                response = self.session.get(url, proxies=proxies, timeout=timeout, verify=False)
                response.raise_for_status()
                return response
            except Exception as e:
                print(f"  [Proxy Failed] {str(e)[:50]}...")
                # Fall through to try without proxy
        
        # Try without proxy
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"  [Error] Request failed: {str(e)[:50]}...")
            return None
    
    def _load_cache(self) -> set:
        """Load previously seen news IDs"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('seen_ids', []))
            except:
                return set()
        return set()
    
    def _save_cache(self):
        """Save seen news IDs to cache"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump({'seen_ids': list(self.seen_news)}, f)
    
    def _generate_news_id(self, title: str, link: str) -> str:
        """Generate unique ID for news item"""
        content = f"{title}{link}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_relevant(self, title: str, description: str, source_keywords: List[str] = None) -> bool:
        """Check if news is relevant based on keywords"""
        # For human rights sites, all content is relevant
        return True
    
    def _extract_image_from_soup(self, element, base_url: str) -> Optional[str]:
        """Extract image URL from BeautifulSoup element"""
        img = element.find('img')
        if img:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                return urljoin(base_url, src)
        return None
    
    # ==================== RSS Fetching ====================
    def fetch_from_rss(self, source: dict) -> List[Dict]:
        """Fetch news from RSS feed"""
        news_items = []
        url = source.get('rss_url', source.get('url'))
        
        try:
            print(f"[RSS] Fetching from {source['name']}...")
            feed = feedparser.parse(url)
            
            if feed.bozo:
                print(f"  [Warning] Feed error: {str(feed.bozo_exception)[:50]}")
            
            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                
                # Parse HTML in description
                soup = BeautifulSoup(description, 'html.parser')
                clean_description = soup.get_text()
                
                # Check if already seen
                news_id = self._generate_news_id(title, link)
                if news_id in self.seen_news:
                    continue
                
                # Extract publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])
                
                # Extract image
                image_url = None
                if hasattr(entry, 'media_content') and entry.media_content:
                    for media in entry.media_content:
                        if 'image' in media.get('type', ''):
                            image_url = media.get('url')
                            break
                if not image_url:
                    img = soup.find('img')
                    if img and img.get('src'):
                        image_url = img.get('src')
                
                news_item = {
                    'id': news_id,
                    'title': title.strip(),
                    'link': link,
                    'description': clean_description[:1000],
                    'source': source['name'],
                    'source_category': source.get('category', 'حقوق بشر'),
                    'language': source['language'],
                    'published': pub_date.isoformat() if pub_date else None,
                    'image_url': image_url,
                    'fetched_at': datetime.now().isoformat()
                }
                
                news_items.append(news_item)
            
            print(f"  -> Found {len(news_items)} articles")
                
        except Exception as e:
            print(f"  [Error] RSS fetching: {str(e)[:50]}...")
        
        return news_items
    
    # ==================== Web Scraping ====================
    def fetch_from_scrape(self, source: dict) -> List[Dict]:
        """Fetch news by scraping website"""
        news_items = []
        url = source['url']
        selectors = source.get('selectors', {})
        use_proxy = source.get('use_proxy', True)  # Use proxy by default for scraping
        
        try:
            print(f"[Scrape] Fetching from {source['name']}...")
            
            response = self._make_request(url, use_proxy=use_proxy, timeout=30)
            if not response:
                print(f"  -> Found 0 articles (failed to fetch)")
                return []
            
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find articles
            article_selector = selectors.get('articles', 'article, .post')
            if ',' in article_selector:
                # Handle comma-separated selectors manually if needed, but select() supports it.
                # However, complex selectors might need care.
                pass
            
            articles = soup.select(article_selector)
            # Limit to 20
            articles = articles[:20]
            
            print(f"  [Debug] Selector '{article_selector}' found {len(articles)} items")
            
            if not articles:
                # Try alternative approach - find links with titles
                links = soup.select('a[href*="?p="], a[href*="/20"]')
                for link in links[:20]:
                    title = link.get_text().strip()
                    title = " ".join(title.split())  # Remove newlines and extra spaces
                    href = link.get('href')
                    
                    if len(title) < 10 or not href:
                        continue
                    
                    full_link = urljoin(url, href)
                    news_id = self._generate_news_id(title, full_link)
                    
                    if news_id in self.seen_news:
                        continue
                    
                    # Try to find image near the link
                    parent = link.parent
                    image_url = self._extract_image_from_soup(parent, url) if parent else None
                    
                    news_items.append({
                        'id': news_id,
                        'title': title,
                        'link': full_link,
                        'description': title,
                        'source': source['name'],
                        'source_category': source.get('category', 'حقوق بشر'),
                        'language': source['language'],
                        'published': datetime.now().isoformat(),
                        'image_url': image_url,
                        'fetched_at': datetime.now().isoformat()
                    })
            else:
                for article in articles:
                    # Extract title
                    title_el = article.select_one(selectors.get('title', 'h2 a, h3 a'))
                    if not title_el:
                        continue
                    
                    title = title_el.get_text().strip()
                    title = " ".join(title.split())  # Remove newlines and extra spaces
                    if len(title) < 5:
                        continue
                    
                    # Extract link
                    link_el = article.select_one(selectors.get('link', 'a'))
                    link = link_el.get('href', '') if link_el else ''
                    full_link = urljoin(url, link)
                    
                    # Check if already seen
                    news_id = self._generate_news_id(title, full_link)
                    if news_id in self.seen_news:
                        continue
                    
                # Extract description
                desc_el = article.select_one(selectors.get('description', 'p'))
                description = desc_el.get_text().strip() if desc_el else title
                
                # Extract image
                image_selector = selectors.get('image', 'img')
                img_el = article.select_one(image_selector)
                
                image_url = None
                if img_el:
                    # Check common lazy loading attributes
                    raw_url = img_el.get('data-src') or img_el.get('data-original') or img_el.get('src')
                    if raw_url and not raw_url.startswith('data:'):
                        image_url = urljoin(url, raw_url)
                
                news_items.append({
                    'id': news_id,
                    'title': title,
                        'link': full_link,
                        'description': description[:1000],
                        'source': source['name'],
                        'source_category': source.get('category', 'حقوق بشر'),
                        'language': source['language'],
                        'published': datetime.now().isoformat(),
                        'image_url': image_url,
                        'fetched_at': datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"  [Error] Scraping: {str(e)[:50]}...")
        
        print(f"  -> Found {len(news_items)} articles")
        return news_items
    
    def fetch_from_source(self, source: dict) -> List[Dict]:
        """Fetch news from a single source (auto-detect method)"""
        source_type = source.get('type', 'rss')
        
        if source_type == 'scrape':
            return self.fetch_from_scrape(source)
        else:
            return self.fetch_from_rss(source)
    
    def fetch_all_news(self, max_items: int = 10) -> List[Dict]:
        """Fetch news from all enabled sources"""
        all_news = []
        
        for source in NEWS_SOURCES:
            if not source.get('enabled', True):
                continue
            
            items = self.fetch_from_source(source)
            all_news.extend(items)
        
        # Sort by fetched time (newest first)
        all_news.sort(
            key=lambda x: x.get('fetched_at', ''),
            reverse=True
        )
        
        # Limit total items
        all_news = all_news[:max_items]
        
        print(f"\n[OK] Found {len(all_news)} new news items total")
        return all_news
    
    def mark_as_seen(self, news_id: str):
        """Mark news item as processed"""
        self.seen_news.add(news_id)
        self._save_cache()
    
    def download_image(self, image_url: str, save_path: str) -> bool:
        """Download image from URL"""
        try:
            response = self.session.get(image_url, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"[Error] Downloading image: {e}")
            return False


# Disable SSL warnings for proxy
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Test the fetcher
if __name__ == "__main__":
    print("=" * 60)
    print("Testing News Fetcher with Proxy Support")
    print("=" * 60)
    
    fetcher = NewsFetcher()
    news = fetcher.fetch_all_news(max_items=15)
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(news)} news items from human rights sources")
    print('='*60)
    
    for i, item in enumerate(news, 1):
        print(f"\n[{i}] {item['title'][:70]}...")
        print(f"    Source: {item['source']}")
        print(f"    Link: {item['link'][:80]}...")
        if item.get('image_url'):
            print(f"    Image: YES")
