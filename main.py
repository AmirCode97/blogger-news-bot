
import os
import sys

# Reconfigure standard output and error streams to UTF-8 to prevent 'charmap' encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import re
import time
import schedule
from datetime import datetime, timedelta

def deduplicate_text(text):
    """Detect and remove duplicated text content.
    If the text contains the same content repeated twice, keep only the first occurrence."""
    if not text or len(text) < 50:
        return text
    
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    unique_paragraphs = []
    seen = set()
    
    for p in paragraphs:
        # Simplify paragraph for comparison
        clean_p = re.sub(r'[^\w\s]', '', p).strip()
        words = clean_p.split()
        
        # We need at least 5 words to consider it a deduplicable sentence
        if len(words) < 5:
            unique_paragraphs.append(p)
            continue
            
        fingerprint = " ".join(words[:40]) # check up to 40 words
        
        if fingerprint not in seen:
            seen.add(fingerprint)
            unique_paragraphs.append(p)
        else:
            print(f"  [Dedup] Removed duplicated paragraph: len={len(p)}")

    return "\n\n".join(unique_paragraphs)

def download_and_optimize_image(url: str) -> str:
    """
    Downloads an image from the given URL, resizes it, converts to WebP,
    saves it to the local 'images' directory, and returns the raw GitHub URL.
    """
    if not url:
        return ""
    if "jsdelivr.net" in url or "raw.githubusercontent.com" in url or url.startswith("data:"):
        return url
        
    try:
        import os
        import hashlib
        
        # Generate a unique filename based on the URL hash
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:16]
        filename = f"{url_hash}.webp"
        filepath = os.path.join("images", filename)
        
        # If already downloaded, return the raw GitHub URL
        github_cdn_url = f"https://raw.githubusercontent.com/AmirCode97/blogger-news-bot/main/images/{filename}"
        if os.path.exists(filepath):
            return github_cdn_url
            
        import requests
        from PIL import Image
        from io import BytesIO
        
        print(f"  [Image Download] Fetching {url[:60]}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com/',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'fa,en-US;q=0.9,en;q=0.8'
        }
        
        # Bypassing Cloudflare/anti-bot blocks using cloudscraper if available
        try:
            import cloudscraper
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
            )
            resp = scraper.get(url, timeout=15)
            if resp.status_code == 403:
                # Fallback to standard requests if cloudscraper failed
                resp = requests.get(url, headers=headers, timeout=15)
        except Exception as e:
            print(f"  [Cloudscraper Note] Fallback to requests: {e}")
            resp = requests.get(url, headers=headers, timeout=15)
            
        resp.raise_for_status()
        
        img = Image.open(BytesIO(resp.content))
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if img.width > 800:
            ratio = 800.0 / float(img.width)
            new_height = int(float(img.height) * float(ratio))
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)
            
        os.makedirs("images", exist_ok=True)
        img.save(filepath, format="WEBP", quality=75)
        print(f"  [Image Saved] Saved optimized image to {filepath}")
        
        return github_cdn_url
    except Exception as e:
        print(f"  [Image Error] Failed to download/optimize image: {e}")
        from urllib.parse import quote
        return f"https://wsrv.nl/?url={quote(url)}"



def proxy_external_image(url):
    if not url:
        return ""
    # Already on CDN or data URL or empty
    if "jsdelivr.net" in url or "raw.githubusercontent.com" in url or url.startswith("data:"):
        return url
    from urllib.parse import quote
    # wsrv.nl is a free, fast global image cache proxy unblocked in Iran
    return f"https://wsrv.nl/?url={quote(url)}"

def validate_image_url(url: str, timeout: int = 6) -> bool:
    """
    Verify image URL is actually accessible before publishing.
    Returns True if the image can be fetched, False otherwise.
    jsdelivr CDN and raw.githubusercontent.com URLs are trusted directly without a network check.
    """
    if not url:
        return False
    # Trust our own CDN stock images directly
    if "jsdelivr.net" in url or "raw.githubusercontent.com" in url:
        return True
    try:
        from urllib.parse import quote as _quote
        check_url = f"https://wsrv.nl/?url={_quote(url)}" if "wsrv.nl" not in url else url
        resp = requests.head(check_url, timeout=timeout, allow_redirects=True)
        return resp.status_code == 200
    except Exception:
        return False

def strip_markdown(text):
    """Remove all Markdown formatting symbols from text while preserving the actual content."""
    if not text:
        return text
    # Remove heading markers (##, ###, etc.)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Remove bold+italic (***text*** or ___text___)
    text = re.sub(r'\*{3}(.+?)\*{3}', r'\1', text)
    text = re.sub(r'_{3}(.+?)_{3}', r'\1', text)
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*{2}(.+?)\*{2}', r'\1', text)
    text = re.sub(r'_{2}(.+?)_{2}', r'\1', text)
    # Remove italic (*text* or _text_) - careful not to break normal underscores
    text = re.sub(r'(?<!\w)\*([^\*\n]+?)\*(?!\w)', r'\1', text)
    # Remove inline code (`text`)
    text = re.sub(r'`([^`]+?)`', r'\1', text)
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove blockquote markers (> text)
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove bullet point markers (* item, - item) at start of lines
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    # Remove numbered list markers (1. item)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Remove any remaining standalone ** or ***
    text = re.sub(r'\*{2,3}', '', text)
    # Remove === markers that weren't parsed
    text = re.sub(r'={3,}[A-Z]+={3,}', '', text)
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def strip_ai_noise(text):
    """Remove AI meta-commentary, analysis, and thinking-out-loud lines that should not appear in blog posts."""
    if not text:
        return text
    # Patterns that indicate AI analysis/commentary (not actual news content)
    noise_patterns = [
        r'^.*بسیار عالی.*$',
        r'^.*با توجه به نقش.*$',
        r'^.*پیشنهادات بازنویسی.*$',
        r'^.*سناریوی \d.*$',
        r'^.*عنوان پیشنهادی.*$',
        r'^.*گزینه [الفب].*$',
        r'^.*چرا\?\!?\?.*$',
        r'^.*نکات سئو.*$',
        r'^.*محتوای پیشنهادی.*$',
        r'^.*بهینه‌سازی برای جستجو.*$',
        r'^.*لینک‌سازی داخلی.*$',
        r'^.*عنوان اصلی \(پیشنهادی.*$',
        r'^.*تاکید بر فوریت.*$',
        r'^.*تاکید بر گستردگی.*$',
        r'^.*ساختار پاراگراف.*$',
        r'^.*کلمات کلیدی در عنوان.*$',
        r'^.*قالب‌بندی:.*$',
        r'^.*خوانایی:.*$',
        r'^.*first appeared on.*$',
        r'^.*The post.*appeared.*$',
        r'^.*بازنویسی می‌کنم.*$',
        r'^.*تمرکز بر سردبیری.*$',
        r'^.*مناسب برای تیتر.*$',
        r'^.*بار دراماتیک.*$',
        r'^.*مخاطب را به خواندن.*$',
        r'^.*عنوان:\s*$',
        r'^.*محتوا:\s*$',
        r'^.*پیوند اول:.*$',
        r'^.*اطلاعات تکمیلی:\s*$',
        r'^.*توضیحات\s*\(Meta Description\).*$',
        r'^.*در صورتی که خبرگزاری.*$',
        r'^.*تاریخ انتشار.*در انتهای متن.*$',
        r'^.*درج واضح منبع.*$',
        r'^.*استفاده از لیست.*$',
        r'^.*استفاده از جملات کوتاه.*$',
        r'^.*عنوان \(Title\).*$',
        r'^.*عنوان خبری و مستقیم.*$',
        r'^.*محتوای بازنویسی شده.*$',
        r'^.*هشدار شدید حقوق بشر.*$',
        r'^.*عنوان اصلی \(پیشنهادی.*$',
        r'^.*چرا\?\?.*$',
        r'^.*گستردگی را نشان.*$',
        r'^.*احساس فوریت و اهمیت.*$',
        r'^.*کلمات کلیدی قوی.*$',
        r'^.*موتورهای جستجو.*مفید.*$',
        r'^.*کمک می‌کند تا اطلاعات.*$',
        r'^.*حفظ اعتبار.*$',
        r'^.*سئو بسیار مهم.*$',
        r'^.*در یک سناریوی واقعی.*$',
        r'^.*رعایت شده.*$',
        r'^.*خبرگزاری در ابتدای.*$',
        r'^.*اضافه کردن نام.*$',
        r'^.*توضیح:.*در خروجی بالا.*$',
        r'^.*در پاراگراف اول پوشش.*$',
        r'^.*صفحه به صورت ضمنی.*$',
        r'^.*منابع معتبر.*دیده می‌شود.*$',
        r'^.*جذابیت یا اطلاعاتی ندارد.*$',
        r'^.*عبارت به طور معمول.*$',
        r'^.*حاوی کلمات کلیدی اصلی.*$',
    ]
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            clean_lines.append(line)
            continue
        is_noise = False
        for pattern in noise_patterns:
            if re.search(pattern, stripped):
                is_noise = True
                break
        if not is_noise:
            clean_lines.append(line)
    return '\n'.join(clean_lines)

from typing import List, Dict

from config import (
    BLOG_ID, 
    MAX_NEWS_PER_CHECK, 
    CHECK_INTERVAL_HOURS
)
from news_fetcher import NewsFetcher
from ai_processor import AIProcessor
from blogger_poster import BloggerPoster
from duplicate_detector import DuplicateDetector

class BloggerNewsBot:
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.duplicate_detector = DuplicateDetector()  # Advanced duplicate detection
        self.ai = None
        self.blogger = None
        self.resolved_images = {}
        
        print("[INFO] Initializing Blogger News Bot...")
        print(f"[INFO] Blog ID: {BLOG_ID}")
        print(f"[INFO] Check interval: Every {CHECK_INTERVAL_HOURS} hours")
        
        # Load resolved stock images mappings
        try:
            import json
            resolved_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resolved_images.json")
            if os.path.exists(resolved_path):
                with open(resolved_path, "r", encoding="utf-8") as f:
                    self.resolved_images = json.load(f)
                print(f"[OK] Loaded {len(self.resolved_images)} resolved stock images.")
            else:
                print("[WARNING] resolved_images.json not found!")
        except Exception as e:
            print(f"[ERROR] Loading resolved_images.json: {e}")

        print(f"[INFO] Duplicate cache: {self.duplicate_detector.get_stats()}")

    def _init_ai(self):
        if not self.ai:
            self.ai = AIProcessor()
            print("[OK] AI Processor initialized")

    def _init_blogger(self):
        if not self.blogger:
            try:
                self.blogger = BloggerPoster()
                print("[OK] Blogger API initialized")
            except Exception as e:
                print(f"[ERROR] Blogger initialization failed: {e}")

    def fetch_and_process_news(self):
        print("\n" + "="*60)
        print(f"Starting news fetch at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        news_items = self.fetcher.fetch_all_news(max_items=MAX_NEWS_PER_CHECK)
        
        if not news_items:
            print("[INFO] No new relevant news found")
            return
        
        self._init_ai()
        self._init_blogger()
        
        
        published_count = 0
        posted_titles = []
        
        for item in news_items:
            try:
                # 1. TIME FILTER: Skip older than 24h
                pub_date_str = item.get('published')
                if pub_date_str:
                    try:
                        pub_date = datetime.fromisoformat(pub_date_str)
                        if datetime.now() - pub_date > timedelta(hours=24):
                            print(f"  [Skip] News too old ({pub_date.strftime('%Y-%m-%d')}): {item['title'][:50]}")
                            continue
                    except:
                        pass
                
                # 2. ADVANCED DUPLICATE CHECK
                is_dup, dup_reason = self.duplicate_detector.is_duplicate(
                    item['title'], 
                    item.get('link', ''),
                    item.get('description', '')
                )
                if is_dup:
                    safe_title = item['title'][:40].encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                    print(f"  [SKIP] Duplicate: {safe_title}... ({dup_reason})")
                    continue

                safe_title = item['title'][:50].encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                print(f"\nProcessing: {safe_title}...")
                
                # Prepare content
                article_link = item.get('link', '')
                article_title = item['title']
                
                print(f"  [Fetching] Getting full content...")
                full_article = self.fetcher.fetch_full_article(article_link, item.get('source', ''))
                
                # Get content from article or fallback to item description
                description = full_article.get('full_content', '') if full_article.get('success') else ''
                if not description:
                    description = item.get('description', '')
                
                main_image = full_article.get('main_image') or item.get('image_url', '')
                
                # If still no content, use AI to GENERATE content from title
                if not description or len(description) < 50:
                    print(f"  [Warning] No content found, asking AI to generate from title...")
                    description = f"[این خبر نیاز به تحلیل دارد: {article_title}]"

                # Call AI for Multi-language processing
                # This also fixes content if it was minimal
                if self.ai:
                    print(f"  [AI] Paraphrasing and generating unique title...")
                    processed_title, ai_response = self.ai.process_news(article_title, description)
                    
                    # Update title to the unique one generated by AI
                    article_title = processed_title
                    
                    # Parse AI response - Persian only (no translations)
                    final_fa = description # Fallback
                    meta_description = ""
                    
                    if "===PERSIAN===" in ai_response:
                        try:
                            persian_part = ai_response.split("===PERSIAN===")[1]
                            # Remove other sections if present
                            for marker in ["===TAGS===", "===METADESCRIPTION===", "===ENGLISH===", "===GERMAN==="]:
                                if marker in persian_part:
                                    persian_part = persian_part.split(marker)[0]
                            final_fa = persian_part.strip()
                        except:
                            pass
                    elif len(ai_response) > 100: 
                        # If AI failed to structure but returned long text, use it
                        final_fa = ai_response

                    if "===METADESCRIPTION===" in ai_response:
                        try:
                            meta_part = ai_response.split("===METADESCRIPTION===")[1]
                            for marker in ["===PERSIAN===", "===TAGS===", "===TITLE==="]:
                                if marker in meta_part:
                                    meta_part = meta_part.split(marker)[0]
                            meta_description = meta_part.strip()
                        except:
                            pass
                    
                    # CLEAN AI OUTPUT: Remove Markdown symbols and AI analysis noise
                    final_fa = strip_ai_noise(final_fa)
                    final_fa = strip_markdown(final_fa)
                    article_title = strip_markdown(article_title)
                    meta_description = strip_markdown(meta_description)
                    
                    # Ensure meta_description is populated as fallback
                    if not meta_description:
                        paragraphs = [p.strip() for p in final_fa.split('\n') if p.strip()]
                        if paragraphs:
                            meta_description = paragraphs[0][:160]
                            if len(paragraphs[0]) > 160:
                                meta_description += "..."
                        else:
                            meta_description = final_fa[:160] + "..."
                            
                    description = final_fa
                else:
                    pass

                # VALIDATE: Skip if no content was extracted
                if not description or len(description) < 50:
                    print(f"  [SKIP] No content extracted for this article")
                    continue
                
                # DEDUPLICATION CHECK: Remove any repeated text content
                description = deduplicate_text(description)
                
                print(f"  [Content] {len(description)} characters")
                
                source_name = item.get('source', 'Source')
                search_text = (article_title + " " + description).lower()
                
                # ==========================================
                # 1. Smart Label Classification
                # ==========================================
                post_labels = []
                worker_keywords = ['کارگر', 'کارگران', 'اعتصاب', 'حقوق معوقه', 'سندیکا', 'کولبر', 'سوخت‌بر', 'اخراج', 'بازنشستگان', 'حداقل دستمزد', 'حوادث کار']
                prisoner_keywords = ['زندان', 'بازداشت', 'اوین', 'اعدام', 'حبس', 'وثیقه', 'سلول انفرادی', 'اعتصاب غذا', 'شکنجه', 'بند نسوان', 'زندانی سیاسی']
                
                # Check for Worker-related news across all sources
                if any(kw in search_text for kw in worker_keywords):
                    post_labels.append('کارگران')
                
                # Check for Prisoner/Execution-related news across all sources
                if any(kw in search_text for kw in prisoner_keywords):
                    post_labels.append('وضعیت زندانیان')
                
                # Fallback to category based on source or general human rights if no specific matches
                if not post_labels:
                    if 'ایران اینترنشنال' in source_name:
                        post_labels.append('بین‌الملل')
                    else:
                        post_labels.append('حقوق بشر')
                
                post_labels = list(set(post_labels))
                
                # ==========================================
                # 2. Cinematic Image Override for Workers
                # ==========================================
                if 'کارگران' in post_labels and not main_image:
                    import random
                    
                    # دسته‌بندی عکس‌ها بر اساس موضوع خبر
                    worker_image_categories = {
                        'protest': {  # تجمع و اعتراض صنفی
                            'keywords': ['تجمع', 'اعتراض', 'تحصن', 'اعتصاب', 'صنفی', 'راهپیمایی', 'تظاهرات'],
                            'images': [
                                "xvVwjvWLG5ADOxW4EIgY",
                                "7kyrBNbl4c2KS8vircgB",
                                "3XhhBrieVpJFtVtLookz",
                            ]
                        },
                        'safety': {  # فقدان ایمنی کار
                            'keywords': ['ایمنی', 'حادثه', 'حوادث کار', 'سقوط', 'انفجار', 'آتش‌سوزی'],
                            'images': [
                                "dxiHs3AT6IjhOmWZTBaR",
                                "tFZVcFQcUPRmG9hAknot",
                                "NXgu2fiLV7oKWSt5JUuh",
                                "JjVnVdCMXy6iolMIDaZj",
                                "MjllixzobHAV3Nth51Wr",
                                "TVA9RuHRUvcGXteJcBHv",
                                "fTPZtAObAols1lEMuvse",
                                "L4vX7v7jBCOfJznZRiTh",
                                "lw6Ipz4OXADzZDLf4GzL",
                                "5X4QQndDLzDs02bYOhWp",
                                "fKwKc5NHmDRZbalTqqgT",
                            ]
                        },
                        'wages': {  # معوقات مزدی / مطالبات مزدی / مشکلات بیمه
                            'keywords': ['معوقات', 'مزدی', 'دستمزد', 'حقوق', 'بیمه', 'معیشت', 'مطالبات', 'حق‌بیمه'],
                            'images': [
                                "rnZiSzeEEjpFAtw5Ozvw",
                                "Fyv9ksReWCkwEan3OozA",
                                "xvVwjvWLG5ADOxW4EIgY",
                                "1f0FOBPjZ2bBjqiprIkp",
                                "HHk1ato9bgvQfZFgfsFF",
                                "5jbEVltP8kfK9yrSj9NP",
                                "GQY4znGiq9XsHgqIL0Jv",
                                "aCSKcmmHHvwJNibT0POX",
                                "RbTWgy4tmbXxofhEYD3j",
                                "3XhhBrieVpJFtVtLookz",
                                "K6pWnYcCIIlNtoh4cDKF",
                                "h0D5PmQziVoH8bwSfVJn",
                                "bwStazSQyv0rHfPwsKqS",
                                "4LsX7qJLZi06uBnW8ONx",
                                "43j4MvIyLLHNRaUR4xyK",
                                "7oesnmsu0RfrE2W7Lk0C",
                            ]
                        },
                        'unemployment': {  # بیکاری و تعدیل
                            'keywords': ['بیکاری', 'تعدیل', 'اخراج', 'بازنشسته', 'بازنشستگان', 'تعطیل'],
                            'images': [
                                "Fyv9ksReWCkwEan3OozA",
                                "1f0FOBPjZ2bBjqiprIkp",
                                "gom8LzRHEvtsHkKDgoAh",
                                "LCNF3R3yiHWI23eZ2pRX",
                                "LOeqev3kgW0RAOCaII2l",
                                "aCSKcmmHHvwJNibT0POX",
                                "RbTWgy4tmbXxofhEYD3j",
                                "johotPThTTQum2OKM2Xr",
                                "4LsX7qJLZi06uBnW8ONx",
                                "43j4MvIyLLHNRaUR4xyK",
                            ]
                        },
                        'statistics': {  # آمار و گزارش
                            'keywords': ['آمار', 'گزارش', 'بررسی', 'وضعیت'],
                            'images': [
                                "HHk1ato9bgvQfZFgfsFF",
                                "7oesnmsu0RfrE2W7Lk0C",
                                "K6pWnYcCIIlNtoh4cDKF",
                            ]
                        },
                        'injury': {  # مصدومیت و مرگ کارگر
                            'keywords': ['مصدومیت', 'مرگ', 'جان باختن', 'فوت', 'کشته', 'مجروح', 'زخمی'],
                            'images': [
                                "FexfZ6Z9FojX7y6kMfRH",
                                "lbyYxUafXnxPCDT1DTul",
                                "opBNOv604Cccl4DLBh33",
                                "djBWFeRxBpG2ZR4NgCR1",
                                "z5zgF2E9yC3E3EHwViDu",
                                "P67wCQolqce71iGfEw0g",
                                "bMWHv8lA1GzcwnImumn7",
                                "p54CDjq7NrukeAnOYpIq",
                                "T4C2bHaksBsaY3DOLobO",
                                "gEuvCQ8HVFQPT74zJSaH",
                            ]
                        },
                        'construction': {  # ساختمانی و عمرانی (پیش‌فرض)
                            'keywords': [],
                            'images': [
                                "zwDqgNNNtfGzNZod4M2M",
                                "lbyYxUafXnxPCDT1DTul",
                                "fKwKc5NHmDRZbalTqqgT",
                                "gom8LzRHEvtsHkKDgoAh",
                                "dxiHs3AT6IjhOmWZTBaR",
                            ]
                        },
                    }
                    
                    # تشخیص هوشمند موضوع خبر
                    selected_category = 'construction'  # پیش‌فرض
                    for cat_name, cat_data in worker_image_categories.items():
                        if any(kw in search_text for kw in cat_data['keywords']):
                            selected_category = cat_name
                            break
                    
                    selected_id = random.choice(worker_image_categories[selected_category]['images'])
                    filename = self.resolved_images.get(selected_id, f"{selected_id}.png")
                    main_image = f"https://cdn.jsdelivr.net/gh/AmirCode97/blogger-news-bot@main/images/{filename}"
                    print(f"  [Image Override] Topic: {selected_category} → stock photo selected: {main_image}")

                # ==========================================
                # 2b. Category Fallbacks for other labels if no image is found
                # ==========================================
                if not main_image:
                    import random
                    print(f"  [Image Fallback] No image found. Selecting category-specific stock photo...")
                    
                    category_fallbacks = {
                        'وضعیت زندانیان': [
                            "FexfZ6Z9FojX7y6kMfRH", "lbyYxUafXnxPCDT1DTul", "opBNOv604Cccl4DLBh33",
                            "djBWFeRxBpG2ZR4NgCR1", "z5zgF2E9yC3E3EHwViDu", "P67wCQolqce71iGfEw0g",
                            "bMWHv8lA1GzcwnImumn7", "p54CDjq7NrukeAnOYpIq", "T4C2bHaksBsaY3DOLobO",
                            "gEuvCQ8HVFQPT74zJSaH"
                        ],
                        'حقوق بشر': [
                            "xvVwjvWLG5ADOxW4EIgY", "7kyrBNbl4c2KS8vircgB", "3XhhBrieVpJFtVtLookz",
                            "HHk1ato9bgvQfZFgfsFF", "7oesnmsu0RfrE2W7Lk0C", "K6pWnYcCIIlNtoh4cDKF"
                        ],
                        'بین‌الملل': [
                            "HHk1ato9bgvQfZFgfsFF", "7oesnmsu0RfrE2W7Lk0C", "K6pWnYcCIIlNtoh4cDKF"
                        ]
                    }
                    
                    fallback_id = None
                    for label in post_labels:
                        if label in category_fallbacks:
                            fallback_id = random.choice(category_fallbacks[label])
                            print(f"  [Image Fallback] Category '{label}' -> Selected ID: {fallback_id}")
                            break
                            
                    if not fallback_id and self.resolved_images:
                        fallback_id = random.choice(list(self.resolved_images.keys()))
                        print(f"  [Image Fallback] Generic fallback -> Selected ID: {fallback_id}")
                        
                    if fallback_id:
                        filename = self.resolved_images.get(fallback_id, f"{fallback_id}.png")
                        if filename.endswith(".jpg") or filename.endswith(".png"):
                            pass
                        else:
                            filename = f"{filename}.png"
                        main_image = f"https://cdn.jsdelivr.net/gh/AmirCode97/blogger-news-bot@main/images/{filename}"

                # ==========================================
                # 3. Build HTML (with unblocked image proxy & deep SEO)
                # ==========================================
                image_html = ""
                if main_image:
                    proxied_image = download_and_optimize_image(main_image)
                    print(f"  [Image] {proxied_image[:60]}...")
                    # Image SEO: Alt tags, title tags, loading="lazy", decoding="async", and semantic figure markup
                    image_html = f'''<figure style="margin:0 0 25px 0;text-align:center;">
    <img src="{proxied_image}" alt="{article_title}" title="{article_title}" loading="lazy" decoding="async" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);" />
    <figcaption style="display:none;">{article_title}</figcaption>
</figure>'''
                else:
                    print(f"  [Warning] No image found for this article")
                
                # Convert text paragraphs into semantic <p> tags for better SEO crawling
                formatted_paragraphs = []
                for p in description.split("\n"):
                    clean_p = p.strip()
                    if clean_p:
                        formatted_paragraphs.append(f'<p style="margin-bottom:18px;">{clean_p}</p>')
                description_html = "\n".join(formatted_paragraphs)

                # Generate Google Rich Snippet (Schema.org JSON-LD Structured Data)
                import json
                from urllib.parse import quote
                
                # Dynamic JSON-LD preparation
                schema_data = {
                    "@context": "https://schema.org",
                    "@type": "NewsArticle",
                    "headline": article_title,
                    "image": [main_image] if main_image else [],
                    "datePublished": datetime.utcnow().isoformat() + "Z",
                    "dateModified": datetime.utcnow().isoformat() + "Z",
                    "author": {
                        "@type": "Organization",
                        "name": "iranpolnews",
                        "url": "https://iranpolnews.blogspot.com"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "iranpolnews",
                        "logo": {
                            "@type": "ImageObject",
                            "url": "https://cdn.jsdelivr.net/gh/AmirCode97/blogger-news-bot@main/images/HHk1ato9bgvQfZFgfsFF.png"
                        }
                    },
                    "description": meta_description
                }
                
                schema_json = json.dumps(schema_data, ensure_ascii=False)
                schema_script = f'<script type="application/ld+json">{schema_json}</script>'

                # Generate internal category SEO links
                labels_to_use = post_labels if post_labels else ["حقوق بشر"]
                tag_links = []
                for label in labels_to_use:
                    tag_links.append(f'<a href="/search/label/{quote(label)}" style="color:#c0392b;text-decoration:none;margin-left:12px;font-weight:bold;transition:color 0.2s;" onmouseover="this.style.color=\'#e74c3c\'" onmouseout="this.style.color=\'#c0392b\'">#{label}</a>')
                tags_html = " ".join(tag_links)

                # Generate "مطالب مرتبط" (Related Posts) widget dynamically for new post
                related_widget_html = ""
                try:
                    from update_all_posts import extract_first_image, get_persian_date, build_related_posts_widget
                    
                    # Fetch recent posts to find matches
                    response = self.blogger.service.posts().list(
                        blogId=self.blogger.blog_id,
                        maxResults=50
                    ).execute()
                    items = response.get('items', [])
                    
                    candidates = []
                    for it in items:
                        lbls = it.get('labels', [])
                        overlap = len(set(post_labels).intersection(set(lbls)))
                        candidates.append((overlap, it))
                        
                    # Sort by overlap, then publish date
                    candidates.sort(key=lambda x: (x[0], x[1].get('published', '')), reverse=True)
                    
                    selected_posts = []
                    for score, it in candidates:
                        it_lbls = it.get('labels', [])
                        it_lbl = it_lbls[0] if it_lbls else "حقوق بشر"
                        
                        it_img = extract_first_image(it.get('content', ''), it_lbl, self.resolved_images)
                        it_date = get_persian_date(it.get('published', ''))
                        
                        selected_posts.append({
                            'title': it['title'],
                            'url': it.get('url', ''),
                            'label': it_lbl,
                            'image': it_img,
                            'date': it_date
                        })
                        if len(selected_posts) == 3:
                            break
                            
                    # Fill up to 3 if needed
                    while len(selected_posts) < 3 and items:
                        for it in items:
                            if it.get('url') in [p['url'] for p in selected_posts]:
                                continue
                            it_lbls = it.get('labels', [])
                            it_lbl = it_lbls[0] if it_lbls else "حقوق بشر"
                            it_img = extract_first_image(it.get('content', ''), it_lbl, self.resolved_images)
                            it_date = get_persian_date(it.get('published', ''))
                            selected_posts.append({
                                'title': it['title'],
                                'url': it.get('url', ''),
                                'label': it_lbl,
                                'image': it_img,
                                'date': it_date
                            })
                            if len(selected_posts) == 3:
                                break
                        break
                        
                    if len(selected_posts) >= 3:
                        current_post_label = post_labels[0] if post_labels else "حقوق بشر"
                        related_widget_html = build_related_posts_widget(selected_posts, current_post_label)
                except Exception as e:
                    print(f"  [ERROR] Building related posts widget: {e}")

                html_content = f"""
                <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
                {schema_script}
                {image_html}
                
                <!-- Semantic Article Body -->
                <article style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
                    <!-- SEO Meta Lead Paragraph -->
                    <p style="font-weight:bold;font-size:18px;color:#eee;border-bottom:1px solid #333;padding-bottom:15px;margin-bottom:20px;">
                        {meta_description}
                    </p>
                    
                    <!-- Article Content -->
                    <div>
                        {description_html}
                    </div>
                </article>
                
                <!-- NOTE: Related posts are handled by the Blogger template's built-in rp-section widget -->
                
                <!-- SEO Internal Link Tag Cloud & Source Box -->
                <footer style="margin-top:35px;border-top:1px solid #222;padding-top:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;direction:rtl;text-align:right;">
                    <div style="font-size:14px;color:#888;margin-bottom:10px;">
                        <span style="color:#aaa;margin-left:8px;font-weight:bold;">برچسب‌های مرتبط:</span>
                        {tags_html}
                    </div>
                    <div style="background:#161616;padding:10px 20px;border-radius:8px;border-right:3px solid #c0392b;font-weight:bold;color:#ddd;font-size:13px;box-shadow:0 4px 10px rgba(0,0,0,0.4);margin-bottom:10px;">
                        <span style="color:#c0392b;margin-left:8px;">منبع خبر:</span> iranpolnews
                    </div>
                </footer>
                """

                # 4. PUBLISH
                if self.blogger:
                    post_result = self.blogger.create_post(
                        title=article_title,
                        content=html_content,
                        labels=post_labels,
                        is_draft=False
                    )
                    if post_result:
                        print(f"[OK] Published: {post_result.get('url')}")
                        published_count += 1
                        
                        # Mark as published in BOTH systems
                        self.fetcher.mark_as_seen(article_title, item['id'])
                        self.duplicate_detector.mark_as_published(
                            title=article_title,
                            url=article_link,
                            content=description,
                            post_id=post_result.get('id', '')
                        )
                        
                        # 4. ANTI-429 DELAY
                        print("  [Wait] 20s delay to avoid Blogger rate limits...")
                        time.sleep(20)
                    else:
                        print(f"[FAILED] Could not post to Blogger")
                
            except Exception as e:
                print(f"[ERROR] Processing item: {e}")

        print(f"\nFinished. Published {published_count} items.")
        
        # Finally, update the live statistics
        try:
            from stats_updater import fetch_and_calculate_stats, update_stats_post
            print("\n[INFO] Running Live Stats Engine...")
            stats_data = fetch_and_calculate_stats()
            if stats_data and self.blogger:
                update_stats_post(self.blogger, stats_data)
        except Exception as e:
            print(f"[Error] Failed to update stats: {e}")

    def run_once(self):
        self.fetch_and_process_news()

    def run_scheduler(self):
        print(f"[SCHEDULER] Bot started. Checking news every {CHECK_INTERVAL_HOURS} hours.")
        
        # Run immediately on start
        self.fetch_and_process_news()
        
        # Schedule next runs
        schedule.every(CHECK_INTERVAL_HOURS).hours.do(self.fetch_and_process_news)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    bot = BloggerNewsBot()
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        bot.run_once()
    else:
        # Default mode: Continuous Loop
        bot.run_scheduler()

if __name__ == "__main__":
    import sys
    main()
