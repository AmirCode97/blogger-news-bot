"""
بازنویسی تمام پست‌های قبلی وبلاگ با هوش مصنوعی
Rewrite ALL existing blog posts using AI to make them unique for Google SEO

This script:
1. Fetches all posts from your Blogger blog
2. Rewrites each post's title and content using Gemini AI
3. Removes the "منبع: ..." from the source box
4. Updates each post on Blogger
5. Saves progress so it can resume if interrupted
"""

import os
import re
import sys
import json
import time
from datetime import datetime

from blogger_poster import BloggerPoster
from ai_processor import AIProcessor
from config import BLOG_ID

# Progress file to track which posts have been rewritten
PROGRESS_FILE = "rewrite_progress.json"

def load_progress():
    """Load progress from file to resume if interrupted."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"rewritten_ids": [], "failed_ids": [], "total_processed": 0}

def save_progress(progress):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def extract_plain_text(html_content):
    """Extract plain text from HTML for AI processing."""
    # Remove HTML tags
    text = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove source box text patterns
    text = re.sub(r'خبرگزاری:\s*iranpolnews.*$', '', text)
    text = re.sub(r'منبع:.*$', '', text)
    return text.strip()

def extract_image_from_html(html_content):
    """Extract the main image URL from post HTML."""
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_content)
    if img_match:
        return img_match.group(1)
    return ""

def fix_source_box(html_content):
    """Remove source name from the source box, keep only iranpolnews."""
    # Pattern 1: Full source box with data attributes and source name
    html_content = re.sub(
        r'<div[^>]*data-source-url="[^"]*"[^>]*data-source-name="[^"]*"[^>]*>.*?</div>',
        '<div style="background:#1a1a1a; padding:12px 25px; border-radius:8px; border-right:3px solid #c0392b; font-weight:bold; color:#ddd; display:inline-block; margin:30px 0 10px 0; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);"><span style="color:#c0392b; margin-left:8px;">خبرگزاری:</span> iranpolnews</div>',
        html_content,
        flags=re.DOTALL
    )
    # Pattern 2: Source box with "| منبع: ..."
    html_content = re.sub(
        r'(خبرگزاری:</span>\s*iranpolnews)\s*\|\s*<span[^>]*>منبع:[^<]*</span>',
        r'\1',
        html_content
    )
    # Pattern 3: Any remaining "منبع: ..." text in source boxes
    html_content = re.sub(
        r'\|\s*<span[^>]*font-weight:normal[^>]*>منبع:[^<]*</span>',
        '',
        html_content
    )
    return html_content

def build_rewritten_html(original_html, ai_response, main_image):
    """Build new HTML content from AI response, preserving the blog's style."""
    # Parse AI response
    final_fa = ""
    final_en = ""
    final_de = ""
    
    if "===PERSIAN===" in ai_response:
        try:
            parts = ai_response.split("===PERSIAN===")[1].split("===ENGLISH===")
            if len(parts) > 0:
                final_fa = parts[0].strip()
            if len(parts) > 1:
                en_parts = parts[1].split("===GERMAN===")
                final_en = en_parts[0].strip()
                if len(en_parts) > 1:
                    de_parts = en_parts[1].split("===TAGS===")
                    final_de = de_parts[0].strip()
        except:
            pass
    
    if not final_fa or len(final_fa) < 50:
        return None  # AI failed, skip this post
    
    # Build image HTML
    image_html = ""
    if main_image:
        image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{main_image}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>'
    
    # Insert jump break after first paragraph
    description_with_break = final_fa
    if "\n" in final_fa:
        parts = final_fa.split("\n", 1)
        description_with_break = parts[0] + "\n<!--more-->\n" + parts[1]
    elif len(final_fa) > 300:
        description_with_break = final_fa[:300] + "<!--more-->" + final_fa[300:]

    # Build the full HTML
    html_content = f"""
    <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
    {image_html}
    
    <!-- Persian Section -->
    <div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
        {description_with_break}
    </div>
    """
    
    if final_en:
        html_content += f"""
    <!-- English Section -->
    <div style="margin-top:30px;padding-top:20px;border-top:1px dashed #555;direction:ltr;text-align:left;font-family:sans-serif;color:#fff;">
        <h3 style="color:#ce0000;margin-bottom:10px;">🇬🇧 English Summary</h3>
        <div style="font-size:15px;line-height:1.8;color:#fff;">{final_en}</div>
    </div>
    """
    
    if final_de:
        html_content += f"""
    <!-- German Section -->
    <div style="margin-top:30px;padding-top:20px;border-top:1px dashed #555;direction:ltr;text-align:left;font-family:sans-serif;color:#fff;">
        <h3 style="color:#ce0000;margin-bottom:10px;">🇩🇪 Zusammenfassung (Deutsch)</h3>
        <div style="font-size:15px;line-height:1.8;color:#fff;">{final_de}</div>
    </div>
    """
    
    # Source box - ONLY iranpolnews, no original source
    html_content += """
    <!-- Source Box -->
    <div style="text-align: right; direction: rtl;">
        <div style="background:#1a1a1a; padding:12px 25px; border-radius:8px; border-right:3px solid #c0392b; font-weight:bold; color:#ddd; display:inline-block; margin:30px 0 10px 0; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);">
            <span style="color:#c0392b; margin-left:8px;">خبرگزاری:</span> iranpolnews
        </div>
    </div>
    """
    
    return html_content

def fetch_all_posts(poster):
    """Fetch all posts from the blog using pagination."""
    all_posts = []
    page_token = None
    
    print("[INFO] Fetching all blog posts...")
    
    while True:
        try:
            kwargs = {
                'blogId': poster.blog_id,
                'maxResults': 50,
                'status': 'LIVE',
                'fetchBodies': True,
            }
            if page_token:
                kwargs['pageToken'] = page_token
            
            result = poster.service.posts().list(**kwargs).execute()
            
            posts = result.get('items', [])
            all_posts.extend(posts)
            print(f"  Fetched {len(all_posts)} posts so far...")
            
            page_token = result.get('nextPageToken')
            if not page_token:
                break
                
            time.sleep(1)  # Rate limit
            
        except Exception as e:
            print(f"[ERROR] Fetching posts: {e}")
            break
    
    print(f"[INFO] Total posts found: {len(all_posts)}")
    return all_posts

def rewrite_all_posts():
    """Main function to rewrite all existing blog posts."""
    print("=" * 60)
    print("  بازنویسی تمام پست‌های وبلاگ با هوش مصنوعی")
    print("  Rewriting ALL Blog Posts with AI")
    print("=" * 60)
    
    # Initialize
    poster = BloggerPoster()
    ai = AIProcessor()
    
    if not ai.model:
        print("[FATAL] AI model could not be initialized. Check your GEMINI_API_KEY.")
        return
    
    progress = load_progress()
    rewritten_ids = set(progress["rewritten_ids"])
    failed_ids = set(progress["failed_ids"])
    
    print(f"[INFO] Previously rewritten: {len(rewritten_ids)} posts")
    print(f"[INFO] Previously failed: {len(failed_ids)} posts")
    
    # Fetch all posts
    all_posts = fetch_all_posts(poster)
    
    if not all_posts:
        print("[ERROR] No posts found!")
        return
    
    # Filter out already processed posts
    posts_to_process = [
        p for p in all_posts 
        if p['id'] not in rewritten_ids and p['id'] not in failed_ids
    ]
    
    print(f"\n[INFO] Posts remaining to process: {len(posts_to_process)}")
    print(f"[INFO] Starting rewrite process...\n")
    
    success_count = 0
    fail_count = 0
    consecutive_failures = 0  # Track consecutive failures to detect API key issues
    
    for i, post in enumerate(posts_to_process):
        post_id = post['id']
        original_title = post.get('title', 'No Title')
        original_content = post.get('content', '')
        labels = post.get('labels', [])
        
        # Skip the special "مقاله" posts (user-written articles)
        if 'مقاله' in labels:
            print(f"[{i+1}/{len(posts_to_process)}] SKIP (مقاله): {original_title[:50]}...")
            rewritten_ids.add(post_id)
            continue
        
        safe_title = original_title[:50]
        try:
            safe_title = safe_title.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
        except:
            safe_title = original_title[:50]
        
        print(f"\n[{i+1}/{len(posts_to_process)}] Processing: {safe_title}...")
        
        # Extract plain text and image
        plain_text = extract_plain_text(original_content)
        main_image = extract_image_from_html(original_content)
        
        if len(plain_text) < 30:
            print(f"  [SKIP] Too short ({len(plain_text)} chars)")
            rewritten_ids.add(post_id)
            continue
        
        # Call AI to rewrite
        try:
            print(f"  [AI] Rewriting with Gemini...")
            new_title, ai_response = ai.process_news(original_title, plain_text)
            
            # Check if AI returned the original content unchanged (means API failed)
            if ai_response == plain_text:
                consecutive_failures += 1
                print(f"  [FAIL] AI returned original content (failure #{consecutive_failures})")
                if consecutive_failures >= 3:
                    print("\n" + "!" * 60)
                    print("  [FATAL] 3 consecutive AI failures detected!")
                    print("  This usually means your GEMINI_API_KEY is expired or invalid.")
                    print("  Please get a new key from: https://aistudio.google.com/apikey")
                    print("  Then update it in the .env file and re-run this script.")
                    print("!" * 60)
                    break
                time.sleep(5)
                continue
            
            if not new_title or new_title == original_title:
                # AI didn't generate a unique title, try extracting from response
                if "===TITLE===" in ai_response:
                    try:
                        title_part = ai_response.split("===TITLE===")[1].split("===PERSIAN===")[0]
                        new_title = title_part.strip()
                    except:
                        new_title = original_title
            
            # Build new HTML
            new_html = build_rewritten_html(original_content, ai_response, main_image)
            
            if not new_html:
                consecutive_failures += 1
                print(f"  [FAIL] AI output was insufficient (failure #{consecutive_failures})")
                if consecutive_failures >= 3:
                    print("\n" + "!" * 60)
                    print("  [FATAL] 3 consecutive AI failures detected!")
                    print("  This usually means your GEMINI_API_KEY is expired or invalid.")
                    print("  Please get a new key from: https://aistudio.google.com/apikey")
                    print("  Then update it in the .env file and re-run this script.")
                    print("!" * 60)
                    break
                time.sleep(5)
                continue
            
            # Update on Blogger
            print(f"  [UPDATE] New title: {new_title[:50]}...")
            post_body = {
                'id': post_id,
                'title': new_title,
                'content': new_html,
                'labels': labels
            }
            
            resp = poster.service.posts().update(
                blogId=poster.blog_id, postId=post_id, body=post_body
            ).execute()
            
            if resp:
                print(f"  [OK] Updated: {resp.get('url', 'success')}")
                success_count += 1
                rewritten_ids.add(post_id)
                consecutive_failures = 0  # Reset on success
            else:
                print(f"  [FAIL] Blogger API returned None")
                failed_ids.add(post_id)
                fail_count += 1
            
        except Exception as e:
            error_str = str(e)
            print(f"  [ERROR] {error_str[:100]}")
            
            # Check for API key errors - stop immediately
            if 'API_KEY_INVALID' in error_str or 'API key expired' in error_str:
                print("\n" + "!" * 60)
                print("  [FATAL] API Key is expired or invalid!")
                print("  Get a new key from: https://aistudio.google.com/apikey")
                print("  Update GEMINI_API_KEY in .env file and re-run.")
                print("!" * 60)
                break
            
            failed_ids.add(post_id)
            fail_count += 1
            consecutive_failures += 1
        
        # Save progress after each post
        save_progress({
            "rewritten_ids": list(rewritten_ids),
            "failed_ids": list(failed_ids),
            "total_processed": len(rewritten_ids) + len(failed_ids)
        })
        
        # Rate limiting: wait between posts
        wait_time = 5  # seconds between each post (reduced for GitHub Actions 6h limit)
        print(f"  [WAIT] {wait_time}s delay...")
        time.sleep(wait_time)
    
    # Final report
    print("\n" + "=" * 60)
    print("  گزارش نهایی / Final Report")
    print("=" * 60)
    print(f"  Total posts:     {len(all_posts)}")
    print(f"  Rewritten:       {success_count}")
    print(f"  Failed:          {fail_count}")
    print(f"  Previously done: {len(progress['rewritten_ids'])}")
    print(f"  Skipped:         {len(all_posts) - len(posts_to_process)}")
    print("=" * 60)

if __name__ == '__main__':
    rewrite_all_posts()
