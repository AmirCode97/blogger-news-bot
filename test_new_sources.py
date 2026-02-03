# تست استخراج اخبار از سایت‌های جدید حقوق بشری
import sys
sys.path.insert(0, '.')

from news_fetcher import NewsFetcher
import time

def test_fetch(source_name, url):
    print(f"\n=====================================")
    print(f"🧪 تست منبع: {source_name}")
    print(f"   URL: {url}")
    print(f"=====================================")
    
    fetcher = NewsFetcher()
    
    # تنظیمات موقت برای تست
    # برای IranHRM
    if 'iran-hrm' in url:
        selectors = {
            "articles": "article",
            "title": "h2 a, h3 a, h4 a",
            "link": "h2 a, h3 a, h4 a",
            "image": "img"
        }
    # برای IranHumanRights
    else:
        selectors = {
            "articles": "article, .post",
            "title": "h2 a, h3 a, .entry-title a",
            "link": "h2 a, h3 a, .entry-title a",
            "image": "img"  
        }

    # ۱. اسکرپ لیست
    print("1. Fetching list...")
    items = fetcher.fetch_from_source({
        'name': source_name,
        'url': url,
        'type': 'scrape',
        'selectors': selectors,
        'max_items': 3
    })
    
    print(f"   Found {len(items)} items")
    
    if not items:
        print("   ❌ No items found!")
        return

    # ۲. اسکرپ محتوای کامل اولین خبر
    first_item = items[0]
    print(f"\n2. Fetching full content for: {first_item['title'][:50]}...")
    print(f"   Link: {first_item['link']}")
    
    details = fetcher.fetch_full_article(first_item['link'], source_name)
    
    print(f"\n   ✅ Success: {details['success']}")
    
    content = details['full_content']
    print(f"   Content Length: {len(content)} chars")
    
    # نمایش ۳ پاراگراف اول
    paragraphs = content.split('\n')
    valid_ps = [p for p in paragraphs if '<p' in p]
    print(f"   Paragraphs: {len(valid_ps)}")
    
    for i, p in enumerate(valid_ps[:3]):
        # حذف تگ HTML برای نمایش
        text = p.replace('<p', '').replace('</p>', '').split('>')[1] if '>' in p else p
        print(f"   [P{i+1}]: {text[:100]}...")

# تست هر دو سایت
test_fetch("ناظران حقوق بشر ایران", "https://fa.iran-hrm.com/")
print("\n" + "-"*50 + "\n")
test_fetch("مرکز اسناد حقوق بشر ایران", "https://persian.iranhumanrights.org/")
