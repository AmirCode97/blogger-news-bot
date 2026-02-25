"""
DEEP INSPECTION: Check all posts for missing content/images
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

print(f"📊 Deep inspection of ALL {len(all_posts)} posts\n")

empty_posts = []
short_posts = []
no_image_posts = []

for i, post in enumerate(all_posts, 1):
    title = post.get("title", "")[:60]
    content = post.get("content", "")
    post_id = post.get("id")
    url = post.get("url", "")
    
    # Strip HTML tags to get pure text length
    text_only = re.sub(r'<[^>]+>', '', content).strip()
    text_len = len(text_only)
    
    # Check for images
    has_image = bool(re.search(r'<img\s', content))
    
    # Check for actual Persian content (not just source box text)
    source_box_text = re.sub(r'<div[^>]*منبع.*?</div>', '', content, flags=re.DOTALL)
    source_box_text = re.sub(r'<style>.*?</style>', '', source_box_text, flags=re.DOTALL)
    real_text = re.sub(r'<[^>]+>', '', source_box_text).strip()
    real_text_len = len(real_text)
    
    issues = []
    if real_text_len < 100:
        issues.append(f"❌ EMPTY/VERY SHORT ({real_text_len} chars)")
        empty_posts.append((post_id, title, url, real_text_len))
    elif real_text_len < 300:
        issues.append(f"⚠️ Short content ({real_text_len} chars)")
        short_posts.append((post_id, title, url, real_text_len))
    
    if not has_image:
        issues.append("❌ No image")
        no_image_posts.append((post_id, title, url))
    
    if issues:
        print(f"  🔴 [{i}] {title}...")
        print(f"       URL: {url}")
        print(f"       Content length: {text_len} | Real text: {real_text_len}")
        for issue in issues:
            print(f"       {issue}")
        print()
    else:
        print(f"  ✅ [{i}] {title}... ({real_text_len} chars, has image)")

print(f"\n{'='*70}")
print(f"📊 SUMMARY:")
print(f"   Total posts: {len(all_posts)}")
print(f"   🔴 Empty/very short (< 100 chars): {len(empty_posts)}")
print(f"   ⚠️ Short (< 300 chars): {len(short_posts)}")
print(f"   ❌ No image: {len(no_image_posts)}")
print(f"{'='*70}")

# Show the specific post user mentioned
print(f"\n\n🔍 DETAILED VIEW of problematic posts:")
for pid, title, url, tlen in empty_posts:
    post = service.posts().get(blogId=BLOG_ID, postId=pid).execute()
    content = post.get("content", "")
    print(f"\n--- {title} ---")
    print(f"URL: {url}")
    print(f"HTML ({len(content)} chars):")
    print(content[:1000])
    print("...")
