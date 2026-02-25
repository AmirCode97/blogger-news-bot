"""
Inspect the LATEST posts to find what's wrong with formatting
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os
import pickle
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

# Auth
with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

# Get latest 10 posts
posts = service.posts().list(blogId=BLOG_ID, maxResults=10, fetchBodies=True).execute()
items = posts.get("items", [])

print(f"📊 Checking latest {len(items)} posts\n")

for i, post in enumerate(items, 1):
    title = post.get("title", "")[:60]
    content = post.get("content", "")
    post_id = post.get("id", "")
    
    # Check issues
    has_old_source = bool(re.search(r'Source:', content))
    has_new_source = 'منبع اصلی مقاله:' in content
    has_dark_text = bool(re.search(r'color\s*:\s*#(333|444|555|222|111|000)', content))
    has_white_text = 'color:#fff' in content or 'color: #fff' in content
    
    issues = []
    if has_old_source:
        issues.append("❌ OLD Source: box")
    if not has_new_source:
        issues.append("❌ Missing منبع اصلی")
    if has_dark_text:
        issues.append("❌ Dark text colors")
    if not has_white_text:
        issues.append("⚠️ No white text")
    
    status = "✅ OK" if not issues else " | ".join(issues)
    print(f"  [{i}] {title}...")
    print(f"       ID: {post_id}")
    print(f"       Status: {status}")
    
    # Show source box snippet
    if has_old_source:
        match = re.search(r'(Source:.*?</div>)', content, re.DOTALL)
        if match:
            snippet = match.group(1)[:200]
            print(f"       OLD BOX: {snippet}")
    
    print()

# Summary
problem_count = sum(1 for post in items if re.search(r'Source:', post.get("content", "")) or 'منبع اصلی مقاله:' not in post.get("content", ""))
print(f"\n{'='*60}")
print(f"🔴 Posts with issues: {problem_count}/{len(items)}")
print(f"{'='*60}")
