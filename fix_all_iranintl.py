# اسکریپت اصلاح جامع پست‌های ایران اینترنشنال
# این اسکریپت همه پست‌های ایران اینترنشنال را پیدا می‌کند و محتوای آن‌ها را اصلاح می‌کند

import sys
sys.path.insert(0, '.')

from blogger_poster import BloggerPoster
from news_fetcher import NewsFetcher
import re
import time

BLOG_ID = '1276802394255833723'

def get_all_posts():
    """دریافت همه پست‌های وبلاگ"""
    poster = BloggerPoster()
    posts = []
    page_token = None
    
    print("📥 دریافت همه پست‌های وبلاگ...")
    while True:
        result = poster.service.posts().list(
            blogId=BLOG_ID, 
            maxResults=50, 
            pageToken=page_token
        ).execute()
        posts.extend(result.get('items', []))
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    
    print(f"   پیدا شد: {len(posts)} پست")
    return posts, poster

def identify_iranintl_posts(posts):
    """شناسایی پست‌هایی که از ایران اینترنشنال هستند"""
    iranintl_posts = []
    
    for post in posts:
        content = post.get('content', '')
        title = post.get('title', '')
        
        # بررسی نشانه‌های ایران اینترنشنال
        is_iranintl = False
        
        # ۱. اگر "منبع: ایران اینترنشنال" داشته باشد
        if 'ایران اینترنشنال' in content:
            is_iranintl = True
        
        # ۲. اگر لینک iranintl داشته باشد
        if 'iranintl.com' in content:
            is_iranintl = True
            
        if is_iranintl:
            iranintl_posts.append(post)
    
    return iranintl_posts

def check_if_has_problem(post):
    """بررسی اینکه آیا پست مشکل قاطی شدن محتوا دارد"""
    content = post.get('content', '')
    
    # نشانه‌های مشکل:
    # ۱. تکرار عنوان در متن
    title = post.get('title', '')
    title_short = title[:30] if len(title) > 30 else title
    title_count = content.count(title_short)
    if title_count > 2:  # عنوان بیش از ۲ بار تکرار شده
        return True, "عنوان تکراری"
    
    # ۲. وجود نام‌های نامربوط (نشانه قاطی شدن اخبار)
    # اگر عنوان درباره یک شخص است ولی متن درباره شخص دیگر هم هست
    other_subjects = ['بارو گفت', 'وای‌نت', 'معاریو', 'واشینگتن‌پست گزارش', 
                     'اکسیوس گزارش', 'به گزارش رویترز']
    for subject in other_subjects:
        if subject in content:
            # بررسی کن که این نام در عنوان هم هست یا نه
            if subject.split()[0] not in title:
                return True, f"محتوای نامربوط: {subject}"
    
    # ۳. بیش از ۵ پاراگراف (نشانه قاطی شدن)
    p_count = content.count('<p')
    if p_count > 5:
        return True, f"تعداد پاراگراف زیاد: {p_count}"
    
    return False, "OK"

def extract_article_url_from_post(post):
    """استخراج لینک اصلی خبر از پست"""
    content = post.get('content', '')
    
    # جستجوی لینک iranintl در محتوا
    urls = re.findall(r'https?://(?:www\.)?iranintl\.com/\d+', content)
    if urls:
        return urls[0]
    
    # اگر لینک مستقیم نبود، باید بر اساس عنوان جستجو کنیم
    # این کار پیچیده‌تر است و فعلاً None برمی‌گردانیم
    return None

def main():
    print("=" * 60)
    print("🔧 اسکریپت اصلاح جامع پست‌های ایران اینترنشنال")
    print("=" * 60)
    
    # دریافت پست‌ها
    posts, poster = get_all_posts()
    
    # شناسایی پست‌های ایران اینترنشنال
    iranintl_posts = identify_iranintl_posts(posts)
    print(f"\n📰 پست‌های ایران اینترنشنال: {len(iranintl_posts)}")
    
    # بررسی مشکلات
    problematic_posts = []
    print("\n🔍 بررسی مشکلات...")
    
    for post in iranintl_posts:
        has_problem, reason = check_if_has_problem(post)
        if has_problem:
            problematic_posts.append({
                'post': post,
                'reason': reason
            })
            print(f"   ⚠️ {post['title'][:50]}... - {reason}")
    
    print(f"\n📋 خلاصه:")
    print(f"   کل پست‌ها: {len(posts)}")
    print(f"   پست‌های ایران اینترنشنال: {len(iranintl_posts)}")
    print(f"   پست‌های مشکل‌دار: {len(problematic_posts)}")
    
    if not problematic_posts:
        print("\n✅ هیچ پست مشکل‌داری پیدا نشد!")
        return
    
    # نمایش پست‌های مشکل‌دار
    print("\n" + "=" * 60)
    print("📝 لیست پست‌های مشکل‌دار:")
    print("=" * 60)
    
    for i, item in enumerate(problematic_posts, 1):
        post = item['post']
        print(f"\n[{i}] {post['title'][:60]}...")
        print(f"    دلیل: {item['reason']}")
        print(f"    لینک: {post.get('url', 'N/A')}")

if __name__ == "__main__":
    main()
