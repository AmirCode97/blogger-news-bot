# Check if Iran Intl news are being filtered out
import json

# Load blog posts via API
from blogger_poster import BloggerPoster

poster = BloggerPoster()
service = poster.service

# Get all posts
posts = []
page_token = None
while True:
    result = service.posts().list(blogId='1276802394255833723', maxResults=50, pageToken=page_token).execute()
    posts.extend(result.get('items', []))
    page_token = result.get('nextPageToken')
    if not page_token:
        break

print(f"Total posts in blog: {len(posts)}")

# Check for Iran Intl keywords in titles
iran_intl_keywords = ['رادان', 'بسیج', 'کمیسیون', 'مذاکرات', 'ترامپ', 'هسته‌ای', 'خامنه‌ای', 'سپاه']
iran_intl_posts = []

for post in posts:
    title = post.get('title', '')
    for kw in iran_intl_keywords:
        if kw in title:
            iran_intl_posts.append(title[:70])
            break

print(f"\nPosts with Iran Intl keywords: {len(iran_intl_posts)}")
for t in iran_intl_posts[:10]:
    print(f"  - {t}")

# Now check what news we would fetch
print("\n\n--- Checking fetcher ---")
from news_fetcher import NewsFetcher
from config import NEWS_SOURCES

fetcher = NewsFetcher()

# Find Iran Intl source
iran_intl = None
for source in NEWS_SOURCES:
    if 'ایران اینترنشنال' in source['name']:
        iran_intl = source
        break

if iran_intl:
    items = fetcher.fetch_from_scrape(iran_intl)
    print(f"\nIran Intl items fetched: {len(items)}")
    
    # Check overlap with blog
    iran_titles = [item['title'] for item in items]
    overlap = 0
    for title in iran_titles:
        for post in posts:
            if title[:30] in post.get('title', ''):
                overlap += 1
                print(f"  [OVERLAP] {title[:50]}")
                break
    
    print(f"\nOverlapping (already in blog): {overlap}")
    print(f"New (not in blog): {len(items) - overlap}")
