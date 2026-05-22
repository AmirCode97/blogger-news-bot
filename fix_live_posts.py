import sys
import os
import time
from urllib.parse import quote

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from blogger_poster import BloggerPoster

def safe_print(text):
    try:
        print(text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8'))
    except:
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print(text)

def run_fix():
    safe_print("=" * 60)
    safe_print("  Live Posts Image Fixer - Injecting Fallback Stock Images")
    safe_print("=" * 60)

    poster = BloggerPoster()
    safe_print(f"Connected to Blog ID: {poster.blog_id}")

    targets = {
        "4566076101771367375": {
            "title": "بحران هوای خوزستان: غبار سمی نفس مردم را بند آورد",
            "image": "7oesnmsu0RfrE2W7Lk0C.png",
            "category": "حقوق بشر"
        },
        "7937031076052603044": {
            "title": "موج جدید پلمب واحدهای صنفی در کاشان: کشف حجاب عامل تعطیلی یک کافه",
            "image": "xvVwjvWLG5ADOxW4EIgY.png",
            "category": "حقوق بشر"
        },
        "8656571386204910865": {
            "title": "مرگ در زندان؛ پرونده سیاه اعدام دو فعال سیاسی در ایران",
            "image": "opBNOv604Cccl4DLBh33.png",
            "category": "وضعیت زندانیان"
        },
        "42661393950526048": {
            "title": "سازمان عفو بین‌الملل پرده از ابعاد هولناک اعدام‌ها در ایران برداشت: هشداری جدی برای جامعه جهانی",
            "image": "z5zgF2E9yC3E3EHwViDu.png",
            "category": "وضعیت زندانیان"
        },
        "950771976670731036": {
            "title": "پایان تلخ زندگی؛ اجرای حکم اعدام در سکوت خبری",
            "image": "djBWFeRxBpG2ZR4NgCR1.png",
            "category": "وضعیت زندانیان"
        }
    }

    updated_count = 0

    for post_id, info in targets.items():
        safe_print(f"\nProcessing Post ID: {post_id}")
        safe_print(f"  Title: {info['title']}")
        safe_print(f"  Category: {info['category']} | Target Image: {info['image']}")

        try:
            # 1. Fetch live post
            post = poster.service.posts().get(
                blogId=poster.blog_id,
                postId=post_id
            ).execute()

            content = post.get('content', '')
            
            # Check if there is already an image in the content
            if "wsrv.nl" in content or "jsdelivr.net" in content:
                safe_print("  [SKIP] Image already exists in post content.")
                continue

            # 2. Build beautiful image HTML with proxy and CDN
            image_url = f"https://cdn.jsdelivr.net/gh/AmirCode97/blogger-news-bot@main/images/{info['image']}"
            proxied_image = f"https://wsrv.nl/?url={quote(image_url)}"
            image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{proxied_image}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>'

            # 3. Inject image after </style> tag if present, else at start
            style_end = content.find('</style>')
            if style_end != -1:
                insert_pos = style_end + len('</style>')
                new_content = content[:insert_pos] + '\n' + image_html + '\n' + content[insert_pos:]
            else:
                new_content = image_html + '\n' + content

            # 4. Update the live post via API
            body = {
                'id': post_id,
                'title': post.get('title'),
                'content': new_content,
                'labels': post.get('labels', [])
            }

            poster.service.posts().update(
                blogId=poster.blog_id,
                postId=post_id,
                body=body
            ).execute()

            safe_print(f"  [SUCCESS] Updated post on Blogger!")
            updated_count += 1

            # Small delay to avoid API rate limits
            time.sleep(2)

        except Exception as e:
            safe_print(f"  [ERROR] Failed to update post {post_id}: {e}")

    safe_print("\n" + "=" * 60)
    safe_print(f"  Fix completed. Successfully updated {updated_count} posts.")
    safe_print("=" * 60)

if __name__ == '__main__':
    run_fix()
