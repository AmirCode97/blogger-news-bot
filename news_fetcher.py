
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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fa,en-US;q=0.9,en;q=0.8',
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
        
        # Try with proxy first
        if proxies:
            try:
                response = self.session.get(url, proxies=proxies, timeout=timeout, verify=False)
                if response.status_code == 200:
                    return response
            except: pass
        
        # Try without proxy
        try:
            response = self.session.get(url, timeout=timeout, verify=False)
            if response.status_code == 200:
                return response
        except: pass
        
        return None

    def fetch_from_rss(self, source: dict) -> List[Dict]:
        news_items = []
        url = source.get('rss_url', source.get('url'))
        try:
            safe_print(f"[RSS] Fetching from {source['name']}...")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:source.get('max_items', 5)]:
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                
                news_id = self._generate_news_id(title, link)
                if self.is_duplicate(title, news_id): continue
                
                # Get description from RSS
                raw_desc = entry.get('summary', entry.get('description', ''))
                description = BeautifulSoup(raw_desc, 'html.parser').get_text()[:500] if raw_desc else ""
                
                # Get image
                image_url = None
                media = entry.get('media_content', entry.get('media_thumbnail', []))
                if media and len(media) > 0:
                    image_url = media[0].get('url')
                if not image_url:
                    for enc in entry.get('enclosures', []):
                        if 'image' in enc.get('type', ''):
                            image_url = enc.get('url')
                            break

                news_items.append({
                    'id': news_id,
                    'title': title,
                    'link': link,
                    'description': description,  # IMPORTANT: Store RSS description
                    'source': source['name'],
                    'source_category': source.get('category', 'News'),
                    'published': entry.get('published', datetime.now().isoformat()),
                    'image_url': image_url
                })
        except Exception as e:
            safe_print(f"  [Error] RSS: {e}")
        return news_items

    def fetch_from_scrape(self, source: dict) -> List[Dict]:
        news_items = []
        try:
            safe_print(f"[Scrape] Fetching from {source['name']}...")
            response = self._make_request(source['url'], use_proxy=True)
            if not response: 
                safe_print(f"  [Error] Could not fetch {source['url']}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            selectors = source.get('selectors', {})
            
            # Get article selector
            article_selector = selectors.get('articles', 'article')
            articles = soup.select(article_selector)
            
            if not articles:
                # Fallback: try common patterns
                articles = soup.find_all('article') or soup.find_all('div', class_=re.compile(r'post|article|news'))
            
            safe_print(f"  Found {len(articles)} articles")
            
            for art in articles[:source.get('max_items', 5)]:
                # Find title and link
                title_sel = selectors.get('title', 'h2 a, h3 a, .title a, a')
                title_el = art.select_one(title_sel) if title_sel else art.find(['h2', 'h3', 'h4'])
                
                if not title_el: continue
                
                title = title_el.get_text().strip()
                if len(title) < 10: continue  # Skip short titles
                
                # Get link
                if title_el.name == 'a':
                    link = title_el.get('href', '')
                else:
                    link_el = title_el.find('a') or art.find('a')
                    link = link_el.get('href', '') if link_el else ''
                
                if not link: continue
                link = urljoin(source['url'], link)
                
                news_id = self._generate_news_id(title, link)
                if self.is_duplicate(title, news_id): continue
                
                # Get description from the listing (if available)
                desc_el = art.select_one(selectors.get('description', 'p, .excerpt, .summary'))
                description = desc_el.get_text().strip() if desc_el else ""
                
                # Get image
                image_url = None
                img = art.find('img')
                if img:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src: 
                        image_url = urljoin(source['url'], src)

                news_items.append({
                    'id': news_id,
                    'title': title,
                    'link': link,
                    'description': description,  # Store description from listing
                    'source': source['name'],
                    'source_category': source.get('category', 'News'),
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
        """
        Fetch full article content from the news page.
        Returns dict with success, full_content, main_image
        """
        safe_print(f"  [Fetch] {url[:60]}...")
        
        response = self._make_request(url, use_proxy=True)
        if not response:
            safe_print(f"  [Warning] Could not fetch article page")
            return {'success': False, 'full_content': '', 'main_image': None}
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # =============================================
            # SPECIAL HANDLING FOR KNOWN SOURCES
            # =============================================
            
            paragraphs = []
            main_image = None
            
            # ==== Iran International ====
            if 'iranintl.com' in url:
                # Get content from meta description or JSON-LD
                meta_desc = soup.find('meta', {'name': 'description'})
                if meta_desc:
                    paragraphs.append(meta_desc.get('content', ''))
                
                # Try to get content from script tags (JSON-LD)
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict):
                            if 'articleBody' in data:
                                paragraphs = [data['articleBody']]
                                break
                            elif 'description' in data:
                                paragraphs.append(data['description'])
                    except: pass
                
                # Get og:image
                og_img = soup.find('meta', property='og:image')
                if og_img:
                    main_image = og_img.get('content')
            
            # ==== Iran HRS (Human Rights) ====
            elif 'iranhrs.org' in url or 'iran-hrm.com' in url:
                # Try entry-content first
                content_div = soup.find('div', class_='entry-content') or soup.find('article')
                if content_div:
                    for p in content_div.find_all(['p', 'div']):
                        text = p.get_text().strip()
                        if len(text) > 50 and 'cookie' not in text.lower():
                            paragraphs.append(text)
                
                # Image
                og_img = soup.find('meta', property='og:image')
                if og_img:
                    main_image = og_img.get('content')
                elif content_div:
                    img = content_div.find('img')
                    if img:
                        main_image = urljoin(url, img.get('src', ''))
            
            # ==== Generic Extraction ====
            else:
                # Find main content area
                content_selectors = [
                    ('article', {}),
                    ('div', {'class': 'entry-content'}),
                    ('div', {'class': 'post-content'}),
                    ('div', {'class': 'content'}),
                    ('main', {}),
                ]
                
                main_div = None
                for tag, attrs in content_selectors:
                    main_div = soup.find(tag, attrs) if attrs else soup.find(tag)
                    if main_div:
                        break
                
                if not main_div:
                    main_div = soup.body
                
                if main_div:
                    for p in main_div.find_all(['p']):
                        text = p.get_text().strip()
                        if len(text) > 50:
                            paragraphs.append(text)
                
                # Image extraction
                og_img = soup.find('meta', property='og:image')
                if og_img:
                    main_image = og_img.get('content')
                else:
                    twitter_img = soup.find('meta', {'name': 'twitter:image'})
                    if twitter_img:
                        main_image = twitter_img.get('content')
            
            # Build full text
            full_text = "\n\n".join(paragraphs[:15]) if paragraphs else ""
            
            # Log results
            if full_text:
                safe_print(f"  [OK] Extracted {len(paragraphs)} paragraphs, {len(full_text)} chars")
            else:
                safe_print(f"  [Warning] No content extracted")
            
            return {
                'success': len(full_text) > 50,
                'full_content': full_text,
                'main_image': main_image
            }
            
        except Exception as e:
            safe_print(f"  [Error] Parse: {e}")
            return {'success': False, 'full_content': '', 'main_image': None}


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
