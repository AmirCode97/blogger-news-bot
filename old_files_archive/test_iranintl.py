# تست اختصاصی ایران اینترنشنال
import sys
sys.path.insert(0, '.')

from news_fetcher import NewsFetcher
from config import NEWS_SOURCES
import json

def test_iranintl():
    print("=" * 60)
    print("🇮🇷 تست دریافت خبر از ایران اینترنشنال")
    print("=" * 60)
    
    # پیدا کردن کانفیگ ایران اینترنشنال
    source_config = next((s for s in NEWS_SOURCES if 'iranintl' in s['url']), None)
    if not source_config:
        print("❌ تنظیمات ایران اینترنشنال پیدا نشد!")
        return

    print(f"URL: {source_config['url']}")
    print(f"Selector: {source_config['selectors']['articles']}")
    
    fetcher = NewsFetcher()
    
    # 1. دریافت لیست اخبار
    print("\n1. دریافت لیست اخبار (List Fetching)...")
    try:
        # اجبار به استفاده از اسکرپ
        source_config['type'] = 'scrape' 
        news_items = fetcher.fetch_from_source(source_config)
    except Exception as e:
        print(f"❌ خطا در دریافت لیست: {e}")
        return

    print(f"   تعداد خبر پیدا شده: {len(news_items)}")
    
    if not news_items:
        print("❌ هیچ خبری پیدا نشد! احتمالاً مشکل سلکتور یا پروکسی.")
        return

    # 2. تست محتوای اولین خبر
    item = news_items[0]
    print(f"\n2. تست دریافت محتوای خبر (Content Fetching)...")
    print(f"   عنوان: {item['title']}")
    print(f"   لینک: {item['link']}")
    
    details = fetcher.fetch_full_article(item['link'], 'ایران اینترنشنال')
    
    if details['success']:
        print("\n✅ دریافت موفقیت‌آمیز بود!")
        print(f"   تعداد کاراکتر متن: {len(details['full_content'])}")
        print(f"   عکس دارد؟ {'بله' if details['image_url'] else 'خیر'}")
        
        # نمایش بخشی از متن برای اطمینان
        print("\n   [بخشی از متن]:")
        content_preview = details['full_content'].replace('\n', ' ')[:200]
        print(f"   {content_preview}...")
    else:
        print("\n❌ خطا در دریافت محتوا!")

if __name__ == "__main__":
    test_iranintl()
