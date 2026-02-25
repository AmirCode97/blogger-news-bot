"""Fix duplicated text content inside Persian div of blog posts"""
import sys, pickle, os, re, time
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

recent = []
for p in all_posts:
    try:
        dt = dateparser.parse(p.get("published",""))
        if dt.year == 2026 and ((dt.month == 2 and dt.day >= 11) or dt.month > 2):
            recent.append(p)
    except:
        pass

print(f"Checking {len(recent)} posts...\n")

def is_text_duplicated(content):
    """Check if the plain text inside the Persian div is duplicated"""
    soup = BeautifulSoup(content, 'html.parser')
    text = re.sub(r'\s+', ' ', soup.get_text(separator=' ').strip())
    if len(text) < 100:
        return False
    chunk = text[:80].strip()
    return text.count(chunk) >= 2

def fix_duplicated_text(content):
    """The text inside the Persian section div is repeated.
    Find the Persian div content, detect duplication, and remove the repeat."""
    
    # Find the Persian Section div content
    # Pattern: text inside <div style="font-size:17px;line-height:2.2;...">TEXT</div>
    pattern = r'(<div style="font-size:17px;line-height:2\.2;color:#fff;text-align:justify;direction:rtl;font-family:\'Vazir\',sans-serif;">)\s*(.*?)\s*(</div>)'
    
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return None
    
    opening_tag = match.group(1)
    inner_text = match.group(2).strip()
    closing_tag = match.group(3)
    
    # Remove the <!--more--> tag temporarily for comparison
    clean_text = inner_text.replace("<a name='more'></a>", "MOREBREAK")
    
    # Get plain text for analysis
    plain = re.sub(r'<[^>]+>', '', clean_text).strip()
    plain = re.sub(r'\s+', ' ', plain)
    
    if len(plain) < 50:
        return None
    
    # Find the first 60 chars
    first_chunk = plain[:60]
    
    # Find second occurrence
    second_pos = plain.find(first_chunk, 10)
    if second_pos < 0:
        return None  # Not actually duplicated
    
    # The text up to the second occurrence is the unique content
    unique_plain = plain[:second_pos].strip()
    
    # Now find the corresponding position in the HTML
    # Extract text nodes from inner_text to find where the duplication starts in HTML
    lines = inner_text.split('\n')
    
    # Approach: Build the text char by char and find where duplication starts in HTML
    # Simpler: just find the second occurrence of the first line
    first_line_text = re.sub(r'<[^>]+>', '', lines[0]).strip()
    if not first_line_text or len(first_line_text) < 20:
        # Try next non-empty line
        for line in lines[1:]:
            first_line_text = re.sub(r'<[^>]+>', '', line).strip()
            if len(first_line_text) >= 20:
                break
    
    if not first_line_text or len(first_line_text) < 20:
        return None
    
    # Find second occurrence of first_line_text in inner_text (as plain text)
    # We need to search in the raw inner_text
    first_pos = inner_text.find(first_line_text)
    if first_pos < 0:
        return None
    
    second_pos_html = inner_text.find(first_line_text, first_pos + len(first_line_text))
    if second_pos_html < 0:
        return None
    
    # Keep only the text up to the second occurrence
    unique_inner = inner_text[:second_pos_html].strip()
    
    # Restore the MOREBREAK
    unique_inner = unique_inner.replace("MOREBREAK", "<a name='more'></a>")
    
    # Rebuild the content
    new_content = content[:match.start()] + opening_tag + '\n                    ' + unique_inner + '\n                ' + closing_tag + content[match.end():]
    
    return new_content

fixed_count = 0
failed_count = 0
skipped = 0

for p in recent:
    content = p.get("content", "")
    if not is_text_duplicated(content):
        skipped += 1
        continue
    
    fixed = fix_duplicated_text(content)
    if fixed and not is_text_duplicated(fixed):
        try:
            service.posts().patch(
                blogId=BLOG_ID, postId=p['id'],
                body={"content": fixed}
            ).execute()
            fixed_count += 1
            print(f"✅ [{fixed_count}] {p['title'][:55]}")
            if fixed_count % 10 == 0:
                time.sleep(2)  # Rate limit every 10
            else:
                time.sleep(0.5)
        except Exception as e:
            failed_count += 1
            print(f"❌ API: {p['title'][:40]} -> {e}")
    else:
        failed_count += 1
        print(f"⚠️ Can't fix: {p['title'][:55]} (ID: {p['id']})")

print(f"\n{'='*60}")
print(f"✅ Fixed: {fixed_count}")
print(f"⏭️ Skipped (not dup): {skipped}")
print(f"⚠️ Failed: {failed_count}")
print(f"{'='*60}")
