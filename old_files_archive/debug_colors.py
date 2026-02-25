"""Show exact color patterns in problematic posts"""
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

# Check the first problematic post
post = service.posts().get(blogId=BLOG_ID, postId="3108444567403366445").execute()
content = post.get("content", "")

# Find all color patterns
colors = re.findall(r'color\s*:\s*([^;"\']+)', content)
print("All color values found:")
for c in colors:
    print(f"  → color:{c.strip()}")

print(f"\n\nFirst 500 chars of content:")
print(content[:500])
