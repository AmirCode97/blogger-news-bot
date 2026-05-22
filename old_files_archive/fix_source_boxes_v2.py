import os
import sys
import re
import pickle
import time
from googleapiclient.discovery import build

# Force UTF-8 for output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(r'c:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot')

BLOG_ID = "1276802394255833723"

DARK_BOX = '''<!-- Premium Source Box -->
<div style="text-align: right; direction: rtl;">
    <div style="background:#1a1a1a; padding:12px 25px; border-radius:8px; border-right:3px solid #c0392b; font-weight:bold; color:#ddd; display:inline-block; margin:30px 0 10px 0; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);">
        <span style="color:#c0392b; margin-left:8px;">خبرگزاری:</span> iranpolnews
    </div>
</div>'''

def fix_html(html):
    original_html = html
    
    # Pattern finding the big white box or various source link patterns
    source_patterns = [
        # Pattern 1: Premium Source Box (white box)
        r'<!--\s*(?:Premium\s*)?Source\s*Box\s*-->\s*<div[^>]*>[\s\S]*?منبع[\s\S]*?</div>\s*(?:</div>)?',
        # Pattern 2: Old basic source paragraph
        r'<p[^>]*>[\s\S]*?منبع\s*(?:اصلی)?\s*(?:مقاله|خبر)\s*:[\s\S]*?</p>',
        # Pattern 3: Any div wrapping منبع اصلی مقاله
        r'<div[^>]*>[\s\S]*?منبع\s*(?:اصلی)?\s*(?:مقاله|خبر)[\s\S]*?</div>',
        # Special case: simple red link boxes
        r'<a[^>]*background:#ce0000[^>]*>[\s\S]*?مشاهده در[\s\S]*?</a>',
    ]
    
    # Remove existing dark boxes to avoid duplication
    html = re.sub(r'<!--\s*(?:Premium\s*)?Source\s*Box\s*-->\s*<div[^>]*>\s*<div[^>]*>\s*<span[^>]*>خبرگزاری:</span> iranpolnews\s*</div>\s*</div>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<div[^>]*background:#1a1a1a[^>]*>[\s\S]*?خبرگزاری:[\s\S]*?iranpolnews</div>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    for pattern in source_patterns:
        html = re.sub(pattern, '', html, flags=re.IGNORECASE | re.DOTALL)
        
    # Append the new dark box
    html = html.rstrip() + '\n' + DARK_BOX
    
    return html, html.strip() != original_html.strip()

def fix_posts():
    print("Fetching posts from Blogger API...")
    
    credentials_path = os.path.join(r'c:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot', 'token_auth_fixed.pickle')
    if not os.path.exists(credentials_path):
        print("Credentials file not found at " + credentials_path)
        return
        
    with open(credentials_path, 'rb') as t:
        creds = pickle.load(t)
    service = build('blogger', 'v3', credentials=creds)
    
    all_posts = []
    page_token = None
    try:
        while True:
            result = service.posts().list(blogId=BLOG_ID, maxResults=50, pageToken=page_token).execute()
            all_posts.extend(result.get('items', []))
            page_token = result.get('nextPageToken')
            if not page_token:
                break
            print(f"Loaded {len(all_posts)} posts...")
    except Exception as e:
        print(f"Error fetching posts: {e}")
        return
            
    print(f"Total posts found: {len(all_posts)}")
    print("Checking for posts that need the source box fixed...")
    
    updated = 0
    skipped = 0
    for idx, p in enumerate(all_posts, 1):
        old_content = p.get('content', '')
        
        # Check if already has EXACT dark box at the end
        if old_content.rstrip().endswith(DARK_BOX.strip()):
            skipped += 1
            if idx % 100 == 0:
                print(f"[{idx}/{len(all_posts)}] Reached {idx} posts...")
            continue
            
        new_content, changed = fix_html(old_content)
        
        if changed:
            try:
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=p['id'],
                    body={'content': new_content}
                ).execute()
                safe_title = p.get('title', 'No Title').encode('ascii', errors='replace').decode('ascii')
                print(f"[{idx}/{len(all_posts)}] [UPDATED] {safe_title[:30]}...")
                updated += 1
                time.sleep(0.5) # Modest speed, Blogger allows quite a bit
            except Exception as e:
                print(f"[{idx}/{len(all_posts)}] [ERROR] {e}")
                time.sleep(2)
        else:
            skipped += 1
            
    print(f"Done. Updated: {updated}, Already correct/Skipped: {skipped}")

if __name__ == '__main__':
    fix_posts()
