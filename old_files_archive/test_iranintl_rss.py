"""Test Iran International RSS feed in detail"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
import feedparser

feed = feedparser.parse("https://www.iranintl.com/feed")
print(f"Total entries: {len(feed.entries)}\n")

# Show first 3 entries with all fields
for i, entry in enumerate(feed.entries[:5]):
    print(f"\n{'='*60}")
    print(f"[{i+1}] {entry.get('title','?')}")
    print(f"    Link: {entry.get('link','?')}")
    print(f"    Published: {entry.get('published','?')}")
    
    # Description/summary
    raw_desc = entry.get('summary', entry.get('description', ''))
    print(f"    Summary length: {len(raw_desc)}")
    print(f"    Summary preview: {raw_desc[:200]}")
    
    # Image sources
    media = entry.get('media_content', [])
    print(f"    media_content: {media}")
    thumb = entry.get('media_thumbnail', [])
    print(f"    media_thumbnail: {thumb}")
    enc = entry.get('enclosures', [])
    print(f"    enclosures: {enc}")
    
    # Check for image in summary
    if '<img' in raw_desc:
        import re
        imgs = re.findall(r'<img[^>]+src="([^"]+)"', raw_desc)
        print(f"    Images in summary: {imgs}")
    
    # All keys
    print(f"    All keys: {list(entry.keys())}")
