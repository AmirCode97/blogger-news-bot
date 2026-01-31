
import sys
from news_fetcher import NewsFetcher
from config import NEWS_SOURCES

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

def check_images():
    print("Checking image extraction...")
    fetcher = NewsFetcher()
    
    # Check Radio Farda and IranHRS specifically
    target_sources = [s for s in NEWS_SOURCES if s['name'] in ["کانون حقوق بشر ایران", "رادیو فردا"]]
    
    for source in target_sources:
        print(f"\n--- Source: {source['name']} ---")
        try:
            items = fetcher.fetch_from_scrape(source)
            print(f"Fetched {len(items)} items")
            
            with_images = [item for item in items if item.get('image_url')]
            print(f"Items with images: {len(with_images)}")
            
            if with_images:
                print(f"Sample Image URL: {with_images[0]['image_url']}")
            else:
                print("❌ No images found! Checking raw HTML/Selectors might be needed.")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_images()
