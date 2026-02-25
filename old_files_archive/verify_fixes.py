"""
Verify that fixes were applied correctly
"""
import os, sys, pickle, re
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

def main():
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('blogger', 'v3', credentials=creds)
    
    target_slugs = ["blog-post_787", "blog-post_1381", "blog-post_10", 
                     "blog-post_583", "blog-post_5336", "blog-post_381", "blog-post_09"]
    
    all_posts = []
    page_token = None
    while True:
        result = service.posts().list(blogId=BLOG_ID, maxResults=50, pageToken=page_token).execute()
        all_posts.extend(result.get('items', []))
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    
    print("=" * 70)
    print("🔍 VERIFICATION OF FIXES")
    print("=" * 70)
    
    for post in all_posts:
        url = post.get('url', '')
        if not any(s in url for s in target_slugs):
            continue
        
        content = post.get('content', '')
        title = post.get('title', '')[:50]
        
        # Check for dark colors
        has_dark_333 = 'color:#333' in content or 'color: #333' in content
        has_dark_444 = 'color:#444' in content or 'color: #444' in content
        has_white = 'color:#fff' in content
        has_source_box = 'منبع اصلی مقاله' in content
        has_correct_source = 'background:#ce0000' in content and 'مشاهده در' in content
        
        print(f"\n📄 {title}...")
        print(f"   🔗 {url}")
        print(f"   {'❌' if has_dark_333 else '✅'} No dark #333 text: {'FAIL' if has_dark_333 else 'OK'}")
        print(f"   {'❌' if has_dark_444 else '✅'} No dark #444 text: {'FAIL' if has_dark_444 else 'OK'}")
        print(f"   {'✅' if has_white else '❌'} Has white text: {'OK' if has_white else 'FAIL'}")
        print(f"   {'✅' if has_source_box else '❌'} Has source box: {'OK' if has_source_box else 'FAIL'}")
        print(f"   {'✅' if has_correct_source else '❌'} Correct source style: {'OK' if has_correct_source else 'FAIL'}")

if __name__ == "__main__":
    main()
