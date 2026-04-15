import os
import sys
import re
import pickle
import time
from googleapiclient.discovery import build

sys.path.append(r'c:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot')

BLOG_ID = "1276802394255833723"

def clean_html_content(html):
    original_html = html
    
    # Patterns to remove (audio player, share, timestamps, etc.)
    junk_patterns = [
        # Audio player text
        r'پخش\s*نسخه\s*شنیداری',
        r'اشتراک[‌\u200c]?گذاری',
        r'[۰-۹\d]+\s*دقیقه\s*پیش',
        r'[۰-۹\d]+\s*ساعت\s*پیش',
        r'[۰-۹\d]+\s*روز\s*پیش',
        r'لحظاتی\s*پیش',
        r'►\s*پخش',
        r'▶\s*پخش',
        r'نسخه\s*شنیداری',
        r'بازپخش',
        r'ذخیره\s*کردن',
        r'نشان‌گذاری',
        r'کپی\s*لینک',
        r'رونوشت\s*لینک',
    ]
    
    cleaned = html
    for pattern in junk_patterns:
        cleaned = re.sub(pattern, '', cleaned)
    
    return cleaned, cleaned != original_html

def fix_posts():
    print("Fetching posts from Blogger to fix Iran International audio text issue...")
    
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
    print("Checking for posts that contain unwanted audio player text...")
    
    updated = 0
    for idx, p in enumerate(all_posts, 1):
        old_content = p.get('content', '')
        new_content, changed = clean_html_content(old_content)
        
        safe_title = p.get('title', '')[:40].encode('ascii', errors='replace').decode('ascii')
        
        if changed:
            try:
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=p['id'],
                    body={'content': new_content}
                ).execute()
                print(f"[{idx}/{len(all_posts)}] [Fixed] Removed UI text from: {safe_title}")
                updated += 1
                time.sleep(1.5) # Avoid rate limits
            except Exception as e:
                print(f"[{idx}/{len(all_posts)}] [ERROR] Could not update {safe_title}: {e}")
        else:
            print(f"[{idx}/{len(all_posts)}] [Skip] No changes needed for: {safe_title}")
            
    print(f"\nDone. Successfully cleaned {updated} posts.")

if __name__ == '__main__':
    fix_posts()
