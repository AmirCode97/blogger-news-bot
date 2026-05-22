import sys
import os
import re
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from blogger_poster import BloggerPoster

def safe_print(text):
    try:
        print(text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))
    except:
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print(text)

poster = BloggerPoster()
safe_print(f"Connected to Blog ID: {poster.blog_id}")

page_token = None
all_posts = []

while True:
    try:
        params = {
            'blogId': poster.blog_id,
            'maxResults': 50,
        }
        if page_token:
            params['pageToken'] = page_token
        
        resp = poster.service.posts().list(**params).execute()
        posts = resp.get('items', [])
        if not posts:
            break
        
        all_posts.extend(posts)
        page_token = resp.get('nextPageToken')
        if not page_token or len(all_posts) >= 150:
            break
    except Exception as e:
        safe_print(f"Error fetching posts: {e}")
        break

safe_print(f"Fetched {len(all_posts)} posts.")

missing_count = 0
report_lines = []

for i, post in enumerate(all_posts):
    content = post.get("content", "")
    title = post.get("title", "")
    labels = post.get("labels", [])
    post_id = post.get("id")
    url = post.get("url")
    
    # Check for image
    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    has_img = False
    for src in img_matches:
        src_lower = src.lower()
        if any(skip in src_lower for skip in ['logo', 'icon', 'avatar', 'pixel', 'badge', '1x1', 'spacer']):
            continue
        has_img = True
        break
        
    # Check for sources
    domains = re.findall(r'(https?://[^\s/$.?#].[^\s"]*)', content)
    source_links = []
    for d in domains:
        if 'blogspot.com' not in d and 'blogger.com' not in d and 'wsrv.nl' not in d and 'jsdelivr' not in d:
            source_links.append(d)
            
    if not has_img or "background:#222" in content or "background: #222" in content:
        missing_count += 1
        line = f"\n{missing_count}. Missing Image: {title}"
        report_lines.append(line)
        line = f"   ID: {post_id}"
        report_lines.append(line)
        line = f"   URL: {url}"
        report_lines.append(line)
        line = f"   Labels: {labels}"
        report_lines.append(line)
        line = f"   Detected Source Links: {source_links}"
        report_lines.append(line)
        
        # We can extract the actual news source from the content or styling or links if possible
        # Check if the title matches or if there is any source info
        source_source = "Unknown"
        if "iranhr.net" in str(source_links):
            source_source = "سازمان حقوق بشر ایران (IranHR)"
        elif "humanrightsinir.org" in str(source_links):
            source_source = "حقوق بشر در ایران (HumanRightsInIR)"
        elif "iranhrs.org" in str(source_links):
            source_source = "کانون حقوق بشر ایران (IranHRS)"
        elif "iran-hrm.com" in str(source_links):
            source_source = "ناظران حقوق بشر ایران (Iran-HRM)"
        elif "iranintl.com" in str(source_links):
            source_source = "ایران اینترنشنال"
        
        line = f"   Inferred Source: {source_source}"
        report_lines.append(line)
        line = f"   HTML Snippet: {content[:300]}..."
        report_lines.append(line)

report_text = "\n".join(report_lines)
with open("missing_report.txt", "w", encoding="utf-8") as rf:
    rf.write(report_text)

safe_print(f"\nFinished checking. Found {missing_count} posts with missing images. Details saved to missing_report.txt")
