"""
EMERGENCY: Restore posts from their source URLs
Since content was wiped, we need to re-fetch from original sources and rebuild posts.
This script:
1. Gets all posts that are empty (only have source box)
2. Extracts the source URL from the source box
3. Re-fetches the article from the source
4. Rebuilds the post with correct formatting
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os, pickle, re, time, json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fa,en-US;q=0.9,en;q=0.8',
})

def fetch_article(url):
    """Fetch full article content from source URL"""
    try:
        resp = session.get(url, timeout=30, verify=False)
        if resp.status_code != 200:
            return None, None
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        paragraphs = []
        main_image = None
        
        # Get og:image
        og_img = soup.find('meta', property='og:image')
        if og_img:
            main_image = og_img.get('content')
        
        # Iran HRS / Iran HRM
        if 'iranhrs.org' in url or 'iran-hrm.com' in url:
            content_div = soup.find('div', class_='entry-content') or soup.find('article')
            if content_div:
                for p in content_div.find_all(['p', 'div']):
                    text = p.get_text().strip()
                    if len(text) > 50 and 'cookie' not in text.lower() and 'share' not in text.lower():
                        paragraphs.append(text)
            if not main_image and content_div:
                img = content_div.find('img')
                if img:
                    main_image = urljoin(url, img.get('src', ''))
        
        # Iran International
        elif 'iranintl.com' in url:
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                paragraphs.append(meta_desc.get('content', ''))
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'articleBody' in data:
                        paragraphs = [data['articleBody']]
                        break
                except: pass
        
        # LokalKlick
        elif 'lokalklick.eu' in url:
            content_div = soup.find('div', class_='entry-content') or soup.find('article')
            if content_div:
                for p in content_div.find_all('p'):
                    text = p.get_text().strip()
                    if len(text) > 30:
                        paragraphs.append(text)
            if not main_image and content_div:
                img = content_div.find('img')
                if img:
                    main_image = urljoin(url, img.get('src', ''))
        
        # IranHR.net
        elif 'iranhr.net' in url:
            content_div = soup.find('div', class_='entry-content') or soup.find('article') or soup.find('div', class_='post-content')
            if content_div:
                for p in content_div.find_all(['p']):
                    text = p.get_text().strip()
                    if len(text) > 50:
                        paragraphs.append(text)
            if not main_image and content_div:
                img = content_div.find('img')
                if img:
                    main_image = urljoin(url, img.get('src', ''))
        
        # Generic
        else:
            content_div = (soup.find('article') or soup.find('div', class_='entry-content') 
                          or soup.find('div', class_='post-content') or soup.find('main'))
            if content_div:
                for p in content_div.find_all('p'):
                    text = p.get_text().strip()
                    if len(text) > 50:
                        paragraphs.append(text)
        
        full_text = "\n\n".join(paragraphs[:15])
        return full_text, main_image
    
    except Exception as e:
        print(f"      Error fetching: {e}")
        return None, None

def build_post_html(content, image_url, source_url, source_name):
    """Build properly formatted post HTML"""
    image_html = ""
    if image_url:
        image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{image_url}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>'
    
    # Insert jump break after first paragraph
    content_with_break = content
    if "\n" in content:
        parts = content.split("\n", 1)
        content_with_break = parts[0] + "\n<!--more-->\n" + parts[1]
    elif len(content) > 300:
        content_with_break = content[:300] + "<!--more-->" + content[300:]
    
    html = f"""
                <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
                {image_html}
                
                <!-- Persian Section -->
                <div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
                    {content_with_break}
                </div>
                
                <!-- Premium Source Box -->
                <div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
                    <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
                        <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
                        <a href="{source_url}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در {source_name}</a>
                    </p>
                </div>
                """
    return html

# ============================================
# MAIN: Find and restore empty posts
# ============================================
all_posts = []
page_token = None
while True:
    result = service.posts().list(blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

print(f"📊 Scanning {len(all_posts)} posts for empty content...\n")

restored = 0
failed = 0

for i, post in enumerate(all_posts, 1):
    title = post.get("title", "")
    content = post.get("content", "")
    post_id = post.get("id")
    
    # Check if post is empty (only has source box, no real content)
    text_only = re.sub(r'<[^>]+>', '', content).strip()
    # Remove source box text
    clean_text = re.sub(r'منبع اصلی مقاله:.*', '', text_only).strip()
    clean_text = re.sub(r'مشاهده در.*', '', clean_text).strip()
    
    if len(clean_text) > 100:
        # Post has content, skip
        continue
    
    # This post is empty - try to restore
    print(f"\n🔧 [{i}] Restoring: {title[:60]}...")
    
    # Extract source URL from the source box
    source_match = re.search(r'<a\s+href="([^"]*)"[^>]*>مشاهده در ([^<]*)</a>', content)
    if not source_match:
        print(f"      ❌ Could not find source URL")
        failed += 1
        continue
    
    source_url = source_match.group(1)
    source_name = source_match.group(2)
    print(f"      📎 Source: {source_url[:70]}...")
    
    # Fetch original article
    article_text, article_image = fetch_article(source_url)
    
    if not article_text or len(article_text) < 50:
        print(f"      ❌ Could not fetch article content (got {len(article_text or '')} chars)")
        failed += 1
        continue
    
    print(f"      📝 Got {len(article_text)} chars, image: {'✅' if article_image else '❌'}")
    
    # Build new HTML
    new_html = build_post_html(article_text, article_image, source_url, source_name)
    
    # Update the post
    try:
        service.posts().patch(
            blogId=BLOG_ID,
            postId=post_id,
            body={"content": new_html}
        ).execute()
        restored += 1
        print(f"      ✅ Restored!")
        time.sleep(2)  # API rate limit
    except Exception as e:
        print(f"      ❌ Update failed: {e}")
        failed += 1

print(f"\n{'='*70}")
print(f"📊 RESTORATION RESULTS:")
print(f"   ✅ Restored: {restored}")
print(f"   ❌ Failed: {failed}")
print(f"{'='*70}")
