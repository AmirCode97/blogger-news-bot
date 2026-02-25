"""Quick check specific post"""
import sys, pickle, os
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from googleapiclient.discovery import build
load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")
with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

# Search for the specific post
all_posts = []
page_token = None
while True:
    result = service.posts().list(blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

for p in all_posts:
    if "سپاه پاسداران و پایان صبر" in p.get("title",""):
        print(f"Title: {p['title']}")
        print(f"URL: {p.get('url','')}")
        print(f"\nFull HTML content:\n")
        print(p.get("content",""))
        break
