# Publish ALL remaining Iran Intl news
import sys
sys.path.insert(0, '.')

from news_fetcher import NewsFetcher
from blogger_poster import BloggerPoster
from config import NEWS_SOURCES

print("=== Publishing ALL Iran Intl News ===\n")

# Get Iran Intl source
iran_intl = None
for source in NEWS_SOURCES:
    if 'ایران اینترنشنال' in source['name']:
        iran_intl = source
        break

if not iran_intl:
    print("Iran Intl source not found!")
    sys.exit(1)

# Fetch news
fetcher = NewsFetcher()
items = fetcher.fetch_from_scrape(iran_intl)
print(f"\nFetched {len(items)} items from Iran Intl")

# Get existing blog posts
poster = BloggerPoster()
existing_posts = []
page_token = None
while True:
    result = poster.service.posts().list(blogId='1276802394255833723', maxResults=50, pageToken=page_token).execute()
    existing_posts.extend(result.get('items', []))
    page_token = result.get('nextPageToken')
    if not page_token:
        break

existing_titles = [p['title'][:40] for p in existing_posts]
print(f"Existing blog posts: {len(existing_posts)}")

# Find truly new items
new_items = []
for item in items:
    is_new = True
    for existing_title in existing_titles:
        if item['title'][:40] == existing_title:
            is_new = False
            break
    if is_new:
        new_items.append(item)

print(f"\nTruly new items: {len(new_items)}")

# Post ALL new items
for i, item in enumerate(new_items, 1):
    print(f"\n[{i}/{len(new_items)}] Posting: {item['title'][:60]}...")
    
    # Get full article
    full = fetcher.fetch_full_article(item['link'], 'ایران اینترنشنال')
    content = full.get('full_content', item['title'])
    image = full.get('main_image', '')
    
    # Create HTML
    image_html = ""
    if image:
        image_html = f'<div style="margin-bottom: 20px;"><img src="{image}" style="width: 100%; max-width: 700px; border-radius: 8px;"></div>'
    
    html_content = f'''
    {image_html}
    <p>{content}</p>
    <p style="color: #888; margin-top: 20px;">منبع: ایران اینترنشنال</p>
    '''
    
    try:
        post = poster.service.posts().insert(
            blogId='1276802394255833723',
            body={
                'title': item['title'],
                'content': html_content,
                'labels': ['بین‌الملل', 'ایران', 'اخبار']
            }
        ).execute()
        print(f"  ✅ Published: {post.get('url', 'N/A')}")
    except Exception as e:
        print(f"  ❌ Failed: {e}")

print(f"\n\n=== Done! Published {len(new_items)} Iran Intl articles ===")
