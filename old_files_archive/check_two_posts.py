"""
Fix 2 posts: EU Today + LokalKlick
1. Translate to Persian
2. Add author bio with photo at end
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os, pickle, re
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

# Get ALL posts
all_posts = []
page_token = None
while True:
    result = service.posts().list(blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

for p in all_posts:
    title = p.get("title","")
    if "سپاه پاسداران و پایان صبر" in title:
        print(f"\n{'='*60}")
        print(f"POST 1 (EU Today): {title}")
        print(f"ID: {p['id']}")
        print(f"URL: {p.get('url','')}")
        content = p.get("content","")
        # Get text only
        text = re.sub(r'<[^>]+>', '', content).strip()
        print(f"Content length: {len(content)}")
        print(f"Text preview: {text[:500]}...")
        
    if "کشته‌شدگان، زندانیان و زنان در ایران" in title:
        print(f"\n{'='*60}")
        print(f"POST 2 (LokalKlick): {title}")
        print(f"ID: {p['id']}")
        print(f"URL: {p.get('url','')}")
        content = p.get("content","")
        text = re.sub(r'<[^>]+>', '', content).strip()
        print(f"Content length: {len(content)}")
        print(f"Text preview: {text[:500]}...")
