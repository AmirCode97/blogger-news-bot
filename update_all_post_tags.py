import sys
import os
import time
import re
from urllib.parse import quote
from datetime import datetime

# Reconfigure terminal stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from blogger_poster import BloggerPoster

def safe_print(text):
    try:
        print(text)
    except Exception:
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except Exception:
            print("[Print Error] Encoding issue")

def classify_labels(title, content):
    """
    Classify post based on keywords in title or content.
    Returns a list of matching labels (categories).
    """
    search_text = (title + " " + content).lower()
    
    worker_keywords = ['کارگر', 'کارگران', 'اعتصاب', 'حقوق معوقه', 'سندیکا', 'کولبر', 'سوخت‌بر', 'اخراج', 'بازنشستگان', 'حداقل دستمزد', 'حوادث کار']
    prisoner_keywords = ['زندان', 'بازداشت', 'اوین', 'اعدام', 'حبس', 'وثیقه', 'سلول انفرادی', 'اعتصاب غذا', 'شکنجه', 'بند نسوان', 'زندانی سیاسی']
    international_keywords = ['آمریکا', 'واشنگتن', 'ترامپ', 'منطقه', 'دیپلماسی', 'کشورهای', 'خارجه', 'اسپرز', 'فینال', 'نت‌بلاکس', 'چین', 'تنگه هرمز', 'بریتانیا', 'خلیج فارس']
    
    labels = []
    
    # Check Worker news
    if any(kw in search_text for kw in worker_keywords):
        labels.append('کارگران')
        
    # Check Prisoner news
    if any(kw in search_text for kw in prisoner_keywords):
        labels.append('وضعیت زندانیان')
        
    # Check International news
    if any(kw in search_text for kw in international_keywords):
        labels.append('بین‌الملل')
        
    # Fallback to Human Rights if no specific category matches
    if not labels:
        labels.append('حقوق بشر')
        
    return list(set(labels))

def run_repair(dry_run=False, max_updates=250):
    safe_print("=" * 70)
    safe_print("   Blogger News Bot - Retroactive Smart Tag & Footer Repair Utility")
    safe_print("=" * 70)
    safe_print(f"  Max Updates Limit: {max_updates} (to protect Blogger API quotas)")
    if dry_run:
        safe_print(">>> RUNNING IN DRY-RUN MODE (No live modifications will be made) <<<")
    
    poster = BloggerPoster()
    blog_id = poster.blog_id
    safe_print(f"Connected to Blog ID: {blog_id}\n")
    
    posts_processed = 0
    posts_updated = 0
    next_page_token = None
    
    while True:
        try:
            # Fetch batch of posts (Blogger API maximum per request is 150)
            if next_page_token:
                req = poster.service.posts().list(blogId=blog_id, maxResults=150, pageToken=next_page_token)
            else:
                req = poster.service.posts().list(blogId=blog_id, maxResults=150)
                
            res = req.execute()
            items = res.get('items', [])
            
            if not items:
                break
                
            for idx, post in enumerate(items):
                posts_processed += 1
                post_id = post['id']
                title = post['title']
                existing_labels = post.get('labels', [])
                content = post.get('content', '')
                
                # Safety check: Skip live statistics post
                if "Live Statistics" in title or "آمار_زنده" in existing_labels:
                    safe_print(f"\n[{posts_processed}] Skipping Live Stats Post ID: {post_id}")
                    continue
                    
                safe_print(f"\n[{posts_processed}] Processing Post ID: {post_id}")
                safe_print(f"  Title: {title}")
                safe_print(f"  Existing Labels: {existing_labels}")
                
                # 1. Smart classification
                calculated_labels = classify_labels(title, content)
                safe_print(f"  Calculated Labels: {calculated_labels}")
                
                # Check if labels changed or if footer is missing/needs update
                has_correct_labels = set(existing_labels) == set(calculated_labels)
                has_modern_footer = "<!-- SEO Internal Link Tag Cloud & Source Box -->" in content
                
                if has_correct_labels and has_modern_footer:
                    safe_print("  [SKIP] Labels are already accurate and modern footer is present.")
                    continue
                    
                # 2. Build beautiful tags HTML and deep-links
                tag_links = []
                for label in calculated_labels:
                    tag_links.append(
                        f'<a href="/search/label/{quote(label)}" '
                        f'style="color:#c0392b;text-decoration:none;margin-left:12px;font-weight:bold;transition:color 0.2s;" '
                        f'onmouseover="this.style.color=\'#e74c3c\'" onmouseout="this.style.color=\'#c0392b\'">#{label}</a>'
                    )
                tags_html = " ".join(tag_links)
                
                # 3. Rebuild the premium footer matching the user's reference image
                footer_html = f"""<!-- SEO Internal Link Tag Cloud & Source Box -->
<footer style="margin-top:35px;border-top:1px solid #222;padding-top:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;direction:rtl;text-align:right;">
    <div style="font-size:14px;color:#888;margin-bottom:10px;">
        <span style="color:#aaa;margin-left:8px;font-weight:bold;">برچسب‌های مرتبط:</span>
        {tags_html}
    </div>
    <div style="background:#161616;padding:10px 20px;border-radius:8px;border-right:3px solid #c0392b;font-weight:bold;color:#ddd;font-size:13px;box-shadow:0 4px 10px rgba(0,0,0,0.4);margin-bottom:10px;">
        <span style="color:#c0392b;margin-left:8px;">منبع خبر:</span> iranpolnews
    </div>
</footer>"""

                # 4. Clean existing footer(s) and inject new footer
                cleaned_content = content
                for marker in ["<!-- SEO Internal Link Tag Cloud & Source Box -->", "<!-- Source Box -->", "<!-- Source Box"]:
                    if marker in cleaned_content:
                        cleaned_content = cleaned_content.split(marker)[0].strip()
                        
                new_content = cleaned_content + "\n\n" + footer_html
                
                # 5. Save changes to Blogger
                if dry_run:
                    safe_print(f"  [DRY-RUN] Would update labels to {calculated_labels} and refresh HTML footer.")
                else:
                    try:
                        updated_body = {
                            'id': post_id,
                            'title': title,
                            'content': new_content,
                            'labels': calculated_labels
                        }
                        
                        poster.service.posts().update(
                            blogId=blog_id,
                            postId=post_id,
                            body=updated_body
                        ).execute()
                        
                        safe_print(f"  [SUCCESS] Successfully updated post {post_id} on live blog.")
                        posts_updated += 1
                        
                        if posts_updated >= max_updates:
                            safe_print(f"\n[INFO] Reached maximum update limit of {max_updates} posts. Stopping to preserve API quotas.")
                            safe_print("\n" + "=" * 70)
                            safe_print(f"  Job Completed. Processed: {posts_processed} posts | Updated: {posts_updated} posts.")
                            safe_print("=" * 70)
                            return
                            
                        # Delay to protect API quota (1.5 seconds)
                        time.sleep(1.5)
                    except Exception as e:
                        safe_print(f"  [ERROR] Failed to update post {post_id}: {e}")
            
            # Check pagination
            next_page_token = res.get('nextPageToken')
            if not next_page_token:
                break
                
        except Exception as e:
            safe_print(f"[FATAL ERROR] Fetching posts batch failed: {e}")
            break
            
    safe_print("\n" + "=" * 70)
    safe_print(f"  Job Completed. Processed: {posts_processed} posts | Updated: {posts_updated} posts.")
    safe_print("=" * 70)

if __name__ == '__main__':
    # Default to running with modifications. Pass --dry-run to test locally.
    is_dry = '--dry-run' in sys.argv
    run_repair(dry_run=is_dry)
