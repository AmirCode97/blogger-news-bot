"""
FINAL RESTORATION: Fix the EU Today post + add images to placeholder posts
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os, pickle, re, time, json
from dotenv import load_dotenv
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup

load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

import urllib3
urllib3.disable_warnings()

def fetch_with_googlebot(url):
    """Fetch with Googlebot UA"""
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
            
            content_div = (soup.find('div', class_='entry-content') 
                          or soup.find('article')
                          or soup.find('div', class_='post-content')
                          or soup.find('main'))
            
            if content_div:
                for p in content_div.find_all('p'):
                    text = p.get_text().strip()
                    if len(text) > 30 and 'cookie' not in text.lower():
                        paragraphs.append(text)
            
            if not paragraphs:
                meta = soup.find('meta', {'name': 'description'}) or soup.find('meta', property='og:description')
                if meta:
                    desc = meta.get('content', '')
                    if len(desc) > 50:
                        paragraphs = [desc]
            
            return "\n\n".join(paragraphs[:15]), image
    except Exception as e:
        print(f"      Error: {e}")
    return None, None

def build_post_html(content, image_url, source_url, source_name):
    """Build properly formatted post HTML"""
    image_html = ""
    if image_url:
        image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{image_url}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>'
    
    content_with_break = content
    if "\n" in content:
        parts = content.split("\n", 1)
        content_with_break = parts[0] + "\n<!--more-->\n" + parts[1]
    elif len(content) > 300:
        content_with_break = content[:300] + "<!--more-->" + content[300:]
    
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
# Get ALL posts
# ============================================
all_posts = []
page_token = None
while True:
    result = service.posts().list(blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

print(f"📊 Final Restoration - {len(all_posts)} posts\n")

fixed = 0

for i, post in enumerate(all_posts, 1):
    title = post.get("title", "")
    content = post.get("content", "")
    post_id = post.get("id")
    
    text_only = re.sub(r'<[^>]+>', '', content).strip()
    clean_text = re.sub(r'منبع اصلی مقاله:.*', '', text_only).strip()
    clean_text = re.sub(r'مشاهده در.*', '', clean_text).strip()
    has_image = bool(re.search(r'<img\s', content))
    
    needs_fix = False
    
    # Case 1: Empty post (< 100 chars real text)
    if len(clean_text) < 100:
        needs_fix = True
    # Case 2: Has placeholder text but no image
    elif not has_image and len(clean_text) < 500:
        needs_fix = True
    
    if not needs_fix:
        continue
    
    print(f"\n🔧 [{i}] {title[:60]}...")
    print(f"      Text: {len(clean_text)} chars, Image: {'✅' if has_image else '❌'}")
    
    # Extract source info
    source_match = re.search(r'<a\s+href="([^"]*)"[^>]*>مشاهده در ([^<]*)</a>', content)
    source_url = source_match.group(1) if source_match else "#"
    source_name = source_match.group(2) if source_match else "منبع"
    
    article_text = None
    article_image = None
    
    # Try to fetch real content
    if source_url.startswith('http'):
        print(f"      📡 Fetching: {source_url[:50]}...")
        article_text, article_image = fetch_with_googlebot(source_url)
    
    if article_text and len(article_text) > 100:
        # Full restore with fetched content
        new_html = build_post_html(article_text, article_image, source_url, source_name)
        try:
            service.posts().patch(
                blogId=BLOG_ID, postId=post_id,
                body={"content": new_html}
            ).execute()
            fixed += 1
            print(f"      ✅ Full restore! ({len(article_text)} chars, image: {'✅' if article_image else '❌'})")
            time.sleep(2)
        except Exception as e:
            print(f"      ❌ Error: {e}")
    elif not has_image and article_image:
        # Add image to existing placeholder content
        # Extract existing text div content
        existing_text = clean_text if clean_text.startswith('بر اساس') else f"بر اساس گزارش‌های رسیده، {title}\n\nجزئیات بیشتر این خبر به‌زودی منتشر خواهد شد. برای مشاهده متن کامل خبر، لطفاً به منبع اصلی مراجعه کنید."
        new_html = build_post_html(existing_text, article_image, source_url, source_name)
        try:
            service.posts().patch(
                blogId=BLOG_ID, postId=post_id,
                body={"content": new_html}
            ).execute()
            fixed += 1
            print(f"      ✅ Added image!")
            time.sleep(2)
        except Exception as e:
            print(f"      ❌ Error: {e}")
    else:
        print(f"      ⏭️  No better content available")

print(f"\n{'='*70}")
print(f"✅ Fixed: {fixed}")
print(f"{'='*70}")
