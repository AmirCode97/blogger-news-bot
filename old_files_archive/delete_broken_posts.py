
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

def delete_broken_posts():
    service = get_blogger_service()
    if not service: return

    print("Fetching last 15 posts to check for damage...")
    posts = service.posts().list(blogId=BLOG_ID, maxResults=15).execute().get('items', [])
    
    deleted_count = 0
    for post in posts:
        content = post.get('content', '')
        # Check if content is suspiciously short or missing image tags
        # The broken posts seemed to have <style>... and then just the source box, so very short < 300 chars maybe?
        # Or missing the main content div.
        
        # A good post should have the description div.
        if 'color:inherit' in content and len(content) < 500: # Heuristic for broken post
             print(f"Deleting BROKEN post: {post['title']}")
             service.posts().delete(blogId=BLOG_ID, postId=post['id']).execute()
             deleted_count += 1
        elif '<div style="font-size' not in content and '<img' not in content:
             print(f"Deleting BROKEN post (no content): {post['title']}")
             service.posts().delete(blogId=BLOG_ID, postId=post['id']).execute()
             deleted_count += 1
             
    print(f"Deleted {deleted_count} broken posts.")

if __name__ == '__main__':
    delete_broken_posts()
