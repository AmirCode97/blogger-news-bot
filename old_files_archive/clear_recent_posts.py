
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

def clean_recent():
    service = get_blogger_service()
    if not service: return

    print("Fetching last 10 posts to clear mixed styles...")
    posts = service.posts().list(blogId=BLOG_ID, maxResults=10).execute().get('items', [])
    
    count = 0
    for post in posts:
        # Delete everything to ensure uniformity with the reverted theme
        print(f"Deleting recent post: {post['title']}")
        service.posts().delete(blogId=BLOG_ID, postId=post['id']).execute()
        count += 1
             
    print(f"Deleted {count} posts.")

if __name__ == '__main__':
    clean_recent()
