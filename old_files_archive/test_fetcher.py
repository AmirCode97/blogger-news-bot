"""Test the full news fetcher with updated Iran International config"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from news_fetcher import NewsFetcher

fetcher = NewsFetcher()

# Clear cache temporarily to see all news
original_ids = fetcher.seen_ids.copy()
original_titles = fetcher.seen_titles.copy()
fetcher.seen_ids = set()
fetcher.seen_titles = set()

news = fetcher.fetch_all_news(max_items=30)

# Restore cache
fetcher.seen_ids = original_ids
fetcher.seen_titles = original_titles

print(f"\n{'='*70}")
print(f"RESULTS: {len(news)} news items fetched")
print(f"{'='*70}\n")

iran_intl = [n for n in news if "اینترنشنال" in n.get("source","")]
others = [n for n in news if "اینترنشنال" not in n.get("source","")]

print(f"🟢 ایران اینترنشنال: {len(iran_intl)} items")
for n in iran_intl[:5]:
    has_img = "✅" if n.get("image_url") else "❌"
    has_desc = "✅" if len(n.get("description","")) > 20 else "❌"
    print(f"  {has_img}🖼️ {has_desc}📝 {n['title'][:60]}")
    if n.get("image_url"):
        print(f"          img: {n['image_url'][:80]}...")

print(f"\n🔵 Other sources: {len(others)} items")
for n in others[:5]:
    print(f"  [{n.get('source','?')[:20]}] {n['title'][:50]}")
