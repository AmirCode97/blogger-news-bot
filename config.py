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
USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL", "")  # Example: http://user:pass@proxy:port

import json
FREE_PROXIES = []

# 1. Load from env var
residential_env = os.getenv("RESIDENTIAL_PROXIES", "")
if residential_env:
    try:
        if residential_env.startswith("["):
            FREE_PROXIES = json.loads(residential_env)
        else:
            FREE_PROXIES = [p.strip() for p in residential_env.split(",") if p.strip()]
    except Exception as e:
        print(f"[WARNING] Loading proxies from env failed: {e}")

# 2. Load from local proxies.json
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
    # ==================== کانون حقوق بشر ایران ====================
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
    # ==================== هرانا - کارگران ====================
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
    # ==================== حقوق بشر در ایران - بازداشت ====================
    {
        "name": "حقوق بشر در ایران - بازداشت",
        "url": "https://humanrightsinir.org/category/arrest-and-ignorance/",
        # RSS fallback: used automatically if scrape fails (e.g. IP block on GitHub Actions)
        "rss_fallback": "https://humanrightsinir.org/category/arrest-and-ignorance/feed/",
        "type": "scrape",
        "language": "fa",
        "enabled": True,
        "category": "وضعیت زندانیان",
        "priority": 1,
        "max_items": 5,
        "selectors": {
            "articles": "article, .post, .type-post",
            "title": "h2 a, h3 a, .entry-title a, a[rel='bookmark']",
            "link": "h2 a, h3 a, .entry-title a, a[rel='bookmark']",
            "description": "p, .entry-summary, .post-excerpt",
            "image": "img"
        }
    },
    # ==================== حقوق بشر در ایران - محاکمه ====================
    {
        "name": "حقوق بشر در ایران - محاکمه",
        "url": "https://humanrightsinir.org/category/%d9%85%d8%ad%d8%a7%da%a9%d9%85%d9%87-%d8%b5%d8%af%d9%88%d8%b1-%d8%ad%da%a9%d9%85/",
        # RSS fallback: used automatically if scrape fails (e.g. IP block on GitHub Actions)
        "rss_fallback": "https://humanrightsinir.org/category/%d9%85%d8%ad%d8%a7%da%a9%d9%85%d9%87-%d8%b5%d8%af%d9%88%d8%b1-%d8%ad%da%a9%d9%85/feed/",
        "type": "scrape",
        "language": "fa",
        "enabled": True,
        "category": "حقوق بشر",
        "priority": 2,
        "max_items": 5,
        "selectors": {
            "articles": "article, .post, .type-post",
            "title": "h2 a, h3 a, .entry-title a, a[rel='bookmark']",
            "link": "h2 a, h3 a, .entry-title a, a[rel='bookmark']",
            "description": "p, .entry-summary, .post-excerpt",
            "image": "img"
        }
    },
]


# ==================== Content Filter Keywords ====================
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
