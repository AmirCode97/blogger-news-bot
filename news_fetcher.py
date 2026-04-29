
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

# Try to import cloudscraper for Cloudflare bypass
try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False
    print("[WARNING] cloudscraper not installed. Install with: pip install cloudscraper")

# Try to import playwright for JS-rendered SPA sites (e.g. iranintl.com)
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("[WARNING] playwright not installed. Install with: pip install playwright && playwright install chromium")

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
        # Setup cloudscraper session for Cloudflare-protected sites
        if HAS_CLOUDSCRAPER:
            self.cf_session = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
            )
        else:
            self.cf_session = None

    def _get_proxy(self) -> Optional[Dict]:
        if not USE_PROXY: return None
        if PROXY_URL: return {'http': PROXY_URL, 'https': PROXY_URL}
        if FREE_PROXIES:
            proxy = random.choice(FREE_PROXIES)
            self.current_proxy = proxy
            return {'http': proxy, 'https': proxy}
        return None

    def _is_cloudflare_site(self, url: str) -> bool:
        """Check if the URL belongs to a known Cloudflare-protected site."""
        cf_domains = ['iranhr.net', 'hra-news.org']
        return any(domain in url for domain in cf_domains)

    def _make_request(self, url: str, use_proxy: bool = False, timeout: int = 30) -> Optional[requests.Response]:
        proxies = self._get_proxy() if use_proxy else None
        
        # For Cloudflare-protected sites, use cloudscraper first
        if self._is_cloudflare_site(url) and self.cf_session:
            try:
                safe_print(f"  [CF] Using cloudscraper for {url[:60]}...")
                response = self.cf_session.get(url, timeout=timeout)
                if response.status_code == 200:
                    return response
                else:
                    safe_print(f"  [CF] Status {response.status_code}")
            except Exception as e:
                safe_print(f"  [CF] Error: {e}")
        
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
            
            response = self._make_request(url, use_proxy=True)
            if not response:
                safe_print(f"  [Error] Could not fetch RSS XML")
                return []
                
            feed = feedparser.parse(response.content)
            
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
            
            # ==== Iran International (SPA - needs Playwright) ====
            if 'iranintl.com' in url:
                # First try Playwright for full JS rendering
                if HAS_PLAYWRIGHT:
                    pw_result = self._fetch_with_playwright(url)
                    if pw_result:
                        if pw_result.get('image'):
                            main_image = pw_result['image']
                        if pw_result.get('content'):
                            # Clean audio player / share / timestamp junk from content
                            cleaned = self._clean_iranintl_content(pw_result['content'])
                            if cleaned:
                                paragraphs = [cleaned]
                
                # Fallback: try static extraction from initial HTML
                if not main_image:
                    og_img = soup.find('meta', property='og:image')
                    if og_img:
                        main_image = og_img.get('content')
                
                if not paragraphs:
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
            
            # ==== IranHR.net (Cloudflare-protected) ====
            elif 'iranhr.net' in url:
                # Content extraction
                content_div = soup.find('div', class_='context') or soup.find('article') or soup.find('div', class_='col-md-8')
                if content_div:
                    for p in content_div.find_all(['p', 'h2', 'h3']):
                        text = p.get_text().strip()
                        if len(text) > 50 and 'cookie' not in text.lower():
                            if text not in paragraphs:
                                paragraphs.append(text)
                
                # Image: Try .main-image first (iranhr.net specific)
                main_img_div = soup.find('div', class_='main-image') or soup.find('img', class_='main-image')
                if main_img_div:
                    img_tag = main_img_div.find('img') if main_img_div.name == 'div' else main_img_div
                    if img_tag:
                        src = img_tag.get('src') or img_tag.get('data-src')
                        if src:
                            main_image = urljoin(url, src)
                            # Fix http:// to https://
                            if main_image.startswith('http://'):
                                main_image = main_image.replace('http://', 'https://', 1)
                
                # Fallback: og:image
                if not main_image:
                    og_img = soup.find('meta', property='og:image')
                    if og_img:
                        main_image = og_img.get('content', '')
                        # iranhr.net og:image uses http://, fix to https://
                        if main_image.startswith('http://'):
                            main_image = main_image.replace('http://', 'https://', 1)
                
                if main_image:
                    safe_print(f"  [IranHR] Image found: {main_image[:80]}")
            
            # ==== Iran HRS / Iran-HRM ====
            elif 'iranhrs.org' in url or 'iran-hrm.com' in url:
                # Try entry-content first
                content_div = soup.find('div', class_='entry-content') or soup.find('article')
                if content_div:
                    for p in content_div.find_all(['p', 'h2', 'h3']):
                        text = p.get_text().strip()
                        if len(text) > 50 and 'cookie' not in text.lower():
                            if text not in paragraphs:
                                paragraphs.append(text)
                
                # Image
                og_img = soup.find('meta', property='og:image')
                if og_img:
                    main_image = og_img.get('content')
                elif content_div:
                    img = content_div.find('img')
                    if img:
                        main_image = urljoin(url, img.get('src', ''))
            
            # ==== HumanRightsInIR.org (WordPress) ====
            elif 'humanrightsinir.org' in url:
                # Content extraction
                content_div = soup.find('div', class_='entry-content') or soup.find('article')
                if content_div:
                    for p in content_div.find_all(['p']):
                        text = p.get_text().strip()
                        if len(text) > 50 and 'cookie' not in text.lower():
                            paragraphs.append(text)
                
                # Image: wp-post-image is the real article image, NOT og:image (which is generic logo)
                wp_img = soup.find('img', class_='wp-post-image')
                if not wp_img:
                    # Try thumbnail container
                    thumb_div = soup.find('div', class_=re.compile(r'thumb|featured|post-image'))
                    if thumb_div:
                        wp_img = thumb_div.find('img')
                if wp_img:
                    src = wp_img.get('src') or wp_img.get('data-src') or wp_img.get('data-lazy-src')
                    if src:
                        main_image = urljoin(url, src)
                        safe_print(f"  [HumanRightsInIR] Image: {main_image[:80]}")
                
                # Only use og:image as last resort, and skip if it's a generic logo
                if not main_image:
                    og_img = soup.find('meta', property='og:image')
                    if og_img:
                        og_url = og_img.get('content', '')
                        # Skip generic logos/placeholders
                        if og_url and 'cropped-' not in og_url and 'logo' not in og_url.lower():
                            main_image = og_url
            
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
            
            # =============================================
            # UNIVERSAL FALLBACK: If still no image, try harder
            # =============================================
            if not main_image:
                main_image = self._extract_fallback_image(soup, url)
            
            # Build full text
            full_text = "\n\n".join(paragraphs[:15]) if paragraphs else ""
            
            # Log results
            if full_text:
                safe_print(f"  [OK] Extracted {len(paragraphs)} paragraphs, {len(full_text)} chars")
            else:
                safe_print(f"  [Warning] No content extracted")
            
            if main_image:
                safe_print(f"  [Image] {main_image[:80]}")
            else:
                safe_print(f"  [Warning] No image found")
            
            return {
                'success': len(full_text) > 50,
                'full_content': full_text,
                'main_image': main_image
            }
            
        except Exception as e:
            safe_print(f"  [Error] Parse: {e}")
            return {'success': False, 'full_content': '', 'main_image': None}

    def _extract_fallback_image(self, soup, url: str) -> Optional[str]:
        """
        Universal fallback image extraction when source-specific handlers fail.
        Tries multiple strategies in order of reliability.
        """
        # Strategy 1: og:image
        og_img = soup.find('meta', property='og:image')
        if og_img:
            img_url = og_img.get('content', '')
            if img_url and 'logo' not in img_url.lower() and 'icon' not in img_url.lower():
                return img_url
        
        # Strategy 2: twitter:image
        twitter_img = soup.find('meta', {'name': 'twitter:image'})
        if twitter_img:
            img_url = twitter_img.get('content', '')
            if img_url:
                return img_url
        
        # Strategy 3: JSON-LD image
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    img = data.get('image')
                    if isinstance(img, str) and img:
                        return img
                    elif isinstance(img, dict):
                        return img.get('url', '')
                    elif isinstance(img, list) and len(img) > 0:
                        first = img[0]
                        return first if isinstance(first, str) else first.get('url', '')
            except:
                pass
        
        # Strategy 4: First large image in article content
        content_area = soup.find('article') or soup.find('div', class_=re.compile(r'content|entry|post'))
        if content_area:
            for img in content_area.find_all('img'):
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if not src:
                    continue
                # Skip tiny icons, avatars, logos
                width = img.get('width', '')
                height = img.get('height', '')
                if width and int(width) < 100:
                    continue
                if height and int(height) < 100:
                    continue
                src_lower = src.lower()
                if any(skip in src_lower for skip in ['logo', 'icon', 'avatar', 'emoji', 'gravatar', 'pixel', 'badge']):
                    continue
                return urljoin(url, src)
        
        return None

    def _clean_iranintl_content(self, text: str) -> str:
        """
        Clean Iran International content by removing audio player,
        share buttons, and timestamp UI text that gets scraped accidentally.
        """
        if not text:
            return text
        
        # Patterns to remove (audio player, share, timestamps, etc.)
        junk_patterns = [
            # Audio player text: "پخش نسخه شنیداری" (Play audio version)
            r'پخش\s*نسخه\s*شنیداری',
            # Share button: "اشتراک‌گذاری" or "اشتراکگذاری"
            r'اشتراک[‌\u200c]?گذاری',
            # Timestamps: "۲۴ دقیقه پیش" or "۳ ساعت پیش" etc.
            r'[۰-۹\d]+\s*دقیقه\s*پیش',
            r'[۰-۹\d]+\s*ساعت\s*پیش',
            r'[۰-۹\d]+\s*روز\s*پیش',
            # "لحظاتی پیش" (moments ago)
            r'لحظاتی\s*پیش',
            # Play/pause icons or labels
            r'►\s*پخش',
            r'▶\s*پخش',
            # "نسخه شنیداری" alone
            r'نسخه\s*شنیداری',
            # "بازپخش" (replay)
            r'بازپخش',
            # Bookmark / save
            r'ذخیره\s*کردن',
            r'نشان‌گذاری',
            # Copy link
            r'کپی\s*لینک',
            r'رونوشت\s*لینک',
        ]
        
        cleaned = text
        for pattern in junk_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Remove multiple consecutive blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned

    def _fetch_with_playwright(self, url: str, timeout: int = 15000) -> Optional[Dict]:
        """
        Fetch a page using Playwright headless browser.
        Used for JS-rendered SPA sites like iranintl.com.
        Returns dict with 'image' and 'content' keys, or None on failure.
        """
        if not HAS_PLAYWRIGHT:
            return None
        
        safe_print(f"  [PW] Opening headless browser for {url[:60]}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    viewport={'width': 1280, 'height': 720}
                )
                page = context.new_page()
                
                # Navigate and wait for network to settle
                page.goto(url, wait_until='networkidle', timeout=timeout)
                
                # Wait a bit for any remaining JS rendering
                page.wait_for_timeout(2000)
                
                result = {}
                
                # Extract og:image from rendered page
                og_image = page.evaluate('''
                    () => {
                        const meta = document.querySelector('meta[property="og:image"]');
                        return meta ? meta.getAttribute('content') : null;
                    }
                ''')
                if og_image and not any(bad in og_image.lower() for bad in ['logo', 'placeholder', '.svg', 'icon', 'spacer']):
                    result['image'] = og_image
                    safe_print(f"  [PW] og:image found: {og_image[:80]}")
                
                # Try to find article image from rendered DOM
                if not result.get('image'):
                    article_image = page.evaluate('''
                        () => {
                            // Try common article image selectors
                            const selectors = [
                                'article img[src]',
                                '.article-image img[src]',
                                '.post-image img[src]',
                                '.featured-image img[src]',
                                'picture img[src]',
                                'main img[src]'
                            ];
                            for (const sel of selectors) {
                                const img = document.querySelector(sel);
                                if (img) {
                                    const src = img.src || img.getAttribute('src');
                                    if (src && !src.includes('logo') && !src.includes('icon') && !src.includes('avatar')) {
                                        return src;
                                    }
                                }
                            }
                            return null;
                        }
                    ''')
                    if article_image and not any(bad in article_image.lower() for bad in ['placeholder', '.svg', 'logo', 'spacer']):
                        result['image'] = article_image
                        safe_print(f"  [PW] Article image found: {article_image[:80]}")
                
                # Extract article content
                article_content = page.evaluate('''
                    () => {
                        // Strategy 1: Get only <p> text from article content area (excludes header/tools/audio)
                        const contentDiv = document.querySelector('[class*="ArticleLayout"][class*="content"]')
                            || document.querySelector('article [class*="content"]');
                        if (contentDiv) {
                            const ps = contentDiv.querySelectorAll('p');
                            if (ps.length > 0) {
                                const texts = [];
                                ps.forEach(p => {
                                    const t = p.innerText.trim();
                                    if (t.length > 20) texts.push(t);
                                });
                                if (texts.length > 0) return texts.join('\n\n');
                            }
                        }
                        
                        // Strategy 2: Get all <p> from article, skip header elements
                        const article = document.querySelector('article');
                        if (article) {
                            // Remove header and tools sections before extracting
                            const clone = article.cloneNode(true);
                            clone.querySelectorAll('header, [class*="tools"], [class*="share"], [class*="audio"], nav, footer').forEach(el => el.remove());
                            const ps = clone.querySelectorAll('p');
                            if (ps.length > 0) {
                                const texts = [];
                                ps.forEach(p => {
                                    const t = p.innerText.trim();
                                    if (t.length > 20) texts.push(t);
                                });
                                if (texts.length > 0) return texts.join('\n\n');
                            }
                        }
                        
                        // Strategy 3: Fallback to generic selectors
                        const selectors = ['.article-body', '.post-content', 'main'];
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el && el.innerText.length > 100) {
                                return el.innerText.substring(0, 2000);
                            }
                        }
                        return null;
                    }
                ''')
                if article_content:
                    result['content'] = article_content
                
                browser.close()
                
                if result:
                    safe_print(f"  [PW] Success!")
                    return result
                else:
                    safe_print(f"  [PW] No content extracted")
                    return None
                
        except Exception as e:
            safe_print(f"  [PW] Error: {e}")
            return None


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
