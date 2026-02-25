"""
Inspect posts to understand the HTML structure and fix issues
"""
import os
import sys
import pickle
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
    
    # Check specific problematic posts
    target_urls = [
        "blog-post_787",
        "blog-post_1381",
        "blog-post_10",
        "blog-post_583",
        "blog-post_5336",
        "blog-post_381",
        "blog-post_09",
    ]
    
    all_posts = []
    page_token = None
    while True:
        result = service.posts().list(blogId=BLOG_ID, maxResults=50, pageToken=page_token).execute()
        all_posts.extend(result.get('items', []))
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    
    print(f"Total posts: {len(all_posts)}\n")
    
    for post in all_posts:
        url = post.get('url', '')
        # Check if it's one of the target posts
        is_target = any(t in url for t in target_urls)
        
        if is_target:
            content = post.get('content', '')
            print("=" * 80)
            print(f"POST: {post.get('title', '')[:60]}")
            print(f"URL: {url}")
            print(f"HTML Length: {len(content)}")
            print(f"\nFirst 1500 chars of HTML:")
            print(content[:1500])
            print("\n... SOURCE BOX SECTION ...")
            # Find source box
            if 'منبع' in content:
                idx = content.find('منبع')
                print(content[max(0,idx-300):idx+300])
            print("=" * 80)
            print()

if __name__ == "__main__":
    main()
