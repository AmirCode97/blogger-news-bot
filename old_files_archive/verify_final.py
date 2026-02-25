"""Final verification - check ALL posts"""
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

print(f"📊 Verifying ALL {len(all_posts)} posts\n")

issues = 0
for i, post in enumerate(all_posts, 1):
    title = post.get("title", "")[:60]
    content = post.get("content", "")
    
    problems = []
    
    # Check for old "Source:" box (not inside Premium box)
    if re.search(r'>\s*Source:\s*<', content):
        problems.append("❌ Old Source: box")
    
    # Check for dark text colors in main content (not in source box)
    # Extract text container colors only
    text_divs = re.findall(r'<div[^>]*style="[^"]*color:#(333|444|222|111|000)[^"]*"', content)
    if text_divs:
        problems.append(f"❌ Dark text color (#{text_divs[0]})")
    
    # Check for missing premium source box
    if 'منبع اصلی مقاله:' not in content:
        problems.append("⚠️ No premium source box")
    
    if problems:
        issues += 1
        print(f"  ❌ [{i}] {title}...")
        for p in problems:
            print(f"       {p}")
    else:
        print(f"  ✅ [{i}] {title}...")

print(f"\n{'='*60}")
if issues == 0:
    print(f"🎉 ALL {len(all_posts)} POSTS ARE PERFECT!")
else:
    print(f"🔴 {issues} posts still have issues")
print(f"{'='*60}")
