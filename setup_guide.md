# 🚀 راهنمای راه‌اندازی ربات خبری Blogger

## 📋 پیش‌نیازها

- Python 3.10+
- حساب Google با دسترسی به Blogger
- (اختیاری) ربات تلگرام برای بررسی اخبار

---

## 📁 ساختار پروژه

```
blogger-news-bot/
├── main.py              # اسکریپت اصلی
├── config.py            # تنظیمات
├── news_fetcher.py      # دریافت اخبار
├── ai_processor.py      # پردازش با AI
├── blogger_poster.py    # ارسال به Blogger
├── telegram_reviewer.py # بررسی با تلگرام
├── requirements.txt     # وابستگی‌ها
├── .env                 # متغیرهای محیطی
└── credentials.json     # اعتبارنامه Google
```

---

## 🔧 مراحل راه‌اندازی

### مرحله ۱: نصب وابستگی‌ها

```bash
cd blogger-news-bot
pip install -r requirements.txt
```

### مرحله ۲: تنظیم Google Cloud Console

1. به [Google Cloud Console](https://console.cloud.google.com/) بروید
2. یک پروژه جدید بسازید
3. **Blogger API** را فعال کنید:
   - به APIs & Services > Library بروید
   - "Blogger API v3" را جستجو و فعال کنید
4. **OAuth 2.0 Credentials** بسازید:
   - به APIs & Services > Credentials بروید
   - روی "Create Credentials" > "OAuth client ID" کلیک کنید
   - نوع را "Desktop app" انتخاب کنید
   - دانلود کنید و به نام `credentials.json` در پوشه پروژه ذخیره کنید

### مرحله ۳: تنظیم Gemini API

1. به [Google AI Studio](https://aistudio.google.com/) بروید
2. API Key بسازید
3. کلید را در فایل `.env` قرار دهید

### مرحله ۴: تنظیم تلگرام (اختیاری)

1. در تلگرام به [@BotFather](https://t.me/BotFather) پیام دهید
2. با دستور `/newbot` یک ربات بسازید
3. توکن ربات را کپی کنید
4. Chat ID خود را از [@userinfobot](https://t.me/userinfobot) بگیرید
5. هر دو را در `.env` قرار دهید

### مرحله ۵: ایجاد فایل .env

```bash
cp .env.example .env
```

سپس فایل را ویرایش کنید:

```env
BLOG_ID= ..........
GOOGLE_CREDENTIALS_FILE=credentials.json
GEMINI_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_CHAT_ID=your_chat_id
CHECK_INTERVAL_HOURS=5
MAX_NEWS_PER_CHECK=10
```

---

## ▶️ اجرای ربات

### اجرای یکباره (تست)

```bash
python main.py --once
```

### اجرای زمان‌بندی شده

```bash
python main.py
```

---

## 📱 نحوه بررسی اخبار

اگر تلگرام تنظیم شده باشد:

1. ربات اخبار جدید را به شما در تلگرام ارسال می‌کند
2. هر خبر با دو دکمه می‌آید:
   - **✅ تأیید و انتشار**: خبر در وبلاگ منتشر می‌شود
   - **❌ رد کردن**: خبر حذف می‌شود
3. همچنین لینک ویرایش در Blogger موجود است

---

## ➕ اضافه کردن منابع خبری

فایل `config.py` را ویرایش کنید و به لیست `NEWS_SOURCES` اضافه کنید:

```python
{
    "name": "نام منبع",
    "url": "https://example.com/rss",
    "language": "fa",  # یا "en"
    "enabled": True,
    "filter_keywords": ["کلمه۱", "کلمه۲"]  # اختیاری
}
```

---

## 🔍 فیلتر کردن اخبار

کلمات کلیدی را در `FILTER_KEYWORDS` در فایل `config.py` ویرایش کنید.
فقط اخباری که شامل این کلمات باشند دریافت می‌شوند.

---

## ❓ رفع مشکلات

### خطای اعتبارنامه Google

- مطمئن شوید `credentials.json` در پوشه پروژه است
- فایل `token.pickle` را حذف و دوباره اجرا کنید

### خطای Gemini API

- کلید API را بررسی کنید
- محدودیت‌های رایگان API را چک کنید

### عدم دریافت اخبار

- RSS feed ها را با مرورگر تست کنید
- کلمات کلیدی فیلتر را بررسی کنید

---

## 📞 پشتیبانی

در صورت بروز مشکل، لاگ‌های ترمینال را بررسی کنید.
