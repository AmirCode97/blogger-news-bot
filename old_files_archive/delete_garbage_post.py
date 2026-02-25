
import os
import sys
import pickle
from googleapiclient.discovery import build
import json

# Force UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

def get_blogger_service():
    if not os.path.exists('token_auth_fixed.pickle'):
        return None
    try:
        with open('token_auth_fixed.pickle', 'rb') as t:
            creds = pickle.load(t)
        return build('blogger', 'v3', credentials=creds)
    except: return None

def fix_garbage():
    service = get_blogger_service()
    if not service: return

    print("Scanning for garbage post 'نفرین قاسم'...")
    try:
        posts = service.posts().list(blogId=BLOG_ID, maxResults=20).execute().get('items', [])
        
        target_title_part = "نفرین قاسم"
        deleted = False
        
        for post in posts:
            if target_title_part in post['title']:
                print(f"Found garbage post: {post['title']}")
                service.posts().delete(blogId=BLOG_ID, postId=post['id']).execute()
                print("Deleted successfully.")
                deleted = True
                
        # Also clear cache to refetch
        if os.path.exists("news_cache.json"):
            print("Clearing cache to allow refetch...")
            os.remove("news_cache.json")
            print("Cache cleared.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_garbage()
