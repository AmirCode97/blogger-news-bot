from blogger_poster import BloggerPoster

poster = BloggerPoster()

# List all posts to check how many exist
response = poster.service.posts().list(blogId=poster.blog_id, maxResults=20).execute()
items = response.get('items', [])
print(f'Total posts found: {len(items)}')
for i, item in enumerate(items):
    title = item["title"][:60]
    pid = item["id"]
    print(f'{i+1}. {title}  (ID: {pid})')
