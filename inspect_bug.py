import sys
from blogger_poster import BloggerPoster

sys.stdout.reconfigure(encoding='utf-8')
poster = BloggerPoster()

# Get recent posts
response = poster.service.posts().list(blogId=poster.blog_id, maxResults=5).execute()
items = response.get('items', [])

if items:
    with open("buggy_post.html", "w", encoding="utf-8") as f:
        f.write(items[0]['content'])
    print("Saved to buggy_post.html")
