"""Update LokalKlick post: change main image to author portrait"""
import sys, pickle, os, time
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from googleapiclient.discovery import build
load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")
with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

# Find the post
all_posts = []
page_token = None
while True:
    result = service.posts().list(blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

for p in all_posts:
    if "کشته‌شدگان، زندانیان و زنان در ایران" in p.get("title",""):
        post_id = p["id"]
        content = p.get("content","")
        
        # Replace the old image with the author portrait
        import re
        new_content = re.sub(
            r'<div style="margin-bottom:25px;text-align:center;"><img src="[^"]*"',
            '<div style="margin-bottom:25px;text-align:center;"><img src="https://lokalklick.eu/wp-content/uploads/2026/01/OB_Hossein_Amjadi_Portrait.jpg"',
            content
        )
        
        service.posts().patch(
            blogId=BLOG_ID, postId=post_id,
            body={"content": new_content}
        ).execute()
        print("✅ Updated! Main image changed to author portrait.")
        break
