
import os
import pickle
import sys
from googleapiclient.discovery import build
from config import BLOG_ID

# Force UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def get_blogger_service():
    if not os.path.exists('token_auth_fixed.pickle'):
        return None
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    return build('blogger', 'v3', credentials=creds)

def clean_source_links():
    service = get_blogger_service()
    if not service: return

    print("Fetching last 15 posts to check for Source Links...")
    posts = service.posts().list(blogId=BLOG_ID, maxResults=15).execute().get('items', [])
    
    deleted_count = 0
    for post in posts:
        content = post.get('content', '')
        
        # Check if source box has NO link
        # Pattern: <a href=...>{source_name}</a>
        # If it has <span>{source_name}</span> inside source box, it's the bad version (V11 v1)
        
        if '<!-- Premium Source Box (Fixed to match Image 1) -->' in content:
            # This is the V11 v1 signature (bad source box)
             print(f"Deleting post with NO LINK source: {post['title']}")
             service.posts().delete(blogId=BLOG_ID, postId=post['id']).execute()
             deleted_count += 1
             
    print(f"Deleted {deleted_count} link-less posts.")

if __name__ == '__main__':
    clean_source_links()
