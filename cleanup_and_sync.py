# اسکریپت همگام‌سازی، حذف تکراری‌ها و حذف اخبار قدیمی
import sys
sys.path.insert(0, '.')

from blogger_poster import BloggerPoster
from news_fetcher import NewsFetcher
from datetime import datetime, timedelta
import json
import os
import hashlib
from difflib import SequenceMatcher

BLOG_ID = '1276802394255833723'
CACHE_FILE = "news_cache.json"

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def generate_news_id(title, link):
    """Generate unique ID for news item (same logic as NewsFetcher)"""
    unique_string = f"{title}_{link}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def main():
    print("=" * 60)
    print("🧹 پاکسازی وبلاگ و همگام‌سازی اخبار دیده شده")
    print("=" * 60)

    poster = BloggerPoster()
    fetcher = NewsFetcher()
    
    # 1. دریافت همه پست‌ها
    all_posts = []
    page_token = None
    print("📥 دریافت لیست پست‌های وبلاگ...")
    while True:
        try:
            result = poster.service.posts().list(
                blogId=BLOG_ID, 
                maxResults=50, 
                pageToken=page_token,
                fetchBodies=False  # فقط عنوان و تاریخ کافی است (سریعتر)
            ).execute()
            all_posts.extend(result.get('items', []))
            page_token = result.get('nextPageToken')
            if not page_token:
                break
        except Exception as e:
            print(f"❌ خطا در دریافت پست‌ها: {e}")
            break
            
    print(f"   کل پست‌های موجود: {len(all_posts)}")
    
    # 2. شناسایی تکراری‌ها و قدیمی‌ها
    seen_titles = []
    posts_to_delete = []
    seen_ids_to_add = set()
    
    # تاریخ امروز
    now = datetime.now()
    
    # برای حفظ جدیدترین نسخه، لیست را برعکس می‌کنیم یا مرتب می‌کنیم؟
    # پست‌ها معمولاً به ترتیب جدید به قدیم می‌آیند.
    # پس اولین باری که می‌بینیم جدیدترین است. برای تکراری‌ها، بعدی‌ها را حذف می‌کنیم.
    
    keep_count = 0
    
    for post in all_posts:
        title = post['title']
        post_id = post['id']
        url = post.get('url', '') # لینک پست در بلاگر (نه لینک اصلی خبر)
        
        # تاریخ انتشار پست
        published_str = post['published'] # 2026-02-03T...
        try:
            published_dt = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            # چون timezone ها متفاوت است، simple comparison
            published_dt = published_dt.replace(tzinfo=None)
        except:
            published_dt = now
            
        is_duplicate = False
        is_old = False
        
        # الف) چک کردن تکراری بودن عنوان (با شباهت بالا)
        for seen_t in seen_titles:
            if similarity(title, seen_t) > 0.9: # 90% شباهت
                is_duplicate = True
                break
        
        # ب) چک کردن قدیمی بودن (مثلاً قدیمی‌تر از ۷ روز؟)
        # کاربر گفت "خبرهای قدیمی را پاک کن"
        # بیایید فرض کنیم اخبار قدیمی‌تر از ۵ روز را نمی‌خواهد.
        if (now - published_dt).days > 5:
            is_old = True
            
        if is_duplicate:
            print(f"   🗑️ تکراری: {title[:50]}...")
            posts_to_delete.append(post)
        elif is_old:
            print(f"   🕰️ قدیمی ({published_dt.date()}): {title[:50]}...")
            posts_to_delete.append(post)
        else:
            # پست نگه داشته می‌شود -> به seen_titles اضافه کن
            seen_titles.append(title)
            keep_count += 1
            
            # تولید ID برای cache (که مبادا دوباره فچ شود)
            # چون لینک اصلی خبر را نداریم، یک هش از تایتل می‌سازیم که NewsFetcher هم چک کند
            # اما NewsFetcher از (Title + Link) استفاده می‌کند.
            # ما فقط Title را داریم. 
            # پس باید NewsFetcher را طوری تغییر دهیم که اگر Title تکراری بود هم نگیرد.
            pass

    print(f"\n📊 وضعیت:")
    print(f"   ✅ سالم و جدید: {keep_count}")
    print(f"   ❌ برای حذف: {len(posts_to_delete)}")
    
    # 3. حذف پست‌ها
    if posts_to_delete:
        print("\n🗑️ شروع حذف...")
        for post in posts_to_delete:
            try:
                poster.service.posts().delete(blogId=BLOG_ID, postId=post['id']).execute()
                print(f"   Deleted: {post['title'][:30]}...")
            except Exception as e:
                print(f"   Failed to delete {post['id']}: {e}")
    else:
        print("\n✅ هیچ پستی برای حذف نیست.")

    # 4. آپدیت کردن news_cache.json
    # برای جلوگیری از ارسال مجدد موارد باقی‌مانده (حتی اگر لینک اصلی را نداریم)
    # ترفند: ما نمیتوانیم seen_ids دقیق بسازیم چون لینک اصلی خبر دست ما نیست.
    # اما می‌توانیم یک فایل `seen_titles.json` بسازیم و NewsFetcher را تغییر دهیم که آن را هم چک کند.
    
    print("\n💾 ذخیره عناوین در کش...")
    cache_data = {'seen_ids': list(fetcher.seen_news), 'seen_titles': seen_titles}
    
    # خواندن کش فعلی اگر هست
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                # ادغام ID ها
                existing_ids = set(old_data.get('seen_ids', []))
                existing_ids.update(fetcher.seen_news)
                cache_data['seen_ids'] = list(existing_ids)
        except:
            pass
            
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False)
        
    print("✅ کش به‌روزرسانی شد.")

if __name__ == "__main__":
    main()
