"""Add خانه label to Amjadi post"""
import os
import sys
import pickle
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

with open('token_auth_fixed.pickle', 'rb') as t:
    creds = pickle.load(t)
service = build('blogger', 'v3', credentials=creds)

posts = service.posts().list(blogId=BLOG_ID, maxResults=50).execute().get('items', [])
for post in posts:
    if 'حسین امجدی' in post.get('title', ''):
        print(f"Found: {post['title'][:50]}")
        service.posts().patch(
            blogId=BLOG_ID,
            postId=post['id'],
            body={'labels': ['خانه', 'گزارش ویژه', 'بین‌الملل', 'حسین امجدی', 'سپاه پاسداران']}
        ).execute()
        print("✅ Added to خانه section!")
        break
