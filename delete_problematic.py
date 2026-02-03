# حذف پست‌های مشکل‌دار ایران اینترنشنال
import sys
sys.path.insert(0, '.')

from blogger_poster import BloggerPoster
import re

BLOG_ID = '1276802394255833723'

def get_all_posts(poster):
    """دریافت همه پست‌های وبلاگ"""
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
    return posts

def identify_iranintl_posts(posts):
    """شناسایی پست‌هایی که از ایران اینترنشنال هستند"""
    iranintl_posts = []
    
    for post in posts:
        content = post.get('content', '')
        
        if 'ایران اینترنشنال' in content or 'iranintl.com' in content:
            iranintl_posts.append(post)
    
    return iranintl_posts

def check_if_has_problem(post):
    """بررسی اینکه آیا پست مشکل قاطی شدن محتوا دارد"""
    content = post.get('content', '')
    title = post.get('title', '')
    
    # ۱. تکرار عنوان
    title_short = title[:30] if len(title) > 30 else title
    if content.count(title_short) > 2:
        return True
    
    # ۲. محتوای نامربوط
    other_subjects = ['بارو گفت', 'وای‌نت', 'معاریو', 'واشینگتن‌پست گزارش', 
                     'اکسیوس گزارش', 'به گزارش رویترز']
    for subject in other_subjects:
        if subject in content and subject.split()[0] not in title:
            return True
    
    # ۳. بیش از ۵ پاراگراف
    if content.count('<p') > 5:
        return True
    
    return False

def main():
    print("=" * 60)
    print("🗑️ حذف پست‌های مشکل‌دار ایران اینترنشنال")
    print("=" * 60)
    
    poster = BloggerPoster()
    posts = get_all_posts(poster)
    iranintl_posts = identify_iranintl_posts(posts)
    
    print(f"\n📰 پست‌های ایران اینترنشنال: {len(iranintl_posts)}")
    
    # پیدا کردن پست‌های مشکل‌دار
    problematic = [p for p in iranintl_posts if check_if_has_problem(p)]
    
    print(f"🔍 پست‌های مشکل‌دار: {len(problematic)}")
    
    if not problematic:
        print("\n✅ هیچ پست مشکل‌داری پیدا نشد!")
        return
    
    # حذف پست‌ها
    print(f"\n🗑️ در حال حذف {len(problematic)} پست...")
    
    deleted = 0
    for post in problematic:
        try:
            poster.service.posts().delete(
                blogId=BLOG_ID,
                postId=post['id']
            ).execute()
            deleted += 1
            print(f"   ✅ حذف شد: {post['title'][:50]}...")
        except Exception as e:
            print(f"   ❌ خطا: {post['title'][:50]}... - {e}")
    
    print(f"\n✅ انجام شد! {deleted} پست حذف شد.")
    
    # نمایش تعداد باقی‌مانده
    remaining = get_all_posts(poster)
    print(f"📊 پست‌های باقی‌مانده: {len(remaining)}")

if __name__ == "__main__":
    main()
