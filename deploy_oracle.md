# 🚀 راهنمای نصب Blogger News Bot روی سرور Oracle

## ۱. اتصال به سرور

```bash
ssh opc@<IP_SERVER>
```

## ۲. نصب پیش‌نیازها

```bash
# به‌روزرسانی سیستم
sudo yum update -y

# نصب Python 3.9+
sudo yum install python3 python3-pip git -y

# نصب screen برای اجرای دائمی
sudo yum install screen -y
```

## ۳. کپی کردن پروژه به سرور

**از کامپیوتر محلی:**

```bash
scp -r C:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot opc@<IP_SERVER>:~/
```

**یا با Git:**

```bash
cd ~
git clone <your-repo-url> blogger-news-bot
```

## ۴. تنظیم پروژه

```bash
cd ~/blogger-news-bot

# نصب کتابخانه‌ها
pip3 install -r requirements.txt

# مطمئن شوید فایل .env و credentials.json موجود است
ls -la .env credentials.json
```

## ۵. تست اجرا

```bash
python3 main.py --test
```

## ۶. راه‌اندازی سرویس Systemd (اجرای خودکار دائمی)

```bash
# ایجاد فایل سرویس
sudo nano /etc/systemd/system/blogger-bot.service
```

**محتوای فایل سرویس:**

```ini
[Unit]
Description=Blogger News Bot
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/blogger-news-bot
ExecStart=/usr/bin/python3 /home/opc/blogger-news-bot/main.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

```bash
# فعال‌سازی و اجرا
sudo systemctl daemon-reload
sudo systemctl enable blogger-bot
sudo systemctl start blogger-bot

# بررسی وضعیت
sudo systemctl status blogger-bot

# مشاهده لاگ‌ها
sudo journalctl -u blogger-bot -f
```

## ۷. دستورات مفید

```bash
# توقف ربات
sudo systemctl stop blogger-bot

# ری‌استارت ربات
sudo systemctl restart blogger-bot

# مشاهده لاگ‌های امروز
sudo journalctl -u blogger-bot --since today

# مشاهده ۱۰۰ خط آخر لاگ
sudo journalctl -u blogger-bot -n 100
```

---

## ⚙️ تنظیمات فعلی

| پارامتر | مقدار |
|---------|-------|
| اخبار در هر اجرا | ۵ خبر |
| فاصله اجرا | هر ۵ ساعت |
| اخبار روزانه | ~۲۰ خبر |
| گزارش تلگرام | بعد از هر اجرا ✅ |

---

## 🔒 نکات امنیتی

1. فایل `credentials.json` و `.env` را در Git قرار ندهید
2. دسترسی SSH را فقط با کلید تنظیم کنید
3. Firewall سرور را روشن نگه دارید
