
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai
from blogger_poster import BloggerPoster
from dotenv import load_dotenv
import json

# بارگذاری متغیرها
load_dotenv()

# تنظیمات خبر خاص
TARGET_URL = "https://eutoday.net/iran-irgc-and-the-end-of-europes-strategic-patience/"

# بیوگرافی فارسی
AUTHOR_BIO_FA = """
<hr>
<div style="background-color: #f9f9f9; padding: 20px; border-right: 5px solid #2c3e50; margin-top: 30px;">
    <div style="display: flex; align-items: center; margin-bottom: 15px;">
        <h3 style="margin: 0; color: #2c3e50; font-family: Tahoma, sans-serif;">درباره نویسنده: حسین امجدی</h3>
    </div>
    <p style="text-align: justify; font-size: 0.95em; line-height: 1.8; font-family: Tahoma, sans-serif;">
        حسین امجدی، فعال حقوق بشر ایرانی ساکن اوبرهاوزن آلمان و عضو انجمن <strong>VVMIran e.V.</strong> (انجمن دفاع از حقوق بشر در ایران) است. 
        او پس از مواجهه با تهدیدات جدی جانی، مجبور به ترک ایران شد. تمرکز نوشته‌های او بر سرکوب دولتی، هدف قرار گرفتن بازداشت‌شدگان و معترضان، و وضعیت زنان در ایران است.
    </p>
    <p style="text-align: justify; font-size: 0.95em; line-height: 1.8; font-family: Tahoma, sans-serif;">
        امجدی همچنین مهندس نرم‌افزار با تخصص در زیرساخت‌های حیاتی است و پژوهش‌های او بر شناسایی شبکه‌های فنی و مالی که امکان سرکوب فراملی را برای رژیم فراهم می‌کنند، متمرکز می‌باشد.
    </p>
</div>
"""

def fetch_article_content(url):
    print(f"🌐 Fetching article from: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # استخراج تیتر
        title_tag = soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else "News Article"
        
        # استخراج متن اصلی
        article_body = soup.find('article') or soup.find('div', class_='entry-content') or soup.find('div', class_='post-content')
        
        paragraphs = []
        if article_body:
            for p in article_body.find_all('p'):
                text = p.get_text().strip()
                if len(text) > 20:
                    paragraphs.append(text)
        
        full_text = "\n\n".join(paragraphs)
        
        # استخراج تصویر اصلی
        image_url = None
        img_tag = soup.find('meta', property='og:image')
        if img_tag:
            image_url = img_tag.get('content')
            
        print(f"✅ Fetched: {title}")
        return {
            "title": title,
            "link": url,
            "full_content": full_text,
            "image_url": image_url,
            "source": "EU Today",
            "fetched_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error fetching article: {e}")
        return None

def process_and_post_manual():
    # 1. دریافت مقاله
    article = fetch_article_content(TARGET_URL)
    if not article:
        return

    # 2. راه اندازی کلاینت بلاگر
    try:
        poster = BloggerPoster()
        if not poster.service:
            print("❌ Blogger API auth failed")
            return
    except Exception as e:
        print(f"❌ Error initializing BloggerPoster: {e}")
        return

    # 3. پردازش (بدون هوش مصنوعی به دلیل انقضای کلید)
    print("⚠️ AI API Expired. Using original content...")
    
    fa_title = article['title']
    # تبدیل متن ساده به پاراگراف‌های HTML
    article_paragraphs = article['full_content'].split('\n\n')
    fa_body = "".join([f"<p>{p}</p>" for p in article_paragraphs])
    
    # 4. افزودن تصویر
    final_html = ""
    if article['image_url']:
        final_html += f'<div class="separator" style="clear: both; text-align: center;"><img border="0" src="{article["image_url"]}" style="display: block; padding: 1em 0; text-align: center; width: 100%; max-width: 800px;" /></div><br/>'
    
    final_html += fa_body
    
    # 5. افزودن بیوگرافی نویسنده
    final_html += "<br><br>" + AUTHOR_BIO_FA
    
    # 6. انتشار در بلاگر
    print(f"🚀 Publishing: {fa_title}")
    
    body = {
        "kind": "blogger#post",
        "blog": {"id": os.getenv("BLOG_ID")},
        "title": fa_title,
        "content": final_html,
        "labels": ["خبر فوری", "گزارش ویژه", "بین‌الملل", "حسین امجدی", "English"]
    }
    
    try:
        posts = poster.service.posts()
        result_post = posts.insert(blogId=os.getenv("BLOG_ID"), body=body, isDraft=False).execute()
        print(f"✅ Successfully published! URL: {result_post.get('url')}")
    except Exception as e:
        print(f"❌ Error during posting: {e}")

if __name__ == "__main__":
    process_and_post_manual()
