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
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin

# Import config
from config import NEWS_SOURCES, FILTER_KEYWORDS, USE_PROXY, PROXY_URL, FREE_PROXIES


class NewsFetcher:
    """Fetches and filters news from various sources (RSS + Web Scraping + Proxy)"""
    
    def __init__(self):
        self.cache_file = "news_cache.json"
        self._load_cache() # Sets self.seen_ids and self.seen_titles
        self.seen_news = self.seen_ids # Alias for backward compatibility
        self.current_proxy = None
        self._setup_session()

    # ... (rest of methods)

    def _save_cache(self):
        """Save seen news IDs and Titles to cache"""
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
        """Generate unique hash for news item"""
        # نرمال‌سازی عنوان برای جلوگیری از تکرار با تغییرات جزئی
        clean_title = re.sub(r'[^\w\s]', '', title).strip()
        unique_string = f"{clean_title}_{link}"
        return hashlib.md5(unique_string.encode()).hexdigest()
        
    def is_duplicate(self, title: str, news_id: str) -> bool:
        """Check if news is duplicate by ID or Title"""
        if news_id in self.seen_ids:
            return True
            
        # چک کردن عنوان (دقیق)
        if title in self.seen_titles:
            return True
            
        # چک کردن عنوان (شباهت - اختیاری، فعلا دقیق)
        # برای سرعت بیشتر بهتر است دقیق باشد
        return False
        
    def mark_as_seen(self, title: str, news_id: str):
        """Add news to seen list"""
        self.seen_ids.add(news_id)
        self.seen_titles.add(title)
        self._save_cache()
    
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
    
    
    def _load_cache(self) -> dict:
        """Load previously seen news IDs and Titles"""
        self.seen_ids = set()
        self.seen_titles = set()
        
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.seen_ids = set(data.get('seen_ids', []))
                    self.seen_titles = set(data.get('seen_titles', []))
            except:
                pass
        return self.seen_ids
    
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
            
            # Get max items for this source (default 5)
            max_items = source.get('max_items', 5)
            
            for entry in feed.entries[:max_items]:
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
            # Limit to source max_items (default 5)
            max_items = source.get('max_items', 5)
            articles = articles[:max_items]
        
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
                
                    if self.is_duplicate(title, news_id):
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
                        'language': source.get('language', 'fa'),
                        'published': datetime.now().isoformat(),
                        'image_url': image_url,
                        'fetched_at': datetime.now().isoformat()
                    })
            else:
                for article in articles:
                    try:
                        # اگر خود article یک لینک است (a tag)
                        if article.name == 'a':
                            # (کد قبلی)
                            title = article.get_text().strip()
                            title = " ".join(title.split())
                            href = article.get('href', '')
                        
                            if len(title) < 10 or not href:
                                continue
                        
                            # رد کردن لینک‌های liveblog
                            if 'liveblog' in href.lower() or '#' in href:
                                continue
                        
                            full_link = urljoin(url, href)
                            news_id = self._generate_news_id(title, full_link)
                        
                            if news_id in self.seen_news:
                                continue
                        
                            # عکس از parent
                            parent = article.parent
                            image_url = self._extract_image_from_soup(parent, url) if parent else None
                        
                            news_items.append({
                                'id': news_id,
                                'title': title,
                                'link': full_link,
                                'description': title,
                                'source': source['name'],
                                'source_category': source.get('category', 'حقوق بشر'),
                                'language': source.get('language', 'fa'),
                                'published': datetime.now().isoformat(),
                                'image_url': image_url,
                                'fetched_at': datetime.now().isoformat()
                            })
                            continue
                    
                        # Extract title از child element
                        title_selector = selectors.get('title', 'h2 a, h3 a') 
                    except Exception as e:
                        print(f"  [Error] Processing article: {e}")
                        continue
                    title_el = article.select_one(title_selector) if title_selector else None
                    if not title_el:
                        continue
                
                    title = title_el.get_text().strip()
                    title = " ".join(title.split())
                    if len(title) < 5:
                        continue
                
                    # Extract link
                    link_el = article.select_one(selectors.get('link', 'a'))
                    link = link_el.get('href', '') if link_el else ''
                    full_link = urljoin(url, link)
                
                    # Check if already seen
                    news_id = self._generate_news_id(title, full_link)
                    if self.is_duplicate(title, news_id):
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
                        'language': source.get('language', 'fa'),
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

    def fetch_full_article(self, article_url: str, source_name: str = "") -> Dict:
        """
        Fetch full article content - CLEAN VERSION
        دریافت محتوای تمیز خبر: فقط متن پاراگراف‌ها و عکس اصلی
        """
        result = {
            'full_content': '',
            'main_image': None,
            'images': [],
            'videos': [],
            'success': False
        }
        
        # لیست سایت‌هایی که با ریکوئست ساده بهتر جواب می‌دهند
        direct_request_sites = ['iranintl', 'radiofarda', 'hra-iran', 'iranhrs', 'bashariyat']
        
        response = None
        if any(site in article_url for site in direct_request_sites):
            try:
                print(f"  [{next((s for s in direct_request_sites if s in article_url), 'Site')}] Trying simple request...")
                # هدرهای شبیه مرورگر واقعی برای جلوگیری از ۴۰۳
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
                }
                response = requests.get(article_url, headers=headers, timeout=15)
                response.encoding = 'utf-8'
                if response.status_code != 200:
                    raise Exception(f"Status {response.status_code}")
            except Exception as e:
                print(f"  [Simple Request Failed] {e}, trying proxy...")
                response = None
        
        if not response:
            response = self._make_request(article_url, use_proxy=True, timeout=30)
        
        if not response:
            return result
        
        response.encoding = 'utf-8'

        # پردازش تصویر اصلی (Universal) - اولویت با متاتگ OpenGraph
        soup = BeautifulSoup(response.text, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            result['main_image'] = og_image['content']
        
        # اگر تصویر پیدا نشد، دنبال توییتر کارت بگرد
        if not result['main_image']:
            twitter_img = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_img and twitter_img.get('content'):
                result['main_image'] = twitter_img['content']

        paragraphs = []
        
        # 1. ایران اینترنشنال (React/Next.js - Brute Force JSON)
        if 'iranintl' in article_url:
             # ... (کد قبلی ایران اینترنشنال سر جای خودش بماند یا اینجا فراخوانی شود)
             # چون کد قبلی طولانی بود، من اینجا فقط لاجیک جدید بقیه را اضافه می‌کنم و می‌گذاریم کد قبلی اجرا شود
             pass

        # 2. رادیو فردا (Radio Farda) - ساختار مشخص
        elif 'radiofarda' in article_url:
            # رادیو فردا معمولا در #content یا .w-content است
            content_div = soup.select_one('#content, .w-content, .col-title, .content-body')
            if content_div:
                for p in content_div.find_all('p'):
                    txt = p.get_text(strip=True)
                    if len(txt) > 30:
                        paragraphs.append(txt)
        
        # 3. هرانا (HRA) و ایران HRS و بشریت (WordPress Standard)
        elif any(s in article_url for s in ['hra-iran', 'iranhrs', 'bashariyat']):
            # وردپرس معمولا .entry-content یا article دارد
            content_div = soup.select_one('.entry-content, article, .post-content, .elementor-widget-theme-post-content')
            if content_div:
                # حذف عناصر مزاحم قبل از استخراج
                for junk in content_div.select('.sharedaddy, .yarpp-related, .printfriendly, .jp-relatedposts'):
                    junk.decompose()
                    
                for p in content_div.find_all(['p', 'h2', 'h3']):
                    txt = p.get_text(strip=True)
                    if len(txt) > 30 and 'بیشتر بخوانید' not in txt:
                        paragraphs.append(txt)

        # اگر پاراگراف‌ها با روش سلکتور پیدا نشدند یا خیلی کم بودند -> Fallback به روش Brute Force HTML
        # (برای همه سایت‌ها بجز ایران اینترنشنال که لاجیک خودش را دارد)
        if 'iranintl' not in article_url and len(paragraphs) < 3:
            print("    [Fallback] Using HTML Brute Force for text...")
            all_ps = soup.find_all('p')
            for p in all_ps:
                txt = p.get_text(strip=True)
                # فیلترهای سخت‌گیرانه برای اطمینان از کیفیت
                if len(txt) > 60 and self._is_persian(txt):
                    # چک کردن لیست سیاه
                    if not any(x in txt for x in ['تبلیغات', 'تماس با ما', 'حقوق محفوظ', 'عضویت', 'خبرنامه']):
                        if txt not in paragraphs:
                            paragraphs.append(txt)

        # ادامه کد برای ایران اینترنشنال (که پایین‌تر است) اجرا می‌شود...
        # اما ما باید مطمئن شویم که اگر paragraphs پر شد، کد ایران اینترنشنال خرابکاری نکند.
        # در کد اصلی، ایران اینترنشنال یک if جداگانه دارد.
        
        # برای اینکه تداخل پیش نیاید، من متغیر paragraphs را به کدهای بعدی پاس می‌دهم.
        # اما چون در پایتون نمی‌توانی وسط تابع راحت پرش کنی، من کد ایران اینترنشنال را در یک شرط else if یا if جدا قرار می‌دهم.

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ========== حذف کامل المان‌های اضافی ==========
        # ========== حذف کامل المان‌های اضافی ==========
        unwanted_selectors = [
            'style', 'nav', 'header', 'footer', 'aside',
            '.sidebar', '.comments', '.related-posts', '.advertisement',
            '.social-share', '.share-buttons', '.author-box', '.tags',
            '.breadcrumb', '.navigation', '.menu', '.logo', '.search',
            '.widget', '.banner', 'iframe', 'noscript', 'form',
            '[class*="header"]', '[class*="footer"]', '[class*="nav"]',
            '[class*="menu"]', '[class*="sidebar"]', '[class*="share"]',
            '[class*="social"]', '[class*="comment"]', '[class*="related"]',
            '[class*="ads"]', '[class*="banner"]', '[class*="widget"]',
            '[class*="more"]', '[class*="popular"]', '[class*="trending"]',
            '[id*="header"]', '[id*="footer"]', '[id*="nav"]', '[id*="menu"]',
            '[id*="sidebar"]', '[id*="comments"]', '[id*="related"]',
        ]
        
        # برای غیر از ایران اینترنشنال، اسکریپت‌ها را پاک کن
        # ایران اینترنشنال محتوا را در اسکریپت نگه‌می‌دارد (Next.js)
        if 'iranintl' not in article_url:
            unwanted_selectors.insert(0, 'script')

        for selector in unwanted_selectors:
            for tag in soup.select(selector):
                tag.decompose()
                tag.decompose()
        
        # ========== استخراج عکس اصلی (og:image) - اگر قبلاً پیدا نشده ==========
        if not result.get('main_image'):
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                result['main_image'] = og_image['content']
        
        # ========== استخراج og:description به عنوان lead ==========
        # اگر paragraphs تعریف نشده بود (برای سایت‌های ناشناخته) تعریف کن
        if 'paragraphs' not in locals():
            paragraphs = []
            
        og_desc = soup.find('meta', property='og:description')
        lead_text = ""
        if og_desc and og_desc.get('content'):
            lead_text = og_desc['content'].strip()
            if len(lead_text) > 50:
                # فقط اگر تکراری نیست اضافه کن
                is_duplicate = False
                for p in paragraphs:
                    if lead_text in p or p in lead_text:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    paragraphs.insert(0, lead_text) # لید را اول بگذار
        # ========== روش جدید برای ایران اینترنشنال: استخراج ساده از HTML ==========
        # سایت ایران اینترنشنال محتوای اخبار مرتبط را هم نشان می‌دهد
        # باید فقط ۲-۳ پاراگراف اول مقاله اصلی را بگیریم
        if 'iranintl' in article_url:
            print(f"    [IranIntl] Extracting article paragraphs from HTML...")
            
            # پیدا کردن همه پاراگراف‌های فارسی
            all_ps = soup.find_all('p')
            persian_paragraphs = []
            
            for p in all_ps:
                text = p.get_text(strip=True)
                if not text:
                    continue
                    
                # بررسی فارسی بودن
                persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
                if persian_chars < 30:
                    continue
                    
                # حداقل ۵۰ کاراکتر
                if len(text) < 50:
                    continue
                    
                # فیلتر محتوای نامربوط
                skip_indicators = ['بیشتر بخوانید', 'مطالب مرتبط', 'تبلیغات', 'عضویت', 'خبرنامه', 
                                  'اپلیکیشن', 'تماس با ما', 'حقوق محفوظ']
                if any(x in text for x in skip_indicators):
                    continue
                
                persian_paragraphs.append(text)
            
            print(f"    [IranIntl] Found {len(persian_paragraphs)} Persian paragraphs")
            
            # استخراج عنوان برای شناسایی پایان مقاله اصلی
            article_title = ""
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                article_title = og_title['content']
            
            # استخراج نام اصلی از عنوان (مثلاً "رادان")
            # کلمات کوتاه (کمتر از ۴ حرف) و عمومی را نادیده بگیر
            generic_words = {'ایران', 'آمریکا', 'اسرائیل', 'تهران', 'فرانسه', 'روسیه', 'اروپا',
                           'جمهوری', 'اسلامی', 'گفت', 'شد', 'است', 'این', 'کرد', 'خواهد', 'خواهند'}
            
            main_keywords = set()
            if article_title:
                for word in re.split(r'[\s\-،:؛|]+', article_title):
                    word = word.strip()
                    if len(word) > 3 and word not in generic_words:
                        main_keywords.add(word)
            
            print(f"    [IranIntl] Main article keywords: {main_keywords}")
            
            # فقط پاراگراف‌های مقاله اصلی را بگیر
            # روش ساده: فقط لید + ادامه مستقیم (حداکثر ۲ پاراگراف)
            
            selected_paragraphs = []
            
            # پاراگراف اول: لید
            if persian_paragraphs:
                selected_paragraphs.append(persian_paragraphs[0])
            
            # پاراگراف دوم: اگر با "او افزود" شروع شود و درباره همان موضوع باشد
            if len(persian_paragraphs) > 1:
                second = persian_paragraphs[1]
                # بررسی اینکه آیا ادامه مقاله است
                if second.startswith('او افزود') or second.startswith('وی گفت') or second.startswith('وی افزود'):
                    # فقط اگر درباره همان موضوع باشد (کلمه کلیدی داشته باشد یا بدون نام جدید)
                    has_main_keyword = any(kw in second for kw in main_keywords)
                    # لیست نام‌های دیگر که نشان‌دهنده خبر جدید است
                    other_names = ['بارو', 'ترامپ', 'وای‌نت', 'معاریو', 'واشینگتن‌پست', 
                                  'رویترز', 'اکسیوس', 'نتانیاهو', 'بایدن', 'پوتین']
                    has_other_name = any(name in second for name in other_names)
                    
                    if has_main_keyword or not has_other_name:
                        selected_paragraphs.append(second)
            
            paragraphs = selected_paragraphs
            print(f"    -> Selected {len(paragraphs)} paragraphs for main article") 

        # ========== روش اختصاصی: ناظران حقوق بشر ایران (Iran HRM) ==========
        elif 'iran-hrm' in article_url:
            print(f"    [IranHRM] Extracting content...")
            content_div = soup.select_one('.entry-content')
            if content_div:
                # حذف پاراگراف‌های نامربوط (تبلیغات، اشتراک، لینک‌های انتهایی)
                for p in content_div.find_all('p'):
                    text = p.get_text(strip=True)
                    # فیلترهای حذف
                    skip_phrases = [
                        'در شبکه‌های اجتماعی دنبال کنید', 'به کانال تلگرام ما بپیوندید',
                        'Call to Action', 'Donate', 'حمایت کنید', 'اشتراک گذاری'
                    ]
                    if any(phrase in text for phrase in skip_phrases):
                        continue
                    
                    if len(text) > 30:
                        paragraphs.append(text)
                
                # محدود به ۱۰ پاراگراف اول (چون گزارش‌ها خیلی طولانی هستند)
                if len(paragraphs) > 10:
                    paragraphs = paragraphs[:10]
                    paragraphs.append("...")
                
                print(f"    [IranHRM] Extracted {len(paragraphs)} clean paragraphs")

        # ========== روش اختصاصی: مرکز اسناد حقوق بشر ایران ==========
        elif 'iranhumanrights.org' in article_url:
            print(f"    [IranHumanRights] Extracting content...")
            # تست سلکتورهای مختلف وردپرسی
            selectors = ['.entry-content', '.post-content', '.article-content']
            content_div = None
            for sel in selectors:
                content_div = soup.select_one(sel)
                if content_div: break
            
            if content_div:
                for p in content_div.find_all('p'):
                    text = p.get_text(strip=True)
                    if len(text) > 30 and 'بیشتر بخوانید' not in text:
                        paragraphs.append(text)
                
                # محدودیت ۱۵ پاراگراف برای جلوگیری از پست‌های خیلی طولانی
                if len(paragraphs) > 15:
                    paragraphs = paragraphs[:15]
                    paragraphs.append("...")
                
                print(f"    [IranHumanRights] Extracted {len(paragraphs)} clean paragraphs") 
            
        # ========== روش ۲: استخراج از HTML (سایت‌های معمولی و فال‌بک) ==========
        if len(paragraphs) < 3:
            content_element = None
            
            # سلکتورهای خاص ایران اینترنشنال و عمومی
            selectors = [
                'div[class*="ArticleBody"]', # IranIntl dynamic class
                'div[class*="CustomPortableText"]', # IranIntl portable text
                '.article-body', '.post-body', '.entry-content', 
                '.news-content', '.content-body', 'article', 'main'
            ]
            
            for selector in selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    print(f"    [Selector] Found content using: {selector}")
                    break
            
            if content_element:
                all_paragraphs = content_element.find_all('p')
                
                # اگر p نداشت، div های متن‌دار را بگیر
                if len(all_paragraphs) < 2:
                     # همه div ها
                     divs = content_element.find_all('div')
                     for div in divs:
                         # فقط اگر متن خالص قابل توجهی دارد
                         t = div.get_text(strip=True)
                         if len(t) > 50 and len(div.find_all()) == 0: # leaf node
                             all_paragraphs.append(div)
                     
                stop_indicators = [
                    'مطالب بیشتر', 'پربازدیدترین', 'بیشتر بخوانید', 
                    'همچنین بخوانید', 'انتخاب سردبیر', 'اخبار مرتبط'
                ]
                
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    
                    if any(stop in text for stop in stop_indicators):
                        break
                    
                    if len(text) < 50 or text in paragraphs:
                        continue
                    
                    if text.startswith('[') or text.count('[') > 3:
                        continue
                    
                    paragraphs.append(text)
                    
                    if len(paragraphs) >= 15:
                        break
        
        # ========== SEO: Internal Linking Logic ==========
        SEO_KEYWORDS = {
            'ایران': '/search/label/ایران',
            'حقوق بشر': '/search/label/حقوق%20بشر',
            'آمریکا': '/search/label/بین‌الملل',
            'اسرائیل': '/search/label/بین‌الملل',
            'اروپا': '/search/label/بین‌الملل',
            'خاورمیانه': '/search/label/بین‌الملل',
            'زندان': '/search/label/حقوق%20بشر',
            'اعدام': '/search/label/حقوق%20بشر',
            'زنان': '/search/label/حقوق%20بشر',
            'سیاسی': '/search/label/سیاست',
            'خامنه‌ای': '/search/label/سیاست',
            'رئیسی': '/search/label/سیاست',
            'پزشکیان': '/search/label/سیاست',
            'سپاه': '/search/label/سیاست',
            'هسته‌ای': '/search/label/بین‌الملل',
            'تحریم': '/search/label/بین‌الملل',
            'مجلس': '/search/label/سیاست',
            'دولت': '/search/label/سیاست',
            'اقتصاد': '/search/label/اقتصاد',
            'تورم': '/search/label/اقتصاد',
            'دلار': '/search/label/اقتصاد',
            'نفت': '/search/label/اقتصاد',
            'بورس': '/search/label/اقتصاد',
            'خودرو': '/search/label/اقتصاد',
            'مسکن': '/search/label/اقتصاد',
            'طلا': '/search/label/اقتصاد',
            'ارز': '/search/label/اقتصاد',
            'بانک': '/search/label/اقتصاد',
            'تجارت': '/search/label/اقتصاد',
            'صادرات': '/search/label/اقتصاد',
            'واردات': '/search/label/اقتصاد',
            'ورزش': '/search/label/ورزش',
            'فوتبال': '/search/label/ورزش',
            'استقلال': '/search/label/ورزش',
            'پرسپولیس': '/search/label/ورزش',
            'کشتی': '/search/label/ورزش',
            'والیبال': '/search/label/ورزش',
            'بسکتبال': '/search/label/ورزش',
            'سینما': '/search/label/فرهنگ%20و%20هنر',
            'تئاتر': '/search/label/فرهنگ%20و%20هنر',
            'موسیقی': '/search/label/فرهنگ%20و%20هنر',
            'کتاب': '/search/label/فرهنگ%20و%20هنر',
            'هنر': '/search/label/فرهنگ%20و%20هنر',
            'فناوری': '/search/label/فناوری',
            'اینترنت': '/search/label/فناوری',
            'موبایل': '/search/label/فناوری',
            'کامپیوتر': '/search/label/فناوری',
            'هوش مصنوعی': '/search/label/فناوری',
            'سلامت': '/search/label/سلامت',
            'پزشکی': '/search/label/سلامت',
            'کرونا': '/search/label/سلامت',
            'واکسن': '/search/label/سلامت',
            'بیماری': '/search/label/سلامت',
            'درمان': '/search/label/سلامت',
            'دارو': '/search/label/سلامت',
            'محیط زیست': '/search/label/محیط%20زیست',
            'آلودگی': '/search/label/محیط%20زیست',
            'آب': '/search/label/محیط%20زیست',
            'هوا': '/search/label/محیط%20زیست',
            'جنگل': '/search/label/محیط%20زیست',
            'حیوانات': '/search/label/محیط%20زیست',
            'جامعه': '/search/label/جامعه',
            'خانواده': '/search/label/جامعه',
            'کودکان': '/search/label/جامعه',
            'طلاق': '/search/label/جامعه',
            'ازدواج': '/search/label/جامعه',
            'فرهنگ': '/search/label/فرهنگ'
        }
        
        used_keywords = set()
        clean_html = ""
        
        # Sort keywords by length (descending) to match longest phrases first
        sorted_keywords = sorted(SEO_KEYWORDS.keys(), key=len, reverse=True)

        for p in paragraphs:
            # SEO Linking Logic
            processed_text = p
            for kw in sorted_keywords:
                if kw not in used_keywords and kw in processed_text:
                    # Link constraint: Only link if keyword is surrounded by spaces or punctuation
                    # and not already part of a link (simple check)
                    
                    # Simple replacement for first occurrence
                    link = f'<a href="{SEO_KEYWORDS[kw]}" title="اخبار {kw}" style="color:#ea2027;font-weight:bold;text-decoration:none">{kw}</a>'
                    processed_text = processed_text.replace(kw, link, 1)
                    used_keywords.add(kw)
                    
                    # Limit: Max 5 links per article to avoid spammy look
                    if len(used_keywords) >= 5:
                        break
            
            clean_html += f"<p style='margin-bottom: 15px; line-height: 2; text-align: justify;'>{processed_text}</p>\n"
        
        if clean_html:
            result['full_content'] = clean_html
            # result['main_image'] unmodified
            result['success'] = True
            print(f"    -> Got {len(paragraphs)} paragraphs (with {len(used_keywords)} SEO links)")
        else:
            print(f"    -> No clean content found")
            
        return result

    
    def _is_persian(self, text: str) -> bool:
        """Check if text contains Persian characters"""
        if not text: return False
        persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        return persian_chars > 3

    def download_image(self, image_url: str, save_path: str) -> bool:
        """Download image from URL"""
        try:
            response = self.session.get(image_url, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            # print(f"[Error] Downloading image: {e}")
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
