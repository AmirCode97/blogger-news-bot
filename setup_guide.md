# 🚀 راهنمای راه‌اندازی ربات خبری Blogger

## 📋 پیش‌نیازها

- Python 3.10+
- حساب Google با دسترسی به Blogger

---

## 📁 ساختار پروژه

```
blogger-news-bot/
├── main.py              # اسکریپت اصلی اجرای ربات
├── config.py            # تنظیمات و منابع خبری
├── news_fetcher.py      # دریافت اخبار از RSS و وب‌سایت‌ها
├── ai_processor.py      # پردازش و بازنویسی خبرها با هوش مصنوعی (Gemini)
├── blogger_poster.py    # ارسال به Blogger
├── requirements.txt     # وابستگی‌ها و پیش‌نیازهای پایتون
├── .env                 # متغیرهای محیطی و سکرت‌ها
└── credentials.json     # اعتبارنامه Google API
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

### مرحله ۴: ایجاد فایل .env

```bash
cp .env.example .env
```

سپس فایل را ویرایش کنید:

```env
BLOG_ID= ..........
GOOGLE_CREDENTIALS_FILE=credentials.json
GEMINI_API_KEY=your_key_here
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
- فایل `token.pickle` یا `token_auth_fixed.pickle` را حذف و دوباره اجرا کنید

### خطای Gemini API

- کلید API را بررسی کنید
- محدودیت‌های رایگان API را چک کنید

### عدم دریافت اخبار

- RSS feed ها را با مرورگر تست کنید
- کلمات کلیدی فیلتر را بررسی کنید

---

## 📞 پشتیبانی

در صورت بروز مشکل، لاگ‌های ترمینال را بررسی کنید.
