# Blogger News Bot

ربات خودکار دریافت اخبار حقوق بشر و ارسال به وبلاگ Blogger

## منابع خبری

- کانون دفاع از حقوق بشر در ایران (بشریت)
- مجموعه فعالان حقوق بشر در ایران (HRA)

## نصب و اجرا

### ۱. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### ۲. تنظیم متغیرهای محیطی

فایل `.env` را ویرایش کنید و مقادیر را وارد کنید.

### ۳. اجرای یکباره (تست)

```bash
python main.py --once
```

### ۴. اجرای زمان‌بندی شده

```bash
python main.py
```

## تنظیم GitHub Actions

برای اجرای خودکار در GitHub:

1. Repository را به GitHub push کنید
2. به Settings → Secrets and variables → Actions بروید
3. این Secrets را اضافه کنید:
   - `BLOG_ID`: شناسه وبلاگ
   - `GEMINI_API_KEY`: کلید API جمینای
   - `GOOGLE_CREDENTIALS_JSON`: محتوای فایل credentials.json

## لایسنس

MIT
