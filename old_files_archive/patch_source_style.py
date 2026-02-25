
import os
import sys
import pickle
# Force UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from config import BLOG_ID

# Define styles
OLD_STYLE_MARKER = 'background:#f9f9f9;border-right:4px solid #ce0000;'
NEW_STYLE_HTML_START = '<div style="margin-top:30px;padding:15px 20px;background:#1a1a1a;border-right:4px solid #ce0000;border-radius:4px;text-align:right;direction:rtl;display:flex;align-items:center;justify-content:flex-end;">'

def get_blogger_service():
    creds = None
    if os.path.exists('token_auth_fixed.pickle'):
        with open('token_auth_fixed.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials found.")
            return None
            
    return build('blogger', 'v3', credentials=creds)

def update_posts():
    service = get_blogger_service()
    if not service:
        return

    print("Fetching last 20 posts...")
    try:
        posts_result = service.posts().list(blogId=BLOG_ID, maxResults=20).execute()
        posts = posts_result.get('items', [])
        
        if not posts:
            print("No posts found.")
            return

        for post in posts:
            content = post.get('content', '')
            title = post.get('title', '')
            
            # Check if post ALREADY has new style
            if 'background:#1a1a1a' in content:
                print(f"  [Skip] Already has new style: {title[:30]}...")
                continue
            
            print(f"Updating style for: {title[:30]}...")
            
            # Simple Logic: Remove old footer if present, append new footer
            # Old footer could be anything, so we look for the last </div>
            # BUT safer: Look for "Source:" or "منبع:" and replace that block
            
            import re
            # Try to find source name
            # Pattern: "Source: ... <a ...>(SOURCE_NAME)</a>" OR "منبع: ... (SOURCE_NAME)"
            source_btn_match = re.search(r'>([^<]+)</a></p>', content)
            source_name = source_btn_match.group(1) if source_btn_match else "News Source"
            
            # Allow fallback if source extraction failed
            if len(source_name) > 50: source_name = "News Source"

            # Remove old footer logic: 
            # We look for the last <div> which usually contains the source in our generator
            # A bit risky to remove blindly.
            # Let's try to find the specific old footer signature
            
            if 'Source:' in content:
                 # It's an English source box
                 content = re.sub(r'<div[^>]*background:[^>]*>.*?Source:.*?</div>', '', content, flags=re.DOTALL)
            elif 'منبع:' in content:
                 # It might be a Persian source box
                 content = re.sub(r'<div[^>]*>.*?منبع:.*?</div>', '', content, flags=re.DOTALL)
            
            # Just append the new footer
            new_footer = f"""
            <!-- Dark Mode Source Box -->
            <div style="margin-top:30px;padding:15px 20px;background:#1a1a1a;border-right:4px solid #ce0000;border-radius:4px;text-align:right;direction:rtl;display:flex;align-items:center;justify-content:flex-end;">
                <p style="margin:0;font-size:13px;color:#ccc;font-family:'Vazir',sans-serif;">
                    <span style="color:#888;">منبع:</span> 
                    <span style="color:#ce0000;font-weight:bold;margin-right:5px;">{source_name}</span>
                </p>
            </div>
            """
            
            new_content = content + new_footer
            
            post['content'] = new_content
            service.posts().update(blogId=BLOG_ID, postId=post['id'], body=post).execute()
            print("  [OK] Updated.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_posts()
