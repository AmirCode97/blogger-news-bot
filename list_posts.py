import sys
from blogger_poster import BloggerPoster

sys.stdout.reconfigure(encoding='utf-8')

poster = BloggerPoster()

# List all posts to check how many exist
response = poster.service.posts().list(blogId=poster.blog_id, maxResults=100).execute()
items = response.get('items', [])
print(f'Total posts found: {len(items)}')
for i, item in enumerate(items):
    title = item["title"][:60]
    pid = item["id"]
    labels = item.get('labels', [])
    print(f'{i+1}. {title}  (ID: {pid})  Labels: {labels}')

