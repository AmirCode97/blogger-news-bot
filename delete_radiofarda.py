# حذف همه پست‌های رادیو فردا
import sys
sys.path.insert(0, '.')

from blogger_poster import BloggerPoster

BLOG_ID = '1276802394255833723'

def main():
    print("=" * 60)
    print("🗑️ حذف همه پست‌های رادیو فردا")
    print("=" * 60)
    
    poster = BloggerPoster()
    
    # دریافت همه پست‌ها
    posts = []
    page_token = None
    print("📥 دریافت پست‌ها...")
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
    
    print(f"   کل پست‌ها: {len(posts)}")
    
    # پیدا کردن پست‌های رادیو فردا
    farda_posts = []
    for post in posts:
        content = post.get('content', '')
        if 'رادیو فردا' in content or 'radiofarda' in content.lower():
            farda_posts.append(post)
    
    print(f"📻 پست‌های رادیو فردا: {len(farda_posts)}")
    
    if not farda_posts:
        print("✅ هیچ پستی از رادیو فردا پیدا نشد!")
        return
    
    # حذف
    print(f"\n🗑️ در حال حذف...")
    deleted = 0
    for post in farda_posts:
        try:
            poster.service.posts().delete(blogId=BLOG_ID, postId=post['id']).execute()
            deleted += 1
            print(f"   ✅ {post['title'][:50]}...")
        except Exception as e:
            print(f"   ❌ خطا: {e}")
    
    print(f"\n✅ {deleted} پست حذف شد!")

if __name__ == "__main__":
    main()
