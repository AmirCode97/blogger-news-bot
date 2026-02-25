
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

def inspect_latest_post():
    service = get_blogger_service()
    if not service: return

    print("Fetching latest post...")
    posts = service.posts().list(blogId=BLOG_ID, maxResults=1).execute().get('items', [])
    
    if posts:
        post = posts[0]
        print(f"TITLE: {post['title']}")
        print("-" * 20)
        print("CONTENT DUMP:")
        print(post['content'])
        print("-" * 20)
    else:
        print("No posts found.")

if __name__ == '__main__':
    inspect_latest_post()
