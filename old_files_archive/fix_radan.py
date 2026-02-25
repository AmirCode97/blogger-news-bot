# Delete the old Radan posts and create a new clean one
import sys
sys.path.insert(0, '.')

from news_fetcher import NewsFetcher
from blogger_poster import BloggerPoster

print("=== Fixing Radan Article ===\n")

# Initialize
poster = BloggerPoster()
fetcher = NewsFetcher()

# Find and delete old Radan posts
print("1. Finding old Radan posts...")
posts = []
page_token = None
while True:
    result = poster.service.posts().list(blogId='1276802394255833723', maxResults=50, pageToken=page_token).execute()
    posts.extend(result.get('items', []))
    page_token = result.get('nextPageToken')
    if not page_token:
        break

radan_posts = [p for p in posts if 'رادان' in p.get('title', '')]
print(f"   Found {len(radan_posts)} Radan posts")

for post in radan_posts:
    print(f"   Deleting: {post['title'][:50]}... (ID: {post['id']})")
    poster.service.posts().delete(blogId='1276802394255833723', postId=post['id']).execute()

# Create new clean post
print("\n2. Creating new clean Radan post...")
url = "https://www.iranintl.com/202602036458"
result = fetcher.fetch_full_article(url, "ایران اینترنشنال")

if result['success']:
    # Create HTML
    image_html = ""
    if result['main_image']:
        image_html = f'<div style="margin-bottom: 20px;"><img src="{result["main_image"]}" style="width: 100%; max-width: 700px; border-radius: 8px;"></div>'
    
    html_content = f'''
    {image_html}
    {result['full_content']}
    <p style="color: #888; margin-top: 20px;">منبع: ایران اینترنشنال</p>
    '''
    
    post = poster.service.posts().insert(
        blogId='1276802394255833723',
        body={
            'title': 'رادان، فرمانده کل انتظامی: آمریکا و اسرائیل خطا کنند، پشیمان خواهند شد',
            'content': html_content,
            'labels': ['بین‌الملل', 'ایران', 'اخبار']
        }
    ).execute()
    print(f"   ✅ Published: {post.get('url')}")
else:
    print("   ❌ Failed to fetch article")
