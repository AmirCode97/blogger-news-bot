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
MAX_NEWS_PER_CHECK = int(os.getenv("MAX_NEWS_PER_CHECK", "10"))

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
# منابع خبری حقوق بشر - سایت‌های درخواستی کاربر
NEWS_SOURCES = [
    # ==================== سایت‌های حقوق بشری (Web Scraping) ====================
    {
        "name": "کانون دفاع از حقوق بشر در ایران (بشریت)",
        "url": "https://bashariyat.org/",
        "type": "scrape",  # نیاز به web scraping
        "language": "fa",
        "enabled": True,
        "selectors": {
            "articles": "article, .post, .entry",
            "title": "h2 a, .entry-title a",
            "link": "h2 a, .entry-title a",
            "description": ".entry-content, .post-content, p",
            "image": "img"
        }
    },
    {
        "name": "کانون حقوق بشر ایران",
        "url": "https://iranhrs.org/",
        "type": "scrape",
        "language": "fa",
        "enabled": False,  # غیرفعال - Cloudflare protection
        # این سایت نیاز به Playwright/Selenium دارد
        "selectors": {
            "articles": "article, .jeg_post, .post",
            "title": "h3 a, .jeg_post_title a",
            "link": "h3 a, .jeg_post_title a",
            "description": ".jeg_post_excerpt, .post-excerpt, p",
            "image": "img"
        }
    },
    {
        "name": "مجموعه فعالان حقوق بشر در ایران (HRA)",
        "url": "https://www.hra-iran.org/fa/",
        "rss_url": "https://www.hra-iran.org/fa/feed/",
        "type": "rss",
        "language": "fa",
        "enabled": True
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
تو یک دستیار خبری هستی که اخبار را برای یک وبلاگ فارسی پردازش می‌کنی.
وظایف تو:
1. خلاصه کردن خبر به فارسی روان
2. حفظ دقت و بی‌طرفی
3. اضافه کردن تحلیل کوتاه در صورت نیاز
4. فرمت مناسب برای وبلاگ

فرمت خروجی:
- عنوان جذاب
- خلاصه خبر (۲-۳ پاراگراف)
- تحلیل کوتاه (اختیاری)
- برچسب‌ها/تگ‌ها
"""

AI_TRANSLATE_PROMPT = """
این خبر انگلیسی را به فارسی ترجمه کن:
- ترجمه روان و طبیعی
- حفظ معنا و دقت
- مناسب برای مخاطب فارسی‌زبان
"""
