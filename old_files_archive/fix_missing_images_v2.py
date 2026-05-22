"""
Fix Missing Images V2 - Smart Title-Based Search
اصلاح عکس‌های گمشده - جستجوی هوشمند بر اساس عنوان خبر

Strategy:
1. For each post without image, identify the likely source based on title patterns
2. Search for the article on iranhr.net by scraping their article listing pages
3. For iranintl.com, try constructing URLs or searching
4. For humanrightsinir.org, search their site
5. Fetch the article page and extract the image
6. Update the post
"""

import sys
import os
import re
import time
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blogger_poster import BloggerPoster
from news_fetcher import NewsFetcher, safe_print


def post_has_image(html_content):
    """Check if the post content contains any meaningful image."""
    if not html_content:
        return False
    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_content)
    for src in img_matches:
        src_lower = src.lower()
        if any(skip in src_lower for skip in ['logo', 'icon', 'avatar', 'pixel', 'badge', '1x1', 'spacer']):
            continue
        return True
    return False


def identify_source_from_title(title):
    """
    Guess which news source a post came from based on title patterns.
    Returns: source key like 'iranhr', 'iranintl', 'humanrightsinir', 'iranhrs', 'iran-hrm'
    """
    # IranHR.net patterns - execution reports, human rights specific language
    iranhr_patterns = [
        'اعدام', 'روایت‌های کشته‌شدگان', 'روایتهای کشتهشدگان',
        'زندانی سیاسی', 'بازداشت‌شدگان', 'بازداشتشدگان',
        'سازمان حقوق بشر ایران', 'احراز هویت',
        'جاویدنام', 'اعتراضات سراسری', 'فراخوان',
        'کمیته دفاع', 'نقض حقوق بشر', 'شکنجه',
        'گزارش نقض کمیته', 'اطلاعیه', 'شجاعت در قزلحصار',
        'دستکم', 'کشتار گسترده', 'شاهدان عینی',
        'زندان', 'حبس تعزیری', 'محکومیت',
        'نگرانی از وضعیت سلامت', 'فعالان مدنی',
        'مستندسازی سرکوب', 'کرامت انسانی',
        'خانواده‌های جاویدنامان', 'خانوادههای جاویدنامان',
        'نرگس محمدی', 'نسرین ستوده',
        'موج بازداشت', 'فاجعه انسانی', 'استثمار',
        'زندانیان سیاسی', 'شلیک مستقیم',
        'هشدار درباره', 'حکم اعدام',
        'بهائی', 'وضعیت زندان'
    ]
    
    # Iran International patterns - geopolitics, international news
    iranintl_patterns = [
        'ترامپ', 'نتانیاهو', 'اسرائیل', 'پنتاگون',
        'واشینگتن', 'کاخ سفید', 'رویترز',
        'آمریکا', 'اروپا', 'پارلمان',
        'تنگه هرمز', 'عربستان', 'بحرین', 'امارات',
        'حمله', 'حملات', 'انفجار', 'انفجارها',
        'ارتش اسرائیل', 'سپاه', 'جزیره خارک',
        'خامنه‌ای', 'خامنهای',
        'دیپلماتیک', 'نیویورک‌تایمز', 'نیویورکتایمز',
        'واشینگتن‌پست', 'واشینگتنپست',
        'هشدار تخلیه', 'نتبلاکس',
        'تعلیق حمله', 'پرستیوی',
        'ویتکاف', 'عراقچی',
        'لیندزی گراهام', 'نیومن',
        'سعار', 'کافه لمیز',
        'رسانه‌های ایران', 'رسانههای ایران',
        'شبکه', 'سفیر',
        'آرژانتین', 'استرالیا',
        'حمله موشکی', 'حمله گسترده',
        'خصوصیسازی', 'خصوصی‌سازی'
    ]
    
    # HumanRightsInIR patterns
    humanrightsinir_patterns = [
        'مدیر مسئول', 'روزنامه', 'دیوان عالی',
        'دادگاه انقلاب', 'تودیع وثیقه',
        'تفتیش منازل', 'شهروند بهایی',
        'فعال سیاسی', 'بازداشت موقت'
    ]
    
    # iran-hrm.com / iranhrs.org patterns
    iranhrs_patterns = [
        'ناظران حقوق بشر', 'کانون حقوق بشر'
    ]
    
    title_lower = title.lower()
    title_clean = title  # Keep original for pattern matching
    
    # Count matches for each source
    iranhr_score = sum(1 for p in iranhr_patterns if p in title_clean)
    iranintl_score = sum(1 for p in iranintl_patterns if p in title_clean)
    humanrightsinir_score = sum(1 for p in humanrightsinir_patterns if p in title_clean)
    iranhrs_score = sum(1 for p in iranhrs_patterns if p in title_clean)
    
    scores = {
        'iranhr': iranhr_score,
        'iranintl': iranintl_score,
        'humanrightsinir': humanrightsinir_score,
        'iranhrs': iranhrs_score
    }
    
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        # Default to iranhr for execution/rights topics, iranintl for political
        if any(kw in title_clean for kw in ['اعدام', 'زندان', 'حقوق بشر']):
            return 'iranhr'
        return 'iranintl'
    
    return best


class SmartImageFixer:
    def __init__(self):
        self.poster = BloggerPoster()
        self.fetcher = NewsFetcher()
        self.iranhr_articles = {}  # title -> url mapping
        self.iranhr_loaded = False
        self.progress_file = "fix_progress.json"
        self.fixed_ids = self._load_progress()
    
    def _load_progress(self):
        """Load previously fixed post IDs to allow resuming."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    return set(json.load(f))
            except:
                pass
        return set()
    
    def _save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(list(self.fixed_ids), f)
    
    def _build_iranhr_index(self):
        """Build iranhr.net article index using their JSON API."""
        if self.iranhr_loaded:
            return
        
        safe_print("[INDEX] Building iranhr.net article index via API...")
        
        # Try to load cached index
        cache_file = "iranhr_index.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.iranhr_articles = json.load(f)
                    self.iranhr_loaded = True
                    safe_print(f"  Loaded {len(self.iranhr_articles)} articles from cache")
                    return
            except:
                pass
        
        # Use iranhr.net's Django REST API
        # Returns JSON with: title_fa, image_fa, url, etc.
        api_base = "https://iranhr.net/fa/api/articles/"
        
        for page in range(1, 300):  # Up to 300 pages
            api_url = f"{api_base}?format=json&page={page}"
            
            if page % 20 == 1:
                safe_print(f"  [API] Fetching page {page}...")
            
            resp = self.fetcher._make_request(api_url, use_proxy=True, timeout=30)
            if not resp:
                safe_print(f"  [Warning] Could not fetch page {page}, stopping")
                break
            
            try:
                data = resp.json()
            except:
                safe_print(f"  [Warning] Invalid JSON on page {page}, stopping")
                break
            
            # Handle paginated API response
            results = []
            if isinstance(data, dict):
                results = data.get('results', data.get('articles', []))
                if not results and isinstance(data, list):
                    results = data
            elif isinstance(data, list):
                results = data
            
            if not results:
                safe_print(f"  No more articles on page {page}, stopping")
                break
            
            for article in results:
                title = article.get('title_fa', article.get('title', ''))
                url = article.get('url', '')
                image = article.get('image_fa', article.get('image', ''))
                article_id = article.get('id', '')
                
                if not title or not url:
                    continue
                
                # Build full URL if relative
                if url and not url.startswith('http'):
                    url = f"https://iranhr.net{url}"
                
                # Build full image URL if relative
                if image and not image.startswith('http'):
                    image = f"https://iranhr.net{image}"
                
                # Fix http -> https
                if image and image.startswith('http://'):
                    image = image.replace('http://', 'https://', 1)
                
                clean_title = self._normalize_title(title)
                # Store both URL and image_url for direct access
                self.iranhr_articles[clean_title] = {
                    'url': url,
                    'image': image,
                    'id': str(article_id)
                }
            
            time.sleep(0.3)  # Be polite
        
        # Save cache
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.iranhr_articles, f, ensure_ascii=False, indent=2)
            safe_print(f"  [OK] Cache saved")
        except Exception as e:
            safe_print(f"  [Warning] Could not save cache: {e}")
        
        self.iranhr_loaded = True
        safe_print(f"  [INDEX] Total: {len(self.iranhr_articles)} articles indexed")
    
    def _normalize_title(self, title):
        """Normalize title for fuzzy matching."""
        # Remove extra whitespace and common variations
        title = re.sub(r'\s+', ' ', title).strip()
        # Remove zero-width characters
        title = re.sub(r'[\u200c\u200d\u200e\u200f]', '', title)
        # Remove punctuation for matching
        title = re.sub(r'[؛،.:\-–—…!?»«]', '', title)
        return title.strip()
    
    def _find_iranhr_article(self, post_title):
        """Find matching article on iranhr.net by title. Returns dict with url and image."""
        self._build_iranhr_index()
        
        normalized = self._normalize_title(post_title)
        
        # Exact match
        if normalized in self.iranhr_articles:
            return self.iranhr_articles[normalized]
        
        # Fuzzy match - check if main words overlap
        post_words = set(normalized.split())
        best_match = None
        best_score = 0
        
        for cached_title, article_data in self.iranhr_articles.items():
            cached_words = set(cached_title.split())
            if len(post_words) == 0 or len(cached_words) == 0:
                continue
            
            overlap = len(post_words & cached_words)
            total = max(len(post_words), len(cached_words))
            score = overlap / total
            
            if score > best_score and score > 0.5:  # At least 50% word overlap
                best_score = score
                best_match = article_data
        
        if best_match:
            safe_print(f"  [Match] Score: {best_score:.0%}")
        
        return best_match
    
    def _find_iranintl_article_image(self, post_title, post_content=''):
        """Try to find image for Iran International articles using Playwright."""
        
        # Strategy 1: Extract original article URL from post content (data-source-url)
        article_url = None
        if post_content:
            # Look for data-source-url in post HTML
            source_match = re.search(r'data-source-url=["\']([^"\']+)["\']', post_content)
            if source_match:
                article_url = source_match.group(1)
                safe_print(f"  [IranIntl] Found source URL: {article_url[:60]}")
            
            # Also try to find iranintl.com link in post
            if not article_url:
                link_match = re.search(r'href=["\']([^"\']*iranintl\.com[^"\']*)["\']', post_content)
                if link_match:
                    article_url = link_match.group(1)
                    safe_print(f"  [IranIntl] Found link: {article_url[:60]}")
        
        # Strategy 2: Use Playwright to fetch the article page
        if article_url:
            result = self.fetcher._fetch_with_playwright(article_url)
            if result and result.get('image'):
                return result['image']
        
        # Strategy 3: Search iranintl.com with Playwright
        from urllib.parse import quote
        try:
            from playwright.sync_api import sync_playwright
            
            search_url = f"https://www.iranintl.com/search?q={quote(post_title[:50])}"
            safe_print(f"  [IranIntl] Playwright search: {search_url[:60]}...")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    viewport={'width': 1280, 'height': 720}
                )
                page = context.new_page()
                page.goto(search_url, wait_until='networkidle', timeout=15000)
                page.wait_for_timeout(3000)
                
                # Find first article link in search results
                first_link = page.evaluate('''
                    () => {
                        const links = document.querySelectorAll('a[href*="/20"]');
                        for (const a of links) {
                            const href = a.href || a.getAttribute('href');
                            if (href && href.includes('iranintl.com') && !href.includes('/search')) {
                                return href;
                            }
                        }
                        return null;
                    }
                ''')
                
                if first_link:
                    safe_print(f"  [IranIntl] Found article: {first_link[:60]}")
                    # Navigate to the article
                    page.goto(first_link, wait_until='networkidle', timeout=15000)
                    page.wait_for_timeout(2000)
                    
                    # Get og:image
                    og_image = page.evaluate('''
                        () => {
                            const meta = document.querySelector('meta[property="og:image"]');
                            return meta ? meta.getAttribute('content') : null;
                        }
                    ''')
                    browser.close()
                    
                    if og_image and 'logo' not in og_image.lower():
                        safe_print(f"  [IranIntl] Image found: {og_image[:80]}")
                        return og_image
                else:
                    browser.close()
        except ImportError:
            safe_print("  [IranIntl] Playwright not available")
        except Exception as e:
            safe_print(f"  [IranIntl] Error: {e}")
        
        return None
    
    def _find_humanrightsinir_article(self, post_title):
        """Search humanrightsinir.org for matching article."""
        # Try WordPress search
        from urllib.parse import quote
        search_url = f"https://humanrightsinir.org/?s={quote(post_title[:50])}"
        
        resp = self.fetcher._make_request(search_url, use_proxy=True)
        if not resp:
            return None
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # Find first matching article
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '')
            text = a_tag.get_text().strip()
            if 'humanrightsinir.org' in href and text and len(text) > 15:
                # Check if title matches
                if self._titles_match(post_title, text):
                    return href
        
        return None
    
    def _titles_match(self, title1, title2):
        """Check if two titles are similar enough to be the same article."""
        t1 = self._normalize_title(title1)
        t2 = self._normalize_title(title2)
        
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1 & words2)
        total = min(len(words1), len(words2))
        
        return overlap / total > 0.5
    
    def fix_post(self, post_id, title, content):
        """Fix a single post by finding and adding its image."""
        source = identify_source_from_title(title)
        safe_print(f"  [Source?] {source}")
        
        article_url = None
        image_url = None
        
        if source == 'iranhr':
            match = self._find_iranhr_article(title)
            if match:
                if isinstance(match, dict):
                    article_url = match.get('url', '')
                    image_url = match.get('image', '')
                    safe_print(f"  [URL] {article_url}")
                    
                    # If API didn't have image, try fetching the page
                    if not image_url and article_url:
                        result = self.fetcher.fetch_full_article(article_url, 'iranhr')
                        image_url = result.get('main_image')
                else:
                    # Legacy format - plain URL string
                    article_url = match
                    safe_print(f"  [URL] {article_url}")
                    result = self.fetcher.fetch_full_article(article_url, 'iranhr')
                    image_url = result.get('main_image')
        
        elif source == 'humanrightsinir':
            article_url = self._find_humanrightsinir_article(title)
            if article_url:
                safe_print(f"  [URL] {article_url}")
                result = self.fetcher.fetch_full_article(article_url, 'humanrightsinir')
                image_url = result.get('main_image')
        
        elif source == 'iranintl':
            image_url = self._find_iranintl_article_image(title, content)
        
        # Validate image URL - reject placeholders, SVGs, logos etc.
        if image_url:
            img_lower = image_url.lower()
            if any(bad in img_lower for bad in ['placeholder', '.svg', 'logo', 'icon', 'avatar', '1x1', 'spacer', 'pixel']):
                safe_print(f"  [Skip] Invalid image (placeholder/svg/logo): {image_url[:60]}")
                image_url = None
        
        if not image_url:
            return False
        
        safe_print(f"  [Image] {image_url[:80]}")
        
        # Build image HTML and insert into post
        image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{image_url}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>'
        
        new_content = content
        style_end = content.find('</style>')
        if style_end != -1:
            insert_pos = style_end + len('</style>')
            new_content = content[:insert_pos] + '\n' + image_html + '\n' + content[insert_pos:]
        else:
            new_content = image_html + '\n' + content
        
        # Update via Blogger API
        try:
            body = {
                'id': post_id,
                'content': new_content,
            }
            self.poster.service.posts().patch(
                blogId=self.poster.blog_id,
                postId=post_id,
                body=body
            ).execute()
            
            self.fixed_ids.add(post_id)
            self._save_progress()
            return True
        except Exception as e:
            safe_print(f"  [ERROR] API: {e}")
            return False
    
    def run(self):
        """Scan all posts and fix those with missing images."""
        print("=" * 60)
        print("  Smart Image Fixer V2")
        print("  Searches news sources by title to find images")
        print("=" * 60)
        
        page_token = None
        total = 0
        no_image = 0
        fixed = 0
        skipped = 0
        failed = []
        
        while True:
            try:
                params = {'blogId': self.poster.blog_id, 'maxResults': 50}
                if page_token:
                    params['pageToken'] = page_token
                
                resp = self.poster.service.posts().list(**params).execute()
                posts = resp.get('items', [])
                if not posts:
                    break
                
                for post in posts:
                    total += 1
                    content = post.get('content', '')
                    title = post.get('title', '')
                    post_id = post.get('id', '')
                    
                    if post_has_image(content):
                        continue
                    
                    no_image += 1
                    
                    # Skip already fixed
                    if post_id in self.fixed_ids:
                        skipped += 1
                        continue
                    
                    safe_title = title[:60].encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                    print(f"\n[#{total}] {safe_title}...")
                    
                    if self.fix_post(post_id, title, content):
                        fixed += 1
                        print(f"  ✅ FIXED!")
                        time.sleep(3)  # Rate limiting
                    else:
                        failed.append({'id': post_id, 'title': title})
                        print(f"  ❌ Could not find image")
                
                page_token = resp.get('nextPageToken')
                if not page_token:
                    break
            except Exception as e:
                print(f"\n[ERROR] {e}")
                break
        
        # Summary
        print("\n" + "=" * 60)
        print(f"  RESULTS")
        print(f"  Total scanned: {total}")
        print(f"  Without images: {no_image}")
        print(f"  Fixed now: {fixed}")
        print(f"  Previously fixed: {skipped}")
        print(f"  Still need fixing: {len(failed)}")
        print("=" * 60)
        
        # Categorize failed by source
        source_counts = {}
        for fp in failed:
            src = identify_source_from_title(fp['title'])
            source_counts[src] = source_counts.get(src, 0) + 1
        
        if source_counts:
            print("\n  Remaining by source:")
            for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
                print(f"    {src}: {count} posts")


if __name__ == '__main__':
    fixer = SmartImageFixer()
    fixer.run()
