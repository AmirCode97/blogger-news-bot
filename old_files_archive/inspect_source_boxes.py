"""
Inspect source box HTML patterns in posts
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
    
    all_posts = []
    page_token = None
    while True:
        result = service.posts().list(blogId=BLOG_ID, maxResults=50, pageToken=page_token).execute()
        all_posts.extend(result.get('items', []))
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    
    # Look at posts that have two source boxes
    for post in all_posts[:10]:
        content = post.get('content', '')
        title = post.get('title', '')[:50]
        
        # Count source boxes
        count_source = content.lower().count('source')
        count_manba = content.count('منبع')
        
        if count_source > 0 or count_manba > 1:
            print(f"\n{'='*70}")
            print(f"POST: {title}")
            print(f"'Source' count: {count_source}, 'منبع' count: {count_manba}")
            
            # Find all divs with source-related content
            # Print last 800 chars where source boxes usually are
            print(f"\nLAST 1200 CHARS:")
            print(content[-1200:])
            print(f"{'='*70}")

if __name__ == "__main__":
    main()
