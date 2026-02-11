"""
Configuration for Blogger News Bot
تنظیمات ربات خبری بلاگر
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== Blogger API ====================
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# ==================== Gemini AI ====================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ==================== Telegram (for review) ====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

# ==================== News Settings ====================
CHECK_INTERVAL_HOURS = int(os.getenv("CHECK_INTERVAL_HOURS", "5"))
MAX_NEWS_PER_CHECK = int(os.getenv("MAX_NEWS_PER_CHECK", "30"))  # Total: 10+5+5+5+5=30

# ==================== Proxy Settings ====================
# برای دور زدن محدودیت‌های Cloudflare
USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"
PROXY_URL = os.getenv("PROXY_URL", "")  # Example: http://user:pass@proxy:port

# لیست پروکسی‌های Residential (فرمت: http://user:pass@ip:port)
FREE_PROXIES = [
    "http://xvgyvcip:icfmhmtsfla6@142.111.48.253:7030",
    "http://xvgyvcip:icfmhmtsfla6@23.95.150.145:6114",
    "http://xvgyvcip:icfmhmtsfla6@198.23.239.134:6540",
    "http://xvgyvcip:icfmhmtsfla6@107.172.163.27:6543",
    "http://xvgyvcip:icfmhmtsfla6@198.105.121.200:6462",
    "http://xvgyvcip:icfmhmtsfla6@64.137.96.74:6641",
    "http://xvgyvcip:icfmhmtsfla6@84.247.60.125:6095",
    "http://xvgyvcip:icfmhmtsfla6@216.10.27.159:6837",
    "http://xvgyvcip:icfmhmtsfla6@23.26.71.145:5628",
    "http://xvgyvcip:icfmhmtsfla6@23.27.208.120:5830",
]

# ==================== News Sources ====================
# منابع خبری - شامل ایران اینترنشنال و سایت‌های حقوق بشری
NEWS_SOURCES = [
    # ==================== ایران اینترنشنال (بین‌الملل) - 10 خبر ====================
    {
        "name": "ایران اینترنشنال",
        "url": "https://www.iranintl.com/",
        "rss_url": "https://www.iranintl.com/feed",
        "type": "rss",
        "language": "fa",
        "enabled": True,
        "category": "بین‌الملل",
        "priority": 1,
        "max_items": 10,
    },
    # ==================== ایران اینترنشنال - گزارش ویژه (تحلیلی) ====================
    # غیرفعال - خبرها از RSS فید اصلی می‌آیند
    {
        "name": "ایران اینترنشنال - گزارش ویژه",
        "url": "https://www.iranintl.com/special-report",
        "type": "scrape",
        "language": "fa",
        "enabled": False,  # غیرفعال - RSS فید اصلی تمامی اخبار را شامل می‌شود
        "category": "گزارش ویژه",
        "priority": 1,
        "max_items": 3,
        "selectors": {}
    },
    # ==================== رادیو فردا - غیرفعال ====================
    {
        "name": "رادیو فردا",
        "url": "https://www.radiofarda.com/",
        "enabled": False,
        "type": "scrape",
        "language": "fa",
        "category": "حقوق بشر",
        "max_items": 5,
        "selectors": {}
    },
    # ==================== سایت‌های حقوق بشری (غیرفعال شده‌اند) ====================
    {
        "name": "کانون دفاع از حقوق بشر در ایران (بشریت)",
        "url": "https://bashariyat.org/",
        "enabled": False,  # غیرفعال طبق درخواست
        "type": "scrape",
        "max_items": 3,
    },
    {
        "name": "کانون حقوق بشر ایران",
        "url": "https://iranhrs.org/",
        "type": "scrape",
        "language": "fa",
        "enabled": True,  # فعال - 5 خبر
        "category": "حقوق بشر",
        "max_items": 5,
        "use_proxy": True, # استفاده از پروکسی برای اطمینان
        "selectors": {
            "articles": "article",
            "title": "h2 a, h3 a",
            "link": "h2 a, h3 a",
            "description": "p",
            "image": "img"
        }
    },
    {
        "name": "مجموعه فعالان حقوق بشر در ایران (HRA)",
        "url": "https://www.hra-iran.org/fa/",
        "enabled": False,  # غیرفعال طبق درخواست
        "type": "rss",
        "max_items": 4
    },
    # ==================== مرکز اسناد حقوق بشر ایران - غیرفعال ====================
    {
        "name": "مرکز اسناد حقوق بشر ایران",
        "url": "https://persian.iranhumanrights.org/",
        "enabled": False,  # غیرفعال طبق درخواست
        "type": "scrape",
        "max_items": 5,
    },
    # ==================== ناظران حقوق بشر ایران - 5 خبر ====================
    {
        "name": "ناظران حقوق بشر ایران",
        "url": "https://fa.iran-hrm.com/",
        "type": "scrape",
        "language": "fa",
        "enabled": True, # فعال
        "category": "حقوق بشر",
        "priority": 2,
        "max_items": 5,
        "selectors": {
            "articles": "article",
            "title": ".jeg_post_title a, h3.jeg_post_title a, h2 a, h3 a, h4 a",
            "link": ".jeg_post_title a, h3.jeg_post_title a, h2 a, h3 a, h4 a",
            "description": ".entry-content p, p",
            "image": "img"
        }
    },
    # ==================== سازمان حقوق بشر ایران (IranHR) - RSS Atom ====================
    {
        "name": "سازمان حقوق بشر ایران",
        "url": "https://iranhr.net/fa/rss/",
        "rss_url": "https://iranhr.net/fa/rss/",
        "type": "rss",
        "language": "fa",
        "enabled": True,
        "category": "حقوق بشر",
        "priority": 1,
        "max_items": 5,
    },
    # ==================== حقوق بشر در ایران (HumanRightsInIR) - WordPress RSS ====================
    {
        "name": "حقوق بشر در ایران",
        "url": "https://humanrightsinir.org/",
        "rss_url": "https://humanrightsinir.org/feed/",
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

# ==================== AI Prompt Templates ====================
AI_SYSTEM_PROMPT = """
تو یک خبرنگار حرفه‌ای هستی که اخبار ایران را پوشش می‌دهی.

وظایف تو:
1. اگر متن خبر ارائه شده، آن را به فارسی روان، انگلیسی و آلمانی خلاصه کن.
2. اگر فقط عنوان داده شده (یا متن بسیار کوتاه است)، بر اساس عنوان یک خبر کامل و حرفه‌ای بنویس.
3. محتوا باید دقیق، بی‌طرف و مناسب برای وبلاگ خبری باشد.
4. هر بخش باید حداقل ۲-۳ پاراگراف داشته باشد.

مهم: هر خبر باید محتوای منحصربه‌فرد داشته باشد. از تکرار محتوای مشابه برای اخبار مختلف خودداری کن.

فرمت خروجی باید دقیقاً به این شکل باشد:

===PERSIAN===
[متن کامل خبر به فارسی - حداقل ۳ پاراگراف با جزئیات]

===ENGLISH===
[Full news in English - minimum 2 detailed paragraphs]

===GERMAN===
[Ausführliche Nachrichten auf Deutsch - mindestens 2 Absätze]

===TAGS===
[تگ‌های مرتبط]
"""

AI_TRANSLATE_PROMPT = """
این خبر انگلیسی را به فارسی ترجمه کن:
- ترجمه روان و طبیعی
- حفظ معنا و دقت
- مناسب برای مخاطب فارسی‌زبان
"""
