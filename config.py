"""
Configuration for Blogger News Bot
تنظیمات ربات خبری بلاگر
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== Blogger API ====================
BLOG_ID = os.getenv("BLOG_ID")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# ==================== Gemini AI ====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ==================== News Settings ====================
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", "6"))
MAX_NEWS_PER_CHECK = int(os.getenv("MAX_NEWS_PER_CHECK", "30"))

# ==================== Proxy Settings ====================
# برای دور زدن محدودیت‌های Cloudflare
USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL", "")  # Example: http://user:pass@proxy:port

# لیست پروکسی‌های Residential (فرمت: http://user:pass@ip:port)
# برای امنیت بیشتر، این لیست از فایل محلی proxies.json یا متغیر محیطی بارگذاری می‌شود تا روی گیت‌هاب عمومی قرار نگیرد.
import json
FREE_PROXIES = []

# ۱. تلاش برای بارگذاری از متغیر محیطی
residential_env = os.getenv("RESIDENTIAL_PROXIES", "")
if residential_env:
    try:
        if residential_env.startswith("["):
            FREE_PROXIES = json.loads(residential_env)
        else:
            FREE_PROXIES = [p.strip() for p in residential_env.split(",") if p.strip()]
    except Exception as e:
        print(f"[WARNING] Loading proxies from env failed: {e}")

# ۲. تلاش برای بارگذاری از فایل محلی proxies.json (در صورتی که وجود داشته باشد)
proxies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxies.json")
if os.path.exists(proxies_file):
    try:
        with open(proxies_file, "r", encoding="utf-8") as f:
            local_proxies = json.load(f)
            if isinstance(local_proxies, list) and local_proxies:
                FREE_PROXIES = local_proxies
    except Exception as e:
        print(f"[WARNING] Loading proxies from proxies.json failed: {e}")

# ==================== News Sources ====================
# منابع خبری - شامل ایران اینترنشنال و سایت‌های حقوق بشری
NEWS_SOURCES = [
    # ==================== ایران اینترنشنال (بین‌الملل) - 5 خبر ====================
    {
        "name": "ایران اینترنشنال",
        "url": "https://www.iranintl.com/",
        "rss_url": "https://www.iranintl.com/feed",
        "type": "rss",
        "language": "fa",
        "enabled": True,
        "category": "بین‌الملل",
        "priority": 1,
        "max_items": 5,
    },
    # ==================== کانون حقوق بشر ایران (بخش حقوق بشر در ایران) ====================
    {
        "name": "کانون حقوق بشر ایران",
        "url": "https://iranhrs.org/category/%d8%ad%d9%82%d9%88%d9%82-%d8%a8%d8%b4%d8%b1-%d8%af%d8%b1-%d8%a7%db%8c%d8%b1%d8%a7%d9%86/",
        "type": "scrape",
        "language": "fa",
        "enabled": True,
        "category": "حقوق بشر",
        "max_items": 7,
        "use_proxy": True,
        "selectors": {
            "articles": "article",
            "title": "h2 a, h3 a",
            "link": "h2 a, h3 a",
            "description": "p",
            "image": "img"
        }
    },
    # ==================== خبرگزاری هرانا (بخش کارگران) - بدون محدودیت ====================
    {
        "name": "هرانا - کارگران",
        "url": "https://www.hra-news.org/category/labor/",
        "enabled": True,
        "type": "scrape",
        "language": "fa",
        "category": "کارگران",
        "priority": 1,
        "selectors": {
            "articles": "div.post-item",
            "title": "h2 a, h3 a, .entry-title a",
            "description": ".entry-summary, .excerpt",
            "image": "img.wp-post-image"
        }
    },
    # ==================== حقوق بشر در ایران - بازداشت/بلاتکلیفی ====================
    {
        "name": "حقوق بشر در ایران - بازداشت",
        "url": "https://humanrightsinir.org/category/%d8%a8%d8%a7%d8%b2%d8%af%d8%a7%d8%b4%d8%aa-%d8%a8%d9%84%d8%a7%d8%aa%da%a9%d9%84%db%8c%d9%81%db%8c/",
        "rss_url": "https://humanrightsinir.org/category/%d8%a8%d8%a7%d8%b2%d8%af%d8%a7%d8%b4%d8%aa-%d8%a8%d9%84%d8%a7%d8%aa%da%a9%d9%84%db%8c%d9%81%db%8c/feed/",
        "type": "rss",
        "language": "fa",
        "enabled": True,
        "category": "وضعیت زندانیان",
        "priority": 1,
        "max_items": 5,
    },
    # ==================== حقوق بشر در ایران - محاکمه / صدور حکم ====================
    {
        "name": "حقوق بشر در ایران - محاکمه",
        "url": "https://humanrightsinir.org/category/%d9%85%d8%ad%d8%a7%da%a9%d9%85%d9%87-%d8%b5%d8%af%d9%88%d8%b1-%d8%ad%da%a9%d9%85/",
        "rss_url": "https://humanrightsinir.org/category/%d9%85%d8%ad%d8%a7%da%a9%d9%85%d9%87-%d8%b5%d8%af%d9%88%d8%b1-%d8%ad%da%a9%d9%85/feed/",
        "type": "rss",
        "language": "fa",
        "enabled": True,
        "category": "حقوق بشر",
        "priority": 2,
        "max_items": 5,
    },
]


# ==================== Content Filter Keywords ====================
# کلمات کلیدی برای فیلتر اخبار مرتبط
FILTER_KEYWORDS = [
    # فارسی
    "ایران", "تهران", "حقوق بشر", "اعتراض", "زندانی سیاسی",
    "جمهوری اسلامی", "رژیم", "سپاه", "خامنه‌ای", "رئیسی",
    "تحریم", "هسته‌ای", "اتمی", "برجام", "آزادی بیان",
    "زن زندگی آزادی", "مهسا امینی", "اعدام", "بازداشت",
    # انگلیسی
    "iran", "iranian", "tehran", "human rights", "protest",
    "political prisoner", "islamic republic", "regime", "irgc",
    "khamenei", "sanctions", "nuclear", "jcpoa", "freedom",
    "mahsa amini", "execution", "arrest"
]

# ==================== Gemini AI ====================
APP_EXTRA_CONFIG = os.getenv("APP_EXTRA_CONFIG", "")

if not APP_EXTRA_CONFIG:
    APP_EXTRA_CONFIG = "You are a helpful news assistant. Summarize and rewrite the input news in Persian."

AI_TRANSLATE_PROMPT = """
این خبر انگلیسی را به فارسی ترجمه کن:
- ترجمه روان و طبیعی
- حفظ معنا و دقت
- مناسب برای مخاطب فارسی‌زبان
"""
