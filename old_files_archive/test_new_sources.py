"""
Test fetching from the 2 new RSS sources
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import feedparser

print("=" * 70)
print("🔍 TESTING NEW RSS SOURCES")
print("=" * 70)

# Test 1: iranhr.net
print("\n📰 Source 1: سازمان حقوق بشر ایران (iranhr.net)")
print("-" * 50)
feed1 = feedparser.parse("https://iranhr.net/fa/rss/")
print(f"Feed Title: {feed1.feed.get('title', 'N/A')}")
print(f"Total entries: {len(feed1.entries)}")
for i, entry in enumerate(feed1.entries[:5], 1):
    title = entry.get('title', 'No title')
    link = entry.get('link', '')
    published = entry.get('published', 'N/A')
    summary = entry.get('summary', '')[:100]
    print(f"\n  {i}. {title}")
    print(f"     🔗 {link}")
    print(f"     📅 {published}")
    print(f"     📝 {summary}...")

# Test 2: humanrightsinir.org
print(f"\n\n{'='*70}")
print("📰 Source 2: حقوق بشر در ایران (humanrightsinir.org)")
print("-" * 50)
feed2 = feedparser.parse("https://humanrightsinir.org/feed/")
print(f"Feed Title: {feed2.feed.get('title', 'N/A')}")
print(f"Total entries: {len(feed2.entries)}")
for i, entry in enumerate(feed2.entries[:5], 1):
    title = entry.get('title', 'No title')
    link = entry.get('link', '')
    published = entry.get('published', 'N/A')
    summary = entry.get('summary', '')[:100]
    print(f"\n  {i}. {title}")
    print(f"     🔗 {link}")
    print(f"     📅 {published}")
    print(f"     📝 {summary}...")

print(f"\n{'='*70}")
print("✅ Both sources working!" if feed1.entries and feed2.entries else "❌ Some sources failed!")
