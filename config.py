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

هدف اصلی: خبر ارائه شده را طوری بازنویسی کن که هیچ موتور جستجویی (مخصوصاً گوگل) آن را به عنوان محتوای تکراری (Duplicate Content) تشخیص ندهد. محتوای خروجی باید ۱۰۰٪ یونیک و اصیل به نظر برسد.

تکنیک‌های بازنویسی پیشرفته (حتماً رعایت کن):
1. عنوان: یک عنوان کاملاً جدید، خلاقانه و جذاب بنویس که هیچ شباهتی به عنوان اصلی نداشته باشد. از زاویه دید متفاوت بنویس.
2. ساختار جملات را کاملاً تغییر بده: جملات مجهول را معلوم کن و بالعکس. ترتیب فاعل و مفعول را عوض کن.
3. از مترادف‌ها و کلمات جایگزین استفاده کن: هر کلمه کلیدی را با مترادف آن جایگزین کن.
4. ترتیب پاراگراف‌ها را تغییر بده: اگر خبر اصلی از بالا به پایین رفته، تو از مهم‌ترین نکته شروع کن یا از زاویه تحلیلی وارد شو.
5. تحلیل و نظر تحریریه اضافه کن: یک پاراگراف تحلیلی از دیدگاه خبرنگار اضافه کن که در منبع اصلی وجود ندارد.
6. مقدمه و نتیجه‌گیری اختصاصی بنویس: پاراگراف اول و آخر باید کاملاً از صفر نوشته شوند.
7. از اعداد و آمار به شیوه متفاوت استفاده کن: مثلاً «بیش از هزار نفر» به جای «۱۰۰۰ نفر».
8. لحن مطبوعاتی حرفه‌ای: مثل خبرگزاری‌های معتبر بنویس.

قوانین طول متن (بسیار مهم):
- اگر خبر کوتاه یا خلاصه است (مثل اخبار ایران اینترنشنال): متن بازنویسی شده دقیقاً بین ۵ تا ۷ خط باشد. مختصر و مفید.
- اگر خبر بلند و مفصل است (مثل گزارش‌های حقوق بشری): متن بازنویسی شده دقیقاً بین ۱۳ تا ۱۵ خط باشد. کامل و تحلیلی.
- برای تشخیص: اگر متن اصلی کمتر از ۵۰۰ کاراکتر است، کوتاه بنویس (۵-۷ خط). اگر بیشتر از ۵۰۰ کاراکتر است، بلند بنویس (۱۳-۱۵ خط).

قوانین مهم:
- هیچ جمله‌ای را عیناً از متن اصلی کپی نکن
- فکت‌ها و اطلاعات واقعی را حفظ کن اما با کلمات متفاوت بیان کن
- از واژه‌های سئو-محور و کلمات کلیدی مرتبط استفاده کن
- فقط فارسی بنویس، هیچ ترجمه انگلیسی یا آلمانی ننویس

فرمت خروجی (دقیقاً رعایت کن، هیچ متن اضافه‌ای ننویس):

===TITLE===
[عنوان کاملاً جدید و یونیک به فارسی]

===PERSIAN===
[متن بازنویسی شده کامل به فارسی - طبق قوانین طول متن بالا]

===TAGS===
[تگ‌های مرتبط با کاما]
"""

AI_TRANSLATE_PROMPT = """
این خبر انگلیسی را به فارسی ترجمه کن:
- ترجمه روان و طبیعی
- حفظ معنا و دقت
- مناسب برای مخاطب فارسی‌زبان
"""
