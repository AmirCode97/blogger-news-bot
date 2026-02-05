# بررسی بخش گزارش‌های ویژه ایران اینترنشنال
from bs4 import BeautifulSoup
import sys
sys.path.insert(0, '.')
from news_fetcher import NewsFetcher

def analyze_special_reports():
    urls_to_test = [
        "https://www.iranintl.com/investigatives",
        "https://www.iranintl.com/program/investigatives",
        "https://www.iranintl.com/comments"
    ]
    
    fetcher = NewsFetcher()
    
    for url in urls_to_test:
        print(f"\n🔍 بررسی آدرس: {url}")
        try:
             # استفاده از نقل قول برای URL های فارسی
            from urllib.parse import quote
            if 'گزارش' in url:
                 parts = url.split('tag/')
                 encoded_tag = quote(parts[1])
                 url = f"{parts[0]}tag/{encoded_tag}"
                 print(f"   (Encoded URL: {url})")

            response = fetcher._make_request(url, use_proxy=True)
            if not response:
                print("   ❌ خطا در اتصال.")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.select("a[href*='/202']")
            print(f"   📄 تعداد لینک پیدا شده: {len(links)}")
            
            if len(links) > 0:
                print("   ✅ این آدرس معتبر به نظر می‌رسد!")
                # نمایش نمونه
                for link in links[:3]:
                    print(f"      - {link.get_text().strip()} ({link.get('href')})")
        
        except Exception as e:
            print(f"   ❌ خطا: {e}")

if __name__ == "__main__":
    analyze_special_reports()
