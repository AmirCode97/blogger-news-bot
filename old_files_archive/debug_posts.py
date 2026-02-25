"""Inspect recent posts to see their content"""
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

posts = service.posts().list(blogId=BLOG_ID, maxResults=10).execute().get('items', [])

print("=" * 80)
print("RECENT POSTS ANALYSIS")
print("=" * 80)

for i, post in enumerate(posts[:5]):
    title = post.get('title', 'No Title')
    content = post.get('content', '')
    labels = post.get('labels', [])
    url = post.get('url', '')
    
    # Count characters and check for actual text
    content_length = len(content)
    
    # Extract plain text (remove HTML)
    import re
    text_only = re.sub(r'<[^>]+>', '', content)
    text_length = len(text_only.strip())
    
    print(f"\n{'='*60}")
    print(f"POST {i+1}: {title[:60]}...")
    print(f"URL: {url}")
    print(f"Labels: {labels}")
    print(f"HTML Length: {content_length} chars")
    print(f"Text Length: {text_length} chars")
    print(f"First 300 chars of text:")
    print(text_only[:300] if text_only else "[EMPTY]")
    print(f"{'='*60}")
