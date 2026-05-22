"""
Fix Missing Images in Blog Posts
اسکریپت اصلاح عکس‌های خالی در پست‌های وبلاگ

This script:
1. Lists all blog posts
2. Identifies posts with no image in their HTML content
3. Tries to extract the original article link from the post
4. Fetches the original article page to get the image
5. Updates the post with the found image
"""

import sys
import os
import re
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from blogger_poster import BloggerPoster
from news_fetcher import NewsFetcher


def find_source_link(html_content):
    """Extract the original article URL from the post's source box or content."""
    # Look for links in the post
    import re
    
    # Pattern 1: Look for href links in the post content (excluding blogspot links)
    links = re.findall(r'href=["\']([^"\']+)["\']', html_content)
    for link in links:
        if 'blogspot.com' not in link and 'blogger.com' not in link:
            if any(domain in link for domain in ['iranhr.net', 'humanrightsinir.org', 'iranintl.com', 'iranhrs.org', 'iran-hrm.com']):
                return link
    
    return None


def post_has_image(html_content):
    """Check if the post content contains any meaningful image."""
    if not html_content:
        return False
    
    # Check for img tags
    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_content)
    
    for src in img_matches:
        # Skip tiny icons, logos, data URIs that are too small
        src_lower = src.lower()
        if any(skip in src_lower for skip in ['logo', 'icon', 'avatar', 'pixel', 'badge', '1x1', 'spacer']):
            continue
        # This is likely a real article image
        return True
    
    return False


def extract_image_from_post_title(title, fetcher):
    """Try to find an image by searching for the article on known sources."""
    # This is a best-effort approach
    return None


def fix_missing_images():
    """Main function to fix all posts with missing images."""
    print("=" * 60)
    print("  Image Fixer - Fixing posts with missing images")
    print("=" * 60)
    
    # Initialize
    poster = BloggerPoster()
    fetcher = NewsFetcher()
    
    page_token = None
    total_count = 0
    no_image_count = 0
    fixed_count = 0
    failed_posts = []
    
    while True:
        try:
            params = {
                'blogId': poster.blog_id,
                'maxResults': 50,
            }
            if page_token:
                params['pageToken'] = page_token
            
            resp = poster.service.posts().list(**params).execute()
            posts = resp.get('items', [])
            
            if not posts:
                break
            
            for post in posts:
                total_count += 1
                content = post.get('content', '')
                title = post.get('title', '')
                post_id = post.get('id', '')
                
                # Check if post has image
                if post_has_image(content):
                    continue
                
                no_image_count += 1
                safe_title = title[:60].encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                print(f"\n[NO IMAGE] Post #{total_count}: {safe_title}")
                print(f"  Post ID: {post_id}")
                
                # Strategy 1: Find original source link in the post
                source_link = find_source_link(content)
                
                if source_link:
                    print(f"  Source: {source_link[:80]}")
                    
                    # Fetch the original article to get the image
                    source_name = ""
                    if 'iranhr.net' in source_link:
                        source_name = "سازمان حقوق بشر ایران"
                    elif 'humanrightsinir.org' in source_link:
                        source_name = "حقوق بشر در ایران"
                    elif 'iranhrs.org' in source_link:
                        source_name = "کانون حقوق بشر ایران"
                    elif 'iran-hrm.com' in source_link:
                        source_name = "ناظران حقوق بشر ایران"
                    elif 'iranintl.com' in source_link:
                        source_name = "ایران اینترنشنال"
                    
                    result = fetcher.fetch_full_article(source_link, source_name)
                    image_url = result.get('main_image')
                    
                    if image_url:
                        print(f"  [FOUND] Image: {image_url[:80]}")
                        
                        # Build the image HTML
                        image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{image_url}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>'
                        
                        # Insert the image after the <style> tag (if present) or at the beginning
                        new_content = content
                        
                        # Check if there's already an image_html div (empty or broken)
                        # Pattern: <style>...</style> followed by content
                        style_end = content.find('</style>')
                        if style_end != -1:
                            insert_pos = style_end + len('</style>')
                            new_content = content[:insert_pos] + '\n' + image_html + '\n' + content[insert_pos:]
                        else:
                            # Just prepend the image
                            new_content = image_html + '\n' + content
                        
                        # Update the post
                        try:
                            body = {
                                'id': post_id,
                                'title': title,
                                'content': new_content,
                                'labels': post.get('labels', [])
                            }
                            poster.service.posts().update(
                                blogId=poster.blog_id,
                                postId=post_id,
                                body=body
                            ).execute()
                            fixed_count += 1
                            print(f"  [FIXED] ✅ Image added successfully!")
                            
                            # Rate limiting
                            time.sleep(3)
                        except Exception as e:
                            print(f"  [ERROR] Failed to update: {e}")
                            failed_posts.append({'id': post_id, 'title': title, 'error': str(e)})
                    else:
                        print(f"  [FAILED] Could not find image from source")
                        failed_posts.append({'id': post_id, 'title': title, 'source': source_link, 'error': 'No image found'})
                else:
                    print(f"  [NO SOURCE] No source link found in post")
                    failed_posts.append({'id': post_id, 'title': title, 'error': 'No source link'})
            
            page_token = resp.get('nextPageToken')
            if not page_token:
                break
                
        except Exception as e:
            print(f"\n[ERROR] {e}")
            break
    
    # Summary
    print("\n" + "=" * 60)
    print(f"  SUMMARY")
    print(f"  Total posts scanned: {total_count}")
    print(f"  Posts without images: {no_image_count}")
    print(f"  Posts fixed: {fixed_count}")
    print(f"  Posts still need fixing: {len(failed_posts)}")
    print("=" * 60)
    
    if failed_posts:
        print("\n  Posts that still need attention:")
        for fp in failed_posts:
            safe_title = fp['title'][:50].encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
            print(f"  - [{fp['id']}] {safe_title} => {fp.get('error', 'Unknown')}")


if __name__ == '__main__':
    fix_missing_images()
