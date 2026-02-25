"""
Script to update old blog posts with new styling:
- White text color (#fff)
- Premium source box with red button
- Preserves original content and images
"""
import os
import sys
import pickle
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

def get_blogger_service():
    if not os.path.exists('token_auth_fixed.pickle'):
        print("❌ No credentials found.")
        return None
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    return build('blogger', 'v3', credentials=creds)

def fix_post_styling(content, source_url=""):
    """Fix the styling of post content to use white text and premium source box."""
    
    # Extract source name from the existing content if possible
    source_match = re.search(r'مشاهده در ([^<]+)</a>', content)
    source_name = source_match.group(1) if source_match else "منبع"
    
    # Extract source URL from existing content
    url_match = re.search(r'href="([^"]+)"[^>]*>مشاهده', content)
    if url_match:
        source_url = url_match.group(1)
    
    # Fix text colors: Replace grey/dark colors with white
    content = re.sub(r'color:\s*#eee', 'color:#fff', content)
    content = re.sub(r'color:\s*#ddd', 'color:#fff', content)
    content = re.sub(r'color:\s*#ccc', 'color:#fff', content)
    content = re.sub(r'color:\s*#bbb', 'color:#fff', content)
    content = re.sub(r'color:\s*#333', 'color:#fff', content)
    content = re.sub(r'color:\s*#444', 'color:#fff', content)
    
    # Check if already has premium source box (has the red button style)
    if 'background:#ce0000;color:#fff;padding:10px 20px' in content:
        # Already has premium styling, just fix colors
        return content
    
    # Check for old source box patterns and replace with new premium box
    old_patterns = [
        r'<!-- Classic Light Source Box -->.*?</div>\s*</div>',
        r'<!-- White Source Box.*?</div>\s*</div>',
        r'<!-- Premium Source Box.*?</div>\s*</div>',
        r'<div[^>]*منبع[^>]*>.*?</div>\s*</div>',
    ]
    
    new_source_box = f'''
    <!-- Premium Source Box -->
    <div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;display:flex;align-items:center;justify-content:flex-end;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
        <p style="margin:0;font-size:14px;color:#888;font-family:'Vazir',sans-serif;display:flex;align-items:center;">
            <span style="opacity:0.8;margin-left:15px;">منبع خبر:</span> 
            <a href="{source_url}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);transition:0.3s;">مشاهده در {source_name}</a>
        </p>
    </div>
    '''
    
    for pattern in old_patterns:
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            content = re.sub(pattern, new_source_box, content, flags=re.DOTALL | re.IGNORECASE)
            break
    
    return content

def update_old_posts(max_posts=50):
    service = get_blogger_service()
    if not service:
        return
    
    print(f"📝 Fetching last {max_posts} posts to update styling...")
    
    try:
        posts = service.posts().list(blogId=BLOG_ID, maxResults=max_posts).execute().get('items', [])
        
        updated = 0
        for post in posts:
            title = post.get('title', 'Untitled')
            content = post.get('content', '')
            post_id = post['id']
            
            # Fix the styling
            new_content = fix_post_styling(content)
            
            # Check if any changes were made
            if new_content != content:
                print(f"  🔄 Updating: {title[:60]}...")
                
                body = {
                    "content": new_content
                }
                
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=post_id,
                    body=body
                ).execute()
                
                updated += 1
            else:
                print(f"  ✓ Already correct: {title[:60]}")
        
        print(f"\n✅ Updated {updated} posts with new styling.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_old_posts()
