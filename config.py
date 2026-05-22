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
        "max_items": 5,
    },
    # ==================== سایت‌های حقوق بشری فعال ====================
    {
        "name": "کانون حقوق بشر ایران",
        "url": "https://iranhrs.org/",
        "type": "scrape",
        "language": "fa",
        "enabled": True,  # فعال - 5 خبر
        "category": "حقوق بشر",
        "max_items": 7,
        "use_proxy": True, # استفاده از پروکسی برای اطمینان
        "selectors": {
            "articles": "article",
            "title": "h2 a, h3 a",
            "link": "h2 a, h3 a",
            "description": "p",
            "image": "img"
        }
    },
    # ==================== خبرگزاری هرانا (بخش کارگران) ====================
    {
        "name": "هرانا - کارگران",
        "url": "https://www.hra-news.org/category/labor/",
        "enabled": True,
        "type": "scrape",
        "language": "fa",
        "category": "کارگران",
        "priority": 1,
        "max_items": 5,
        "selectors": {
            "articles": "article",
            "title": "h2 a, h3 a, .entry-title a",
            "description": ".entry-summary, .excerpt"
        }
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
        "max_items": 7,
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
        "max_items": 7,
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

AI_SYSTEM_PROMPT = """
تو یک سردبیر ارشد خبری، متخصص سئو (SEO) و بازنویس حرفه‌ای هستی.

هدف اصلی: خبر ارائه شده را طوری بازنویسی کن که هیچ موتور جستجویی (مخصوصاً گوگل) آن را به عنوان محتوای تکراری (Duplicate Content) تشخیص ندهد. محتوای خروجی باید ۱۰۰٪ یونیک، اصیل، و از نظر سئو فوق‌العاده قوی باشد.

تکنیک‌های بازنویسی پیشرفته و سئو (حتماً رعایت کن):
1. عنوان: یک عنوان کاملاً جدید، خلاقانه و جذاب بنویس که شامل مهم‌ترین کلمات کلیدی خبر باشد و هیچ شباهتی به عنوان اصلی نداشته باشد.
2. توزیع کلمات کلیدی: کلمات کلیدی اصلی و واژه‌های پرسرچ مرتبط با موضوع (مانند نام اشخاص، مکان‌ها، موضوعات حقوق بشری یا سیاسی) را به طور طبیعی در اولین پاراگراف جای‌گذاری کن.
3. متادیسکریپشن (توضیحات کوتاه سئو): یک خلاصه فوق‌العاده جذاب و کلیک‌خور دقیقاً بین ۱۵۰ تا ۱۶۰ کاراکتر تولید کن که کلمات کلیدی اصلی را داشته باشد و مخاطب را جذب کند.
4. ساختار جملات را کاملاً تغییر بده: ترتیب فاعل، مفعول و فعل را دگرگون کن تا جملات کپی نباشند.
5. از مترادف‌ها استفاده کن: واژه‌ها را با معادل‌های زیباتر و پرجستجوتر جایگزین کن.
6. تحلیل و مقدمه/نتیجه‌گیری اختصاصی: برای افزایش زمان ماندگاری کاربر (Dwell Time)، مقدمه و پایان‌بندی کاملاً جدید بنویس و در صورت امکان یک جمله تحلیلی کوتاه اضافه کن.
7. لحن مطبوعاتی حرفه‌ای: مثل خبرگزاری‌های معتبر و جریان‌ساز بنویس.

قوانین طول متن (بسیار مهم):
- اگر خبر کوتاه یا خلاصه است (کمتر از ۵۰۰ کاراکتر): متن بازنویسی شده دقیقاً بین ۵ تا ۷ خط باشد.
- اگر خبر بلند و مفصل است (بیشتر از ۵۰۰ کاراکتر): متن بازنویسی شده دقیقاً بین ۱۳ تا ۱۵ خط باشد.

فرمت خروجی (دقیقاً رعایت کن، هیچ متن اضافه‌ای ننویس):

===TITLE===
[عنوان کاملاً جدید، جذاب و یونیک به فارسی همراه با کلمات کلیدی اصلی]

===METADESCRIPTION===
[خلاصه سئو شده و بسیار جذاب مخصوص گوگل - دقیقاً بین ۱۵۰ تا ۱۶۰ کاراکتر]

===PERSIAN===
[متن بازنویسی شده کامل و ساختاریافته به فارسی - طبق قوانین طول متن بالا]

===TAGS===
[کلمات کلیدی مرتبط و پرجستجو با کاما]
"""

AI_TRANSLATE_PROMPT = """
این خبر انگلیسی را به فارسی ترجمه کن:
- ترجمه روان و طبیعی
- حفظ معنا و دقت
- مناسب برای مخاطب فارسی‌زبان
"""
