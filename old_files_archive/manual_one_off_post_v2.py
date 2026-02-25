
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

TARGET_URL = "https://eutoday.net/iran-irgc-and-the-end-of-europes-strategic-patience/"

# آدرس تصویر نویسنده (اگر نداریم، از یک آواتار یا مستقیماً تصویر ارسالی استفاده می‌کنیم)
# برای تست، من یک تصویر فرضی می‌گذارم یا فضای آن را آماده می‌کنم
AUTHOR_IMG_URL = "https://i.ibb.co/vzG7ZzY/hossein-amjadi.jpg" # این لینک را با لینک واقعی جایگزین کنید

AUTHOR_BIO_FA_HTML = """
<div style="background-color: #ffffff; padding: 25px; border-top: 1px solid #e1e4e8; border-bottom: 1px solid #e1e4e8; margin-top: 40px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; align-items: flex-start; gap: 20px; direction: rtl;">
    <div style="flex-shrink: 0;">
        <img src="https://i.postimg.cc/T3PzNf0v/hossein-amjadi.png" alt="Hossein Amjadi" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 1px solid #ddd;">
    </div>
    <div style="flex-grow: 1;">
        <h3 style="margin: 0 0 10px 0; color: #1a1a1a; font-size: 1.2em; font-weight: bold; text-transform: uppercase;">HOSSEIN AMJADI</h3>
        <p style="margin: 0; color: #333; line-height: 1.8; text-align: justify; font-size: 0.95em;">
            حسین امجدی، فعال حقوق بشر ایرانی ساکن اوبرهاوزن آلمان و عضو انجمن <strong>VVMIran e.V.</strong> (انجمن دفاع از حقوق بشر در ایران) است. 
            او پس از مواجهه با تهدیدات جدی جانی، مجبور به ترک ایران شد. تمرکز نوشته‌های او بر سرکوب دولتی، هدف قرار گرفتن بازداشت‌شدگان و معترضان، و وضعیت زنان در ایران است. 
            امجدی همچنین مهندس نرم‌افزار با تخصص در زیرساخت‌های حیاتی است و پژوهش‌های او بر شناسایی شبکه‌های فنی و مالی که امکان سرکوب فراملی را برای رژیم فراهم می‌کنند، متمرکز می‌باشد.
        </p>
    </div>
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
        
        title_tag = soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else "News Article"
        
        article_body = soup.find('article') or soup.find('div', class_='entry-content') or soup.find('div', class_='post-content')
        
        paragraphs = []
        if article_body:
            for p in article_body.find_all('p'):
                text = p.get_text().strip()
                if len(text) > 20:
                    paragraphs.append(text)
        
        full_text = "\n\n".join(paragraphs)
        
        image_url = None
        img_tag = soup.find('meta', property='og:image')
        if img_tag:
            image_url = img_tag.get('content')
            
        return {
            "title": title,
            "link": url,
            "full_content": full_text,
            "image_url": image_url
        }
    except Exception as e:
        print(f"❌ Error fetching: {e}")
        return None

def run_translation_and_post():
    article = fetch_article_content(TARGET_URL)
    if not article: return

    # تنظیم API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    
    genai.configure(api_key=api_key)
    
    print("🤖 Translating with AI...")
    prompt = f"""
    Translate this Investigative news article to Persian. 
    Return as JSON: {{"title": "...", "body_html": "..."}}
    
    Article Original Title: {article['title']}
    Content: {article['full_content'][:7000]}
    
    Instructions:
    - Use professional, formal Persian.
    - Title should be impactful.
    - Format body with HTML <p> tags.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        fa_title = result['title']
        fa_body = result['body_html']
        
        # ترکیب محتوا
        final_html = ""
        if article['image_url']:
            final_html += f'<div style="text-align: center;"><img src="{article["image_url"]}" style="width: 100%; max-width: 800px; border-radius: 8px;"></div><br>'
        
        final_html += fa_body
        final_html += AUTHOR_BIO_FA_HTML
        
        # انتشار در بلاگر
        poster = BloggerPoster()
        if not poster.service:
            print("❌ Blogger Auth Failed")
            return
            
        print(f"🚀 Publishing: {fa_title}")
        body = {
            "kind": "blogger#post",
            "blog": {"id": os.getenv("BLOG_ID")},
            "title": fa_title,
            "content": final_html,
            "labels": ["گزارش ویژه", "بین‌الملل", "حسین امجدی"]
        }
        
        result_post = poster.service.posts().insert(blogId=os.getenv("BLOG_ID"), body=body, isDraft=False).execute()
        print(f"✅ Published successfully! URL: {result_post.get('url')}")
        
    except Exception as e:
        print(f"❌ Processing Error: {e}")

if __name__ == "__main__":
    run_translation_and_post()
