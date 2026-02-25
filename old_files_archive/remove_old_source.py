"""
Remove OLD source boxes (with "Source:") and keep ONLY the Premium Source Box
حذف باکس منبع قدیمی و نگه داشتن فقط باکس منبع جدید
"""

import os, sys, pickle, re, time
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

def remove_old_source_box(html):
    """Remove the old-style source box while keeping Premium Source Box"""
    original = html
    
    # Pattern 1: Old source box with "Source:" text
    # <div style="...border-left:...solid #ce0000..."><p...>Source: <a ...>...</a></p></div>
    html = re.sub(
        r'<div[^>]*border-left[^>]*#ce0000[^>]*>\s*<p[^>]*>\s*Source\s*:\s*<a[^>]*>[^<]*</a>\s*</p>\s*</div>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Pattern 2: Old source box with "Source:" and border-right
    html = re.sub(
        r'<div[^>]*>\s*<p[^>]*(?:font-size:\s*13px|font-size:\s*12px)[^>]*>\s*Source\s*:\s*<a[^>]*>[^<]*</a>\s*</p>\s*</div>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Pattern 3: Any div containing exactly "Source:" followed by a link
    html = re.sub(
        r'<div[^>]*>\s*<p[^>]*>\s*Source\s*:\s*<a\s[^>]*>[^<]*</a>\s*</p>\s*</div>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Pattern 4: Old source with "منبع خبر:" (old format, not "منبع اصلی مقاله:")
    html = re.sub(
        r'<div[^>]*>\s*<p[^>]*>\s*(?:منبع\s*خبر|منبع\s*:)\s*<a[^>]*>[^<]*</a>\s*</p>\s*</div>',
        '', html, flags=re.DOTALL | re.IGNORECASE
    )
    
    # Pattern 5: Source box with just "Source" or ":Source" without proper Premium styling
    # Match divs that have Source but NOT "منبع اصلی مقاله"
    def remove_old_not_new(match):
        block = match.group(0)
        if 'منبع اصلی مقاله' in block:
            return block  # Keep the new Premium box
        if 'Source' in block or 'منبع خبر' in block or 'منبع:' in block:
            return ''  # Remove old box
        return block
    
    # Find all div blocks that contain source info
    html = re.sub(
        r'<div[^>]*(?:border-(?:left|right)[^>]*#ce0000|background:#fff)[^>]*>[\s\S]*?</div>',
        remove_old_not_new, html
    )
    
    # Clean up multiple blank lines
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    return html, html != original


def main():
    print("=" * 70)
    print("🔧 REMOVING OLD SOURCE BOXES FROM ALL POSTS")
    print("=" * 70)
    
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('blogger', 'v3', credentials=creds)
    
    # Fetch ALL posts
    print("\n📥 Fetching all posts...")
    all_posts = []
    page_token = None
    while True:
        result = service.posts().list(blogId=BLOG_ID, maxResults=50, pageToken=page_token).execute()
        all_posts.extend(result.get('items', []))
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    
    print(f"📊 Found {len(all_posts)} posts\n")
    
    updated = 0
    skipped = 0
    
    for i, post in enumerate(all_posts, 1):
        title = post.get('title', '')[:50]
        content = post.get('content', '')
        
        fixed_html, changed = remove_old_source_box(content)
        
        if changed:
            try:
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=post['id'],
                    body={'content': fixed_html}
                ).execute()
                print(f"  ✅ [{i}/{len(all_posts)}] Fixed: {title}...")
                updated += 1
                time.sleep(1)
            except Exception as e:
                print(f"  ❌ [{i}/{len(all_posts)}] Error: {title}... - {e}")
        else:
            print(f"  ⏭️  [{i}/{len(all_posts)}] Clean: {title}...")
            skipped += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Updated: {updated}")
    print(f"⏭️  Already clean: {skipped}")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
