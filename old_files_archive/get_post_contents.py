import sys
import os
import json
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from blogger_poster import BloggerPoster

poster = BloggerPoster()
search_ids = [
    "4566076101771367375",
    "7937031076052603044",
    "8656571386204910865",
    "42661393950526048",
    "950771976670731036"
]

report_lines = []

for pid in search_ids:
    try:
        post = poster.service.posts().get(blogId=poster.blog_id, postId=pid).execute()
        title = post.get("title", "")
        content = post.get("content", "")
        labels = post.get("labels", [])
        
        # Strip HTML tags
        soup_text = re.sub(r'<[^>]+>', ' ', content)
        soup_text = re.sub(r'\s+', ' ', soup_text).strip()
        
        report_lines.append(f"\n=====================================")
        report_lines.append(f"Title: {title}")
        report_lines.append(f"ID: {pid}")
        report_lines.append(f"Labels: {labels}")
        report_lines.append(f"Content: {soup_text}")
    except Exception as e:
        report_lines.append(f"Error fetching post {pid}: {e}")

report_text = "\n".join(report_lines)
with open("posts_contents_utf8.txt", "w", encoding="utf-8") as f:
    f.write(report_text)

print("Saved to posts_contents_utf8.txt successfully.")
