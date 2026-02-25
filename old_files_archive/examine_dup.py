"""Save one duplicated post's HTML to a file for examination"""
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

post = service.posts().get(blogId=BLOG_ID, postId="8894512649795724166").execute()
with open("sample_dup.html", "w", encoding="utf-8") as f:
    f.write(post['content'])
print(f"Saved {len(post['content'])} chars to sample_dup.html")
