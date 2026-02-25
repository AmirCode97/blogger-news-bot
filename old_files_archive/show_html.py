"""
Show the HTML of the LATEST problematic post to understand the exact issue
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os
import pickle
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

# Get the FIRST problematic post (latest)
post = service.posts().get(blogId=BLOG_ID, postId="3108444567403366445").execute()
content = post.get("content", "")

print(f"Title: {post.get('title', '')}")
print(f"Length: {len(content)} chars")
print(f"\n{'='*70}")
print("FULL HTML CONTENT:")
print("="*70)
print(content[:3000])
print("\n...\n")
print("="*70)
print("LAST 1500 chars:")
print("="*70)
print(content[-1500:])
