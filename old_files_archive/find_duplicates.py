"""Deep scan for text duplication inside posts"""
import sys, pickle, os, re
from dateutil import parser as dateparser
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")
with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

all_posts = []
page_token = None
while True:
    result = service.posts().list(blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

# Filter Feb 11+ posts
recent = []
for p in all_posts:
    try:
        dt = dateparser.parse(p.get("published",""))
        if dt.year == 2026 and ((dt.month == 2 and dt.day >= 11) or dt.month > 2):
            recent.append(p)
    except:
        pass

print(f"Checking {len(recent)} posts since Feb 11...\n")

duplicated = []
for p in recent:
    content = p.get("content", "")
    # Get plain text
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ').strip()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    if len(text) < 100:
        continue
    
    # Strategy: Find first 80 chars of the content text, then check if it repeats
    first_chunk = text[:80].strip()
    if not first_chunk:
        continue
    
    # Count how many times the first chunk appears
    occurrences = text.count(first_chunk)
    if occurrences >= 2:
        duplicated.append(p)
        print(f"❌ DUPLICATE: {p['title'][:60]}")
        print(f"   ID: {p['id']} | Text len: {len(text)}")
        print(f"   First 80 chars appear {occurrences} times")
        print(f"   Preview: {first_chunk[:50]}...")
        print()

print(f"\n{'='*60}")
print(f"TOTAL DUPLICATED: {len(duplicated)}")
print(f"{'='*60}")

# Save IDs for fixing
with open("dup_post_ids.txt", "w") as f:
    for p in duplicated:
        f.write(f"{p['id']}\n")
print(f"Saved IDs to dup_post_ids.txt")
