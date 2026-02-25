"""
FINAL COMPREHENSIVE FIX for ALL blog posts:
1. Fix ALL dark text colors -> white (#fff)
2. Remove ALL old "Source:" boxes
3. Add Premium "منبع اصلی مقاله:" box if missing
4. Fix old image styles to new premium style
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os
import pickle
import re
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

SOURCE_BOX_TEMPLATE = """
<!-- Premium Source Box -->
<div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
    <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
        <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
        <a href="{url}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در {source}</a>
    </p>
</div>
"""

def fix_post_content(content):
    """Fix all known issues in post HTML"""
    original = content
    
    # ============================================
    # 1. FIX TEXT COLORS: All dark -> white
    # ============================================
    dark_colors = ['#333', '#444', '#555', '#222', '#111', '#000', '#333333', '#444444', '#555555']
    for dark in dark_colors:
        content = content.replace(f'color:{dark}', 'color:#fff')
        content = content.replace(f'color: {dark}', 'color:#fff')
    
    # ============================================
    # 2. EXTRACT SOURCE URL from old box before removing
    # ============================================
    source_url = ""
    source_name = ""
    
    # Find source URL in old box
    old_source_match = re.search(
        r'<div[^>]*(?:background:#f9f9f9|border-right:4px)[^>]*>.*?<a\s+href="([^"]*)"[^>]*>([^<]*)</a>',
        content, re.DOTALL
    )
    if old_source_match:
        source_url = old_source_match.group(1)
        source_name = old_source_match.group(2)
    
    # Also check for "Source:" pattern
    if not source_url:
        source_match = re.search(r'Source:\s*<a\s+href="([^"]*)"[^>]*>([^<]*)</a>', content, re.DOTALL)
        if source_match:
            source_url = source_match.group(1)
            source_name = source_match.group(2)
    
    # ============================================
    # 3. REMOVE ALL OLD SOURCE BOXES
    # ============================================
    # Pattern: old source box with background:#f9f9f9
    content = re.sub(
        r'<div[^>]*background:#f9f9f9[^>]*>.*?</div>',
        '', content, flags=re.DOTALL
    )
    
    # Pattern: old source box with border-right:4px
    content = re.sub(
        r'<div[^>]*border-right:4px\s+solid\s+#ce0000[^>]*>\s*<p[^>]*>\s*Source:.*?</div>',
        '', content, flags=re.DOTALL
    )
    
    # Pattern: any remaining "Source: <a>" blocks  
    content = re.sub(
        r'<div[^>]*>\s*<p[^>]*>\s*Source:\s*<a[^>]*>.*?</a>\s*</p>\s*</div>',
        '', content, flags=re.DOTALL
    )
    
    # ============================================
    # 4. FIX IMAGE STYLE (old -> premium)
    # ============================================
    # Old: <div style="margin-bottom:25px;"><img ... style="width:100%;max-width:700px;border-radius:8px;">
    # New: <div style="margin-bottom:25px;text-align:center;"><img ... style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);">
    content = re.sub(
        r'<div style="margin-bottom:25px;">',
        '<div style="margin-bottom:25px;text-align:center;">',
        content
    )
    content = re.sub(
        r'max-width:700px;border-radius:8px;',
        'max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);',
        content
    )
    
    # ============================================
    # 5. FIX TEXT CONTAINER (old -> premium)
    # ============================================
    # Old: <div style="font-size:16px;line-height:2.2;color:#fff;">
    # New: <div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
    content = re.sub(
        r'<div style="font-size:16px;line-height:2\.2;color:#fff;">',
        '<div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:\'Vazir\',sans-serif;">',
        content
    )
    
    # ============================================
    # 6. ADD PREMIUM SOURCE BOX if missing
    # ============================================
    if 'منبع اصلی مقاله:' not in content and source_url:
        premium_box = SOURCE_BOX_TEMPLATE.format(url=source_url, source=source_name or "منبع")
        content = content.rstrip() + "\n" + premium_box
    
    # ============================================
    # 7. FIX SOURCE BOX TEXT COLOR (in existing premium boxes)
    # ============================================
    # The source box should have color:#555 for text, NOT color:#fff
    content = re.sub(
        r'(منبع اصلی مقاله.*?<p[^>]*style="[^"]*?)color:#fff',
        r'\1color:#555',
        content, flags=re.DOTALL
    )
    
    return content, content != original

# ============================================
# MAIN EXECUTION
# ============================================
print("=" * 70)
print("🔧 COMPREHENSIVE FIX FOR ALL POSTS")
print("=" * 70)

# Get ALL posts
all_posts = []
page_token = None
while True:
    result = service.posts().list(
        blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token
    ).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

print(f"📊 Found {len(all_posts)} posts\n")

fixed_count = 0
clean_count = 0

for i, post in enumerate(all_posts, 1):
    title = post.get("title", "")[:60]
    content = post.get("content", "")
    post_id = post.get("id")
    
    fixed_content, was_changed = fix_post_content(content)
    
    if was_changed:
        try:
            service.posts().patch(
                blogId=BLOG_ID,
                postId=post_id,
                body={"content": fixed_content}
            ).execute()
            fixed_count += 1
            print(f"  ✅ [{i}/{len(all_posts)}] Fixed: {title}...")
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ [{i}/{len(all_posts)}] Error: {title}... ({e})")
    else:
        clean_count += 1
        print(f"  ⏭️  [{i}/{len(all_posts)}] Clean: {title}...")

print(f"\n{'='*70}")
print(f"✅ Fixed: {fixed_count}")
print(f"⏭️  Already clean: {clean_count}")
print(f"{'='*70}")
