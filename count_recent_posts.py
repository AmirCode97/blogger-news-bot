import sys
from blogger_poster import BloggerPoster

sys.stdout.reconfigure(encoding='utf-8')

poster = BloggerPoster()

response = poster.service.posts().list(
    blogId=poster.blog_id,
    maxResults=100
).execute()

items = response.get('items', [])
print(f"Total posts in first page: {len(items)}")
if items:
    print(f"First post: {items[0]['title']} | {items[0]['published']}")
    print(f"Last post of page 1: {items[-1]['title']} | {items[-1]['published']}")
