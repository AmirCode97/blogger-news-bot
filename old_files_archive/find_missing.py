import json
import re

with open("posts_list.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

print(f"Loaded {len(posts)} posts.")

for i, post in enumerate(posts):
    content = post.get("content", "")
    title = post.get("title", "")
    labels = post.get("labels", [])
    
    # Check if image is missing
    # In BloggerNewsBot, missing image means we don't have an img tag, or we have something else.
    # Let's see what the image tag looks like or if there's no img tag at all.
    has_img = "<img" in content
    
    # Find source link if any
    links = re.findall(r'href=["\']([^"\']+)["\']', content)
    source_link = None
    for link in links:
        if 'blogspot.com' not in link and 'blogger.com' not in link:
            source_link = link
            break
            
    if not has_img:
        print(f"\nMissing image: {title}")
        print(f"Labels: {labels}")
        print(f"Source Link: {source_link}")
        print(f"Snippet: {content[:200]}")
    elif "background:#222" in content or "background: #222" in content:
        print(f"\nMissing image (background #222 found): {title}")
        print(f"Labels: {labels}")
        print(f"Source Link: {source_link}")
        print(f"Snippet: {content[:200]}")
