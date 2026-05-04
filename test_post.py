import requests
from blogger_poster import BloggerPoster

# تنظیمات پوستر
poster = BloggerPoster()

# اطلاعات خبر (بازنویسی شده توسط هوش مصنوعی)
title = "فاجعه خاموش در محیط‌های کاری: سایه مرگ و مصدومیت بر سر هزاران کارگر ایرانی"

# متن خبر در ۱۳ خط (سئو شده)
description = """آمارها و حوادث اخیر نشان می‌دهد که بحران ایمنی در محیط‌های کاری ایران ابعاد نگران‌کننده‌ای به خود گرفته است. در تازه‌ترین رویداد تلخ، وقوع آتش‌سوزی در یک کارخانه تولید چسب در منطقه اقدسیه شهرستان چهارباغ واقع در استان البرز، منجر به مصدومیت دست‌کم ۹ کارگر شد که همگی توسط تیم‌های امدادی تحت درمان قرار گرفتند. این حوادث در حالی رخ می‌دهد که آمار رسمی تلفات نیروی کار در نقاط مختلف کشور، از جمله مازندران، شیب تندی به خود گرفته است. تنها در سال گذشته، ۱۲۲ کارگر در استان مازندران بر اثر سوانح شغلی جان خود را از دست دادند و نزدیک به ۹۰۰ نفر دیگر با مصدومیت‌های جدی مواجه شدند که نشان‌دهنده رشد ۱۲ درصدی تلفات نسبت به سال قبل از آن است. سقوط از ارتفاع و برخورد با اجسام سخت، اصلی‌ترین عوامل مرگبار در این استان گزارش شده‌اند که شهر ساری با بالاترین میزان تلفات در صدر این فهرست قرار دارد. فقدان ایمنی و تجهیزات حفاظتی، جان هزاران نفر را روزانه به خطر می‌اندازد. بر اساس آمارهای کلان، سالانه بیش از ۱۲۰۰ نفر در سراسر کشور قربانی سوانح کار می‌شوند و هزاران مورد آسیب‌دیدگی جسمی ثبت می‌گردد. کارشناسان بر این باورند که نبود امنیت شغلی، ضعف شدید در زیرساخت‌های ایمنی و کمبود نظارت‌های قانونی، کارگران را در برابر خطرات محیطی کاملاً بی‌دفاع رها کرده است."""

# افزودن Read More
if "\n" in description:
    parts = description.split("\n", 1)
    description_with_break = parts[0] + "\n<!--more-->\n" + parts[1]
else:
    description_with_break = description[:300] + "<!--more-->" + description[300:]

# آدرس یک عکس باکیفیت مرتبط (برای تست)
img_url = "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80"

# ساخت قالب HTML
html_content = f"""
<style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
<div style="margin-bottom:25px;text-align:center;"><img src="{img_url}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>

<!-- Persian Section -->
<div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
    {description_with_break}
</div>

<!-- Source Box -->
<div style="text-align: right; direction: rtl;">
    <div style="background:#1a1a1a; padding:12px 25px; border-radius:8px; border-right:3px solid #c0392b; font-weight:bold; color:#ddd; display:inline-block; margin:30px 0 10px 0; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);">
        <span style="color:#c0392b; margin-left:8px;">خبرگزاری:</span> iranpolnews
    </div>
</div>
"""

# ارسال به بلاگر در دسته‌بندی کارگران
result = poster.create_post(title, html_content, labels=["کارگران"])

if result:
    print(f"✅ پست با موفقیت منتشر شد: {result.get('url')}")
else:
    print("❌ خطایی در ارسال پست رخ داد.")
