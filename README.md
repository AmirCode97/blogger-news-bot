# Blogger News AI Bot 🤖📰

*English version below / نسخه فارسی در ادامه*

---

## 🇬🇧 English Version

A smart and fully automated bot designed to fetch, process, rewrite, and publish Iranian human rights and political news on the Blogger platform.

### ✨ Introduction
This project is a comprehensive and intelligent bot that automatically aggregates news from reliable sources, processes them using artificial intelligence (Gemini AI), and publishes them on a Blogger blog with a premium dark-themed responsive layout. It also features an advanced **Live Statistics** engine that dynamically updates real-time human rights stats in Iran.

### 🚀 Key Features

* **Diverse News Aggregation & Smart Extraction:** Automatically fetches news from reputable sources including *Iran International, HRA News (HRANA), IranHRS (Human Rights in Iran), Iran-HRM (Iran Human Rights Monitor), IranHR (Iran Human Rights), and Human Rights in Iran (HumanRightsInIR)*, extracting full-text and high-quality images.
* **AI Processing & Rewriting (Gemini AI):** Rewrites news articles to be completely unique and highly SEO-optimized, avoiding duplicate content penalties on search engines.
* **Smart Labeling & Tagging:** Automatically scans keywords and assigns relevant categories/labels (e.g., *Prisoner Status, International Reactions, Special Report, etc.*).
* **Live Stats Engine:** Automatically parses news and reliable reference sources (like HRANA) to extract real-time human rights statistics and updates a dedicated statistics post on the blog.
* **Advanced Duplicate Detection:** A sophisticated system checking both headlines and article bodies to prevent publishing duplicate or highly similar news.
* **Custom Theme Integration:** Generates beautiful, responsive HTML blocks that blend perfectly with a dark-themed blog layout, including a stylized "News Source" badge.

### ⚙️ Installation & Requirements

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment variables:**
   Create a `.env` file in the root directory and configure the following variables:
   ```env
   BLOG_ID=your_blog_id
   GEMINI_API_KEY=your_api_key
   ```
   * **Important Note:** Place your Google Authentication file `credentials.json` (for Blogger API) in the root directory.

### ▶️ Usage

1. **Manual Run (One-time):**
   Checks for new articles and exits immediately:
   ```bash
   python main.py --once
   ```

2. **Continuous Loop (Background Service):**
   Runs continuously in the background, checking sources at a scheduled interval (default: every 5 hours):
   ```bash
   python main.py
   ```

3. **Fully Automated Deployment (GitHub Actions):**
   The bot is pre-configured to run automatically and completely free of charge on GitHub servers (configured in `news_bot.yml`). Simply set up the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions**):
   * `BLOG_ID`
   * `GEMINI_API_KEY`
   * `GOOGLE_CREDENTIALS_JSON` (the raw content of your authentication JSON file)
   * `GOOGLE_TOKEN_PICKLE` (the Base64-encoded string of your authentication token)

---

## 🇮🇷 نسخه فارسی (Persian Version)

ربات هوشمند و تمام‌خودکار برای دریافت، پردازش، بازنویسی و انتشار اخبار حقوق بشر و سیاسی ایران در پلتفرم بلاگر (Blogger).

### ✨ معرفی
این پروژه یک ربات جامع و هوشمند است که به صورت خودکار اخبار را از منابع معتبر دریافت می‌کند، با استفاده از هوش مصنوعی (Gemini AI) پردازش‌های تخصصی روی آن‌ها انجام داده و در وبلاگ با ظاهری بسیار زیبا و هماهنگ با قالب تیره (Dark Theme) منتشر می‌کند. همچنین این ربات دارای سیستم پیشرفته نمایش **آمار زنده** (Live Statistics) از وضعیت حقوق بشر در ایران است.

### 🚀 ویژگی‌های کلیدی

* **منابع خبری متنوع و استخراج هوشمند:** اخبار را از منابع معتبری نظیر *ایران اینترنشنال، هرانا (HRA News)، کانون حقوق بشر ایران (IranHRS)، ناظران حقوق بشر ایران (Iran-HRM)، سازمان حقوق بشر ایران (IranHR) و حقوق بشر در ایران (HumanRightsInIR)* دریافت کرده و متن کامل و تصاویر با کیفیت اصلی را استخراج می‌کند.
* **پردازش هوش مصنوعی (Gemini AI):** خبر ارائه شده را به گونه‌ای بازنویسی می‌کند که از نظر سئو کاملاً یونیک باشد و توسط گوگل به عنوان محتوای تکراری (Duplicate Content) شناسایی نشود.
* **برچسب‌گذاری هوشمند (Smart Labeling):** به طور خودکار با اسکن کلمات کلیدی، دسته بندی و لیبل‌های مناسب (نظیر *وضعیت زندانیان، واکنش‌های بین‌المللی، گزارش ویژه و...*) را به پست اختصاص می‌دهد.
* **موتور آمار زنده (Live Stats Engine):** بررسی اتوماتیک اخبار و منابع مرجع (مانند هرانا) برای استخراج آمار زنده و بروزرسانی لحظه‌ای یک پست اختصاصی در وبلاگ (بخش آمار زنده).
* **سیستم هوشمند ضد تکرار (Duplicate Detection):** مکانیزم پیشرفته و هوشمند برای بررسی متن کامل و تیترها جهت جلوگیری از انتشار اخبار تکراری و مشابه.
* **قالب اختصاصی (Dark Theme Ready):** تولید کدهای کدهای HTML با استایل‌های پیشرفته که با قالب طراحی شده وبلاگ کاملاً هماهنگ است و دارای باکس زیبای "منبع خبر" می‌باشد.

### ⚙️ نحوه نصب و پیش‌نیازها

۱. ابتدا نیازمندی‌های پروژه (پکیج‌ها) را نصب کنید:
```bash
pip install -r requirements.txt
```

۲. فایل `.env` را ایجاد کرده و توکن‌ها و اطلاعات زیر را تنظیم کنید:
```env
BLOG_ID=your_blog_id
GEMINI_API_KEY=your_api_key
```
* **نکته مهم:** حتماً فایل تایید هویت گوگل خود یعنی `credentials.json` (برای Blogger API) را داخل این پوشه قرار دهید.

### ▶️ نحوه اجرا

**۱. اجرای یک‌باره (Manual Run):**
مناسب برای زمانی که می‌خواهید به صورت دستی اجرای ربات را فقط یکبار انجام دهید تا اخبار جدید چک شوند:
```bash
python main.py --once
```

**۲. اجرای همیشگی و خودکار (Continuous Loop):**
ربات روشن می‌ماند و طبق زمان‌بندی داخلی (پیش‌فرض هر ۵ ساعت) سایت‌ها را بررسی می‌کند:
```bash
python main.py
```

**۳. اجرای خودکار بدون نیاز به سرور شخصی (Github Actions):**
پروژه برای اجرای کاملاً خودکار و رایگان روی سرورهای گیت‌هاب پیکربندی شده است (در فایل `news_bot.yml`). برای این منظور کافیست متغیرهای زیر را در بخش **Settings > Secrets and variables > Actions** مخزن گیت‌هاب خود تعریف کنید:
* `BLOG_ID`
* `GEMINI_API_KEY`
* `GOOGLE_CREDENTIALS_JSON` (محتوای کامل فایل جیسون احراز هویت)
* `GOOGLE_TOKEN_PICKLE` (محتوای توکن احراز هویت کدگذاری شده با Base64)

---
**License**: MIT  
**Developed by**: AmirCode97
