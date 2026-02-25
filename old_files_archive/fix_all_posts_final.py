"""
Fix ALL blog posts:
1. Change ALL text colors to white (#fff)
2. Ensure proper source box styling (exactly like the screenshot)
3. Update ALL posts in the blog

اصلاح تمامی پست‌ها:
۱. تغییر رنگ تمام متون به سفید
۲. اطمینان از استایل صحیح باکس منبع
۳. به‌روزرسانی تمامی پست‌ها
"""

import os
import sys
import re
import pickle
import time
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

# The EXACT source box HTML we want (matching the screenshot)
SOURCE_BOX_TEMPLATE = '''
<!-- Premium Source Box -->
<div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
    <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
        <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
        <a href="{url}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در {source}</a>
    </p>
</div>
'''

def fix_post_html(html, title=""):
    """Fix all issues in post HTML"""
    original_html = html
    
    # ========================================
    # 1. FIX TEXT COLORS - Change all dark colors to white
    # ========================================
    
    # Fix color:#333 -> color:#fff
    html = re.sub(r'color\s*:\s*#333\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#444\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#555\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#666\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#222\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#111\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#000\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*black\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#eee\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#ddd\b', 'color:#fff', html)
    html = re.sub(r'color\s*:\s*#ccc\b', 'color:#fff', html)
    
    # Fix any remaining dark text in inline styles
    # Match color:rgb(xx,xx,xx) where values are dark (< 128)
    def fix_rgb_color(match):
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if r < 180 and g < 180 and b < 180:
            return 'color:#fff'
        return match.group(0)
    
    html = re.sub(r'color\s*:\s*rgb\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\)', fix_rgb_color, html)
    
    # ========================================
    # 2. FIX SOURCE BOX - but keep the color inside source box correct
    # ========================================
    
    # Extract the source URL from existing source box
    source_url = ""
    source_name = ""
    
    # Pattern to find source link
    source_link_match = re.search(r'href="([^"]*)"[^>]*>(?:مشاهده در\s*)?([^<]*)</a>', html)
    
    # Try various patterns to find source info
    patterns = [
        # Pattern: منبع اصلی مقاله with link
        r'منبع\s*(?:اصلی)?\s*(?:مقاله|خبر)\s*:.*?href="([^"]*)"[^>]*>([^<]*)</a>',
        # Pattern: any link in source div
        r'<div[^>]*>.*?منبع.*?href="([^"]*)"[^>]*>([^<]*)</a>',
        # Last resort - find last link
        r'href="(https?://[^"]*(?:iranhrs|iranintl|iran-hrm|eu-today)[^"]*)"[^>]*>([^<]*)</a>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if match:
            source_url = match.group(1)
            source_name = match.group(2).strip()
            # Clean up source name
            source_name = re.sub(r'^مشاهده در\s*', '', source_name).strip()
            if not source_name or source_name == '':
                # Extract domain name
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', source_url)
                if domain_match:
                    source_name = domain_match.group(1)
            break
    
    if not source_url:
        # Try to extract any external link
        ext_links = re.findall(r'href="(https?://(?!iranpolnews)[^"]*)"', html)
        if ext_links:
            source_url = ext_links[-1]  # Last external link
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', source_url)
            source_name = domain_match.group(1) if domain_match else "Source"
    
    # Remove ALL existing source boxes (various patterns)
    source_patterns = [
        # Pattern 1: div containing منبع
        r'<div[^>]*>[\s\S]*?منبع\s*(?:اصلی)?\s*(?:مقاله|خبر)\s*:[\s\S]*?</div>\s*(?:</div>)?',
        # Pattern 2: old-style source paragraph
        r'<p[^>]*>[\s\S]*?منبع\s*(?:اصلی)?\s*(?:مقاله|خبر)\s*:[\s\S]*?</p>',
        # Pattern 3: Comment + source box  
        r'<!--\s*(?:Premium\s*)?Source\s*Box\s*-->[\s\S]*?</div>',
        # Pattern 4: div with source styling
        r'<div[^>]*border-right:\s*5px\s*solid\s*#ce0000[^>]*>[\s\S]*?منبع[\s\S]*?</div>\s*</div>',
    ]
    
    for pattern in source_patterns:
        html = re.sub(pattern, '', html, flags=re.IGNORECASE | re.DOTALL)
    
    # Add the correct source box at the end
    if source_url:
        new_source_box = SOURCE_BOX_TEMPLATE.format(url=source_url, source=source_name)
        
        # Fix: inside source box, text must be #555, not #fff
        # We already changed #555 to #fff globally, but source box needs #555
        # So the template already has the correct colors
        
        html = html.rstrip()
        html += '\n' + new_source_box
    
    # ========================================
    # 3. RESTORE SOURCE BOX INTERNAL COLORS
    # ========================================
    # The source box background is white, so text inside needs to be dark
    # We fix this by replacing the source box section specifically
    # The template already has correct colors (background:#fff, color:#555)
    
    # ========================================
    # 4. ENSURE STYLE TAG EXISTS
    # ========================================
    if '.post-featured-image' not in html:
        html = '<style>.post-featured-image, .post-thumbnail { display: none !important; }</style>\n' + html
    
    return html, html != original_html


def main():
    print("=" * 70)
    print("🔧 FIXING ALL BLOG POSTS - White Text + Source Box")
    print("=" * 70)
    
    # Init Blogger API
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
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, post in enumerate(all_posts, 1):
        title = post.get('title', '')[:50]
        post_id = post.get('id', '')
        url = post.get('url', '')
        content = post.get('content', '')
        
        # Fix the HTML
        fixed_html, was_changed = fix_post_html(content, title)
        
        if was_changed:
            try:
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=post_id,
                    body={'content': fixed_html}
                ).execute()
                
                print(f"  ✅ [{i}/{len(all_posts)}] Updated: {title}...")
                updated_count += 1
                
                # Small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ [{i}/{len(all_posts)}] Error: {title}... - {e}")
                error_count += 1
        else:
            print(f"  ⏭️  [{i}/{len(all_posts)}] No change: {title}...")
            skipped_count += 1
    
    print(f"\n{'=' * 70}")
    print(f"📊 RESULTS:")
    print(f"   ✅ Updated: {updated_count}")
    print(f"   ⏭️  No change: {skipped_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()
