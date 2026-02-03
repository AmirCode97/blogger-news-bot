# Test smart filtering for Iran Intl
import sys
sys.path.insert(0, '.')

from news_fetcher import NewsFetcher

fetcher = NewsFetcher()

# Test the Radan article
url = "https://www.iranintl.com/202602036458"
print(f"Testing smart filter on: {url}\n")

result = fetcher.fetch_full_article(url, "ایران اینترنشنال")

print(f"\n\n=== RESULT ===")
print(f"Success: {result['success']}")
print(f"Main Image: {result['main_image'][:80] if result['main_image'] else 'None'}...")
print(f"Content Length: {len(result['full_content'])} chars")
print(f"\n--- FULL CONTENT ---")
print(result['full_content'][:2000])
print("\n...")
print(result['full_content'][-500:] if len(result['full_content']) > 2000 else "")
