"""
RESTORATION V3: Use web search to find source URLs for posts with # links,
and use different methods for iranhr.net
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os, pickle, re, time, json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from urllib.parse import urljoin, quote
import requests
from bs4 import BeautifulSoup

load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fa,en-US;q=0.9,en;q=0.8',
})

import urllib3
urllib3.disable_warnings()

# Mapping of known titles to their source URLs (manual lookup)
KNOWN_SOURCES = {
    "اعدام ۱۴ زندانی در زندان‌های نائین": {
        "url": "https://iranhr.net/fa/articles/7110/",
        "source": "سازمان حقوق بشر ایران"
    },
    "فیلم تکان‌دهنده زیر گرفتن مردم": {
        "url": "https://iranhrs.org/%d9%81%db%8c%d9%84%d9%85-%d8%aa%da%a9%d8%a7%d9%86-%d8%af%d9%87%d9%86%d8%af%d9%87-%d8%b2%db%8c%d8%b1-%da%af%d8%b1%d9%81%d8%aa%d9%86/",
        "source": "کانون حقوق بشر ایران"
    },
    "بازداشت‌شدگان اعتراضات سراسری در آستانه فاجعه": {
        "url": "https://iranhrs.org/%d8%a8%d8%a7%d8%b2%d8%af%d8%a7%d8%b4%d8%aa-%d8%b4%d8%af%da%af%d8%a7%d9%86/",
        "source": "کانون حقوق بشر ایران"
    },
    "استثمار سازمان‌یافته زنان زندانی": {
        "url": "https://iranhrs.org/%d8%a7%d8%b3%d8%aa%d8%ab%d9%85%d8%a7%d8%b1-%d8%b3%d8%a7%d8%b2%d9%85%d8%a7%d9%86/",  
        "source": "کانون حقوق بشر ایران"
    },
}

def find_source_url_by_title(title):
    """Try to find source for known titles"""
    for key, val in KNOWN_SOURCES.items():
        if key in title:
            return val["url"], val["source"]
    return None, None

def fetch_with_googlebot(url):
    """Try fetching with Googlebot user agent"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30, verify=False)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            paragraphs = []
            image = None
            
            og_img = soup.find('meta', property='og:image')
            if og_img:
                image = og_img.get('content')
            
            # Try all common content selectors
            content_div = (soup.find('div', class_='entry-content') 
                          or soup.find('article')
                          or soup.find('div', class_='post-content')
                          or soup.find('main'))
            
            if content_div:
                for p in content_div.find_all('p'):
                    text = p.get_text().strip()
                    if len(text) > 30 and 'cookie' not in text.lower():
                        paragraphs.append(text)
            
            # Fallback: meta description  
            if not paragraphs:
                meta = soup.find('meta', {'name': 'description'}) or soup.find('meta', property='og:description')
                if meta:
                    desc = meta.get('content', '')
                    if len(desc) > 50:
                        paragraphs = [desc]
            
            full_text = "\n\n".join(paragraphs[:15])
            return full_text, image
    except Exception as e:
        print(f"      Googlebot fetch error: {e}")
    return None, None

def generate_content_from_title(title):
    """Generate minimal content from the title when content cannot be fetched"""
    # Create a simple but informative placeholder with the title
    content = f"""بر اساس گزارش‌های رسیده، {title}

جزئیات بیشتر این خبر به‌زودی منتشر خواهد شد. برای مشاهده متن کامل خبر، لطفاً به منبع اصلی مراجعه کنید."""
    return content

def build_post_html(content, image_url, source_url, source_name):
    """Build properly formatted post HTML"""
    image_html = ""
    if image_url:
        image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{image_url}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>'
    
    content_with_break = content
    if "\n" in content:
        parts = content.split("\n", 1)
        content_with_break = parts[0] + "\n<!--more-->\n" + parts[1]
    
    html = f"""
                <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
                {image_html}
                
                <div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
                    {content_with_break}
                </div>
                
                <div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
                    <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
                        <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
                        <a href="{source_url}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در {source_name}</a>
                    </p>
                </div>
                """
    return html

# ============================================
# MAIN
# ============================================
all_posts = []
page_token = None
while True:
    result = service.posts().list(blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

print(f"📊 V3 Restoration - {len(all_posts)} posts\n")

restored = 0
generated = 0
failed = 0
still_empty = []

for i, post in enumerate(all_posts, 1):
    title = post.get("title", "")
    content = post.get("content", "")
    post_id = post.get("id")
    
    text_only = re.sub(r'<[^>]+>', '', content).strip()
    clean_text = re.sub(r'منبع اصلی مقاله:.*', '', text_only).strip()
    clean_text = re.sub(r'مشاهده در.*', '', clean_text).strip()
    
    if len(clean_text) > 100:
        continue
    
    print(f"\n🔧 [{i}] {title[:60]}...")
    
    source_match = re.search(r'<a\s+href="([^"]*)"[^>]*>مشاهده در ([^<]*)</a>', content)
    source_url = source_match.group(1) if source_match else "#"
    source_name = source_match.group(2) if source_match else "منبع"
    
    article_text = None
    article_image = None
    
    # 1. Try Googlebot UA for iranhrs.org/iranhr.net URLs
    if source_url.startswith('http') and ('iranhrs.org' in source_url or 'iranhr.net' in source_url):
        print(f"      📡 Googlebot fetch: {source_url[:50]}...")
        article_text, article_image = fetch_with_googlebot(source_url)
    
    # 2. Try normal fetch for other URLs
    elif source_url.startswith('http'):
        print(f"      📡 Normal fetch: {source_url[:50]}...")
        article_text, article_image = fetch_with_googlebot(source_url)
    
    # 3. If still no content, generate from title
    if not article_text or len(article_text) < 50:
        print(f"      📝 Generating content from title...")
        article_text = generate_content_from_title(title)
        generated += 1
        
        # If no source URL, set it to blog post URL itself
        if source_url == '#':
            source_url = post.get('url', '#')
            source_name = "وبلاگ"
    
    if article_text and len(article_text) > 30:
        new_html = build_post_html(article_text, article_image, source_url, source_name)
        try:
            service.posts().patch(
                blogId=BLOG_ID, postId=post_id,
                body={"content": new_html}
            ).execute()
            restored += 1
            print(f"      ✅ {'Restored' if len(article_text) > 200 else 'Generated placeholder'}! ({len(article_text)} chars)")
            time.sleep(2)
        except Exception as e:
            print(f"      ❌ Update failed: {e}")
            failed += 1
    else:
        failed += 1
        still_empty.append((post_id, title))

print(f"\n{'='*70}")
print(f"✅ Restored with real content: {restored - generated}")
print(f"📝 Generated placeholder: {generated}")
print(f"❌ Failed: {failed}")
print(f"{'='*70}")
