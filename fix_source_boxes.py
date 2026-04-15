import os
import sys
import re
import pickle
import time
from googleapiclient.discovery import build

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

    # Pattern finding the big white box
    source_patterns = [
        # Pattern 1: Premium Source Box (white box)
        r'<!--\s*(?:Premium\s*)?Source\s*Box\s*-->\s*<div[^>]*>[\s\S]*?منبع[\s\S]*?</div>\s*(?:</div>)?',
        # Pattern 2: Old basic source paragraph
        r'<p[^>]*>[\s\S]*?منبع\s*(?:اصلی)?\s*(?:مقاله|خبر)\s*:[\s\S]*?</p>',
        # Pattern 3: Any div wrapping منبع اصلی مقاله
        r'<div[^>]*>[\s\S]*?منبع\s*(?:اصلی)?\s*(?:مقاله|خبر)[\s\S]*?</div>',
        # Pattern 4: The dark box itself if it has the old formatting we want to normalize completely
    ]
    
    for pattern in source_patterns:
        html = re.sub(pattern, '', html, flags=re.IGNORECASE | re.DOTALL)
        
    # Remove any existing dark box we might have added so we don't duplicate
    html = re.sub(r'<!--\s*(?:Premium\s*)?Source\s*Box\s*-->\s*<div[^>]*>\s*<div[^>]*>\s*<span[^>]*>خبرگزاری:</span> iranpolnews\s*</div>\s*</div>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<div[^>]*background:#1a1a1a[^>]*>[\s\S]*?خبرگزاری:[\s\S]*?iranpolnews</div>', '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Append the new dark box
    html = html.rstrip() + '\n' + DARK_BOX
    
    return html, html != original_html

def fix_posts():
    print("Fetching posts from Blogger...")
    
    credentials_path = os.path.join(r'c:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot', 'token_auth_fixed.pickle')
    if not os.path.exists(credentials_path):
        print("Credentials file not found.")
        return
        
    with open(credentials_path, 'rb') as t:
        creds = pickle.load(t)
    service = build('blogger', 'v3', credentials=creds)
    
    all_posts = []
    page_token = None
    while True:
        result = service.posts().list(blogId=BLOG_ID, maxResults=50, pageToken=page_token).execute()
        all_posts.extend(result.get('items', []))
        page_token = result.get('nextPageToken')
        if not page_token:
            break
            
    print(f"Total posts found: {len(all_posts)}")
    print("Checking for posts that need the source box fixed...")
    
    updated = 0
    for idx, p in enumerate(all_posts, 1):
        # We process ALL posts to ensure they all get the updated dark box.
        old_content = p.get('content', '')
        new_content, changed = fix_html(old_content)
        
        # We want to replace it if it doesn't match perfectly. But our fix_html removes all old and appends new.
        # Actually `changed` will always be True because we remove and append.
        # Let's filter out ones that ALREADY strictly end with the dark_box HTML cleanly.
        is_already_fixed = old_content.rstrip().endswith(DARK_BOX.strip())
        
        if not is_already_fixed:
            try:
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=p['id'],
                    body={'content': new_content}
                ).execute()
                safe_title = p.get('title', '')[:40].encode('ascii', errors='replace').decode('ascii')
                print(f"[{idx}/{len(all_posts)}] [OK] Fixed: {safe_title}")
                updated += 1
                time.sleep(1.5) # Avoid rate limits
            except Exception as e:
                print(f"[{idx}/{len(all_posts)}] [ERROR] Error: {e}")
        else:
            safe_title = p.get('title', '')[:40].encode('ascii', errors='replace').decode('ascii')
            print(f"[{idx}/{len(all_posts)}] [SKIP] Skipped (already fine): {safe_title}")
            
    print(f"Done. Updated {updated} posts.")

if __name__ == '__main__':
    fix_posts()
