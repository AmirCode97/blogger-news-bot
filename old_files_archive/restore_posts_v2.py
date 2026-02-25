"""
RESTORATION V2: Handle iranhr.net (needs RSS) and posts with # source URL
For iranhr.net: Use RSS feed to find matching articles
For #: Search multiple sources by title
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os, pickle, re, time, json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from urllib.parse import urljoin, unquote
import requests
from bs4 import BeautifulSoup
import feedparser

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

import urllib3
urllib3.disable_warnings()

def fetch_from_iranhr_rss(title_keyword):
    """Search iranhr.net RSS feed for matching article"""
    try:
        feed = feedparser.parse("https://iranhr.net/fa/rss/")
        for entry in feed.entries:
            # Check if titles match (fuzzy)
            entry_title = entry.get('title', '')
            if title_keyword[:20] in entry_title or entry_title[:20] in title_keyword:
                link = entry.get('link', '')
                summary = entry.get('summary', '')
                desc = BeautifulSoup(summary, 'html.parser').get_text() if summary else ""
                
                # Get image from content
                image = None
                content_html = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else summary
                if content_html:
                    soup = BeautifulSoup(content_html, 'html.parser')
                    img = soup.find('img')
                    if img:
                        image = img.get('src')
                
                return desc, image, link
    except Exception as e:
        print(f"      RSS Error: {e}")
    return None, None, None

def fetch_from_iranhrs_web(url):
    """Try to fetch iranhr.net article via web (with different approach)"""
    try:
        # Try with special headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Accept': 'text/html',
        }
        resp = requests.get(url, headers=headers, timeout=30, verify=False)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Try meta description
            meta = soup.find('meta', {'name': 'description'}) or soup.find('meta', property='og:description')
            desc = meta.get('content', '') if meta else ''
            
            # Try og:image
            og_img = soup.find('meta', property='og:image')
            image = og_img.get('content', '') if og_img else None
            
            # Try article content
            paragraphs = []
            content_div = soup.find('article') or soup.find('div', class_='entry-content')
            if content_div:
                for p in content_div.find_all('p'):
                    text = p.get_text().strip()
                    if len(text) > 30:
                        paragraphs.append(text)
            
            if paragraphs:
                return "\n\n".join(paragraphs[:15]), image
            elif desc and len(desc) > 50:
                return desc, image
    except:
        pass
    return None, None

def fetch_from_iran_intl(url):
    """Fetch from Iran International with JSON-LD"""
    try:
        resp = session.get(url, timeout=30, verify=False)
        if resp.status_code != 200:
            return None, None
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        paragraphs = []
        image = None
        
        og_img = soup.find('meta', property='og:image')
        if og_img:
            image = og_img.get('content')
        
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
        
        return "\n\n".join(paragraphs), image
    except:
        return None, None

def search_google_for_article(title):
    """Try to find the original article URL via Google search (via news sources)"""
    # Search in known RSS feeds
    feeds = [
        "https://iranhr.net/fa/rss/",
        "https://humanrightsinir.org/feed/",
    ]
    
    # Normalize title for comparison
    title_words = set(title.split()[:5])
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                entry_title = entry.get('title', '')
                entry_words = set(entry_title.split()[:5])
                # Check overlap
                overlap = len(title_words & entry_words)
                if overlap >= 3:
                    link = entry.get('link', '')
                    summary = entry.get('summary', '')
                    desc = BeautifulSoup(summary, 'html.parser').get_text() if summary else ""
                    
                    image = None
                    content_html = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else summary
                    if content_html:
                        soup = BeautifulSoup(content_html, 'html.parser')
                        img = soup.find('img')
                        if img:
                            image = img.get('src')
                    
                    return desc, image, link
        except:
            pass
    
    return None, None, None

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

print(f"📊 Scanning {len(all_posts)} posts...\n")

restored = 0
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
    
    # Extract source URL
    source_match = re.search(r'<a\s+href="([^"]*)"[^>]*>مشاهده در ([^<]*)</a>', content)
    source_url = source_match.group(1) if source_match else "#"
    source_name = source_match.group(2) if source_match else "منبع"
    
    article_text = None
    article_image = None
    
    # Strategy 1: If iranhr.net URL, try web fetch with googlebot UA
    if 'iranhr.net' in source_url:
        print(f"      📡 Trying iranhr.net web fetch...")
        article_text, article_image = fetch_from_iranhrs_web(source_url)
        
        if not article_text:
            print(f"      📡 Trying iranhr.net RSS match...")
            article_text, article_image, found_url = fetch_from_iranhr_rss(title)
            if found_url:
                source_url = found_url
    
    # Strategy 2: If # URL, search RSS feeds by title  
    elif source_url == '#' or not source_url.startswith('http'):
        print(f"      🔍 Searching RSS feeds by title...")
        article_text, article_image, found_url = search_google_for_article(title)
        if found_url:
            source_url = found_url
            source_name = "منبع خبری"
    
    # Strategy 3: iranintl.com
    elif 'iranintl.com' in source_url:
        print(f"      📡 Trying Iran International...")
        article_text, article_image = fetch_from_iran_intl(source_url)
    
    # Strategy 4: Generic fetch
    else:
        print(f"      📡 Trying generic fetch...")
        try:
            resp = session.get(source_url, timeout=30, verify=False)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                paragraphs = []
                content_div = (soup.find('div', class_='entry-content') or soup.find('article') or soup.find('main'))
                if content_div:
                    for p in content_div.find_all('p'):
                        text = p.get_text().strip()
                        if len(text) > 30:
                            paragraphs.append(text)
                article_text = "\n\n".join(paragraphs[:15])
                og = soup.find('meta', property='og:image')
                article_image = og.get('content') if og else None
        except:
            pass
    
    if article_text and len(article_text) > 50:
        new_html = build_post_html(article_text, article_image, source_url, source_name)
        try:
            service.posts().patch(
                blogId=BLOG_ID, postId=post_id,
                body={"content": new_html}
            ).execute()
            restored += 1
            print(f"      ✅ Restored! ({len(article_text)} chars)")
            time.sleep(2)
        except Exception as e:
            print(f"      ❌ Update failed: {e}")
            failed += 1
    else:
        print(f"      ❌ Could not restore (no content found)")
        still_empty.append((post_id, title, source_url))
        failed += 1

print(f"\n{'='*70}")
print(f"✅ Restored: {restored}")
print(f"❌ Failed: {failed}")
if still_empty:
    print(f"\n📋 Still empty posts:")
    for pid, title, url in still_empty:
        print(f"   - {title[:60]}... | {url[:50]}")
print(f"{'='*70}")
