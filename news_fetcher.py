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
                    # اگر خود article یک لینک است (a tag)
                    if article.name == 'a':
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
                            'description': title,  # description را بعداً fetch می‌کنیم
                            'source': source['name'],
                            'source_category': source.get('category', 'حقوق بشر'),
                            'language': source['language'],
                            'published': datetime.now().isoformat(),
                            'image_url': image_url,
                            'fetched_at': datetime.now().isoformat()
                        })
                        continue
                
                    # Extract title از child element
                    title_selector = selectors.get('title', 'h2 a, h3 a')
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
        
        # ========== روش ۱: استخراج متن خام (Brute Force) ==========
        # برای سایت‌های مدرن مثل ایران اینترنشنال که محتوا در JSON پخش شده
        if 'iranintl' in article_url:
            print(f"    [Brute Force] Scanning page text ({len(response.text)} chars)...")
            
            # Regex ساده‌تر و سریع‌تر
            # پیدا کردن همه رشته‌های طولانی بین کوتیشن
            matches = re.findall(r'"([^"]{40,})"', response.text)
            
            print(f"    [Debug] Matches found: {len(matches)}")
            
            script_paragraphs = []
            junk_indicators = [
                'div class', 'meta name', 'Link rel', 'script src', 'return', 'function', 
                'var ', 'window.', 'document.', 'items:', 'children:', 'class=', 'style=',
                'بیشتر بخوانید', 'مطالب مرتبط', 'نظرات شما', 'تبلیغات', 
                'عضویت در خبرنامه', 'اپلیکیشن', 'googletag'
            ]
            
            # استخراج کلمات کلیدی از لید برای اولویت‌بندی
            keywords = []
            if lead_text:
                keywords = [w for w in re.split(r'\s+', lead_text) if len(w) > 3][:8]

            # لیست‌های جداگانه برای اولویت‌بندی
            high_priority = []
            medium_priority = []
            
            for m in matches:
                text = m
                
                # تمیز کردن اولیه
                if '\\u' in text:
                    try: text = text.encode().decode('unicode_escape')
                    except: pass
                
                text = text.replace('\\n', ' ').replace('\\"', '"').replace('\\', '').strip()
                text = re.sub(r'\s+', ' ', text) # فاصله های اضافی
                
                # حذف تگ‌های HTML باقی‌مانده
                text = re.sub(r'<[^>]+>', '', text)
                if not text: continue
                
                # حذف کاراکترهای شروع بد
                if text.startswith('>') or text.startswith('<') or text.startswith('/') or text.startswith(','):
                    continue

                # شرط فارسی بودن قوی
                persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
                if persian_chars < 15: # حداقل ۱۵ حرف فارسی
                    continue
                    
                # فیلترهای منفی قوی
                if any(x in text for x in junk_indicators):
                    continue
                
                # حذف اگر خیلی شبیه لید است (تکراری)
                if lead_text and (text in lead_text or lead_text in text[:50]):
                    continue

                # دسته‌بندی
                # ۱. اولویت بالا: حاوی کلمات کلیدی و طول مناسب
                is_relevant = False
                if keywords:
                    match_count = sum(1 for kw in keywords if kw in text)
                    if match_count >= 1:
                        is_relevant = True
                
                if is_relevant and len(text) > 50:
                    if text not in high_priority:
                        high_priority.append(text)
                # ۲. اولویت متوسط: طولانی و تمیز (احتمالاً متن بدنه خبر)
                elif len(text) > 80:
                    if text not in medium_priority:
                        medium_priority.append(text)

            # ترکیب لیست‌ها
            # نکته: در ایران اینترنشنال معمولا متن‌های طولانی پشت سر هم هستند
            print(f"    [Brute Force] Found {len(high_priority)} high priority and {len(medium_priority)} medium priority blocks")
            
            # اول high priority ها را اضافه کن
            for p in high_priority:
                if p not in paragraphs:
                    paragraphs.append(p)
            
            # بعد medium priority ها (با محدودیت)
            for p in medium_priority:
                if p not in paragraphs:
                    paragraphs.append(p)
                    if len(paragraphs) > 15: # حداکثر ۱۵ پاراگراف
                        break 
            
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
        
        # ========== ساخت HTML محتوا ==========
        clean_html = ""
        for p in paragraphs:
            clean_html += f"<p style='margin-bottom: 15px; line-height: 2; text-align: justify;'>{p}</p>\n"
        
        if clean_html:
            result['full_content'] = clean_html
            # result['main_image'] هست، نیازی به تغییر نیست
            result['success'] = True
            print(f"    -> Got {len(paragraphs)} paragraphs (main article only)")
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
