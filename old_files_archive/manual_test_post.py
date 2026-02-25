
import os
import pickle
import sys
from googleapiclient.discovery import build
from config import BLOG_ID

# Force UTF-8 for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def get_blogger_service():
    if not os.path.exists('token_auth_fixed.pickle'):
        return None
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    return build('blogger', 'v3', credentials=creds)

def create_test_post():
    service = get_blogger_service()
    if not service: return

    title = "تیتر آزمایشی: بازگشت تصاویر به خبرگزاری ایران پول"
    image_url = "https://images.unsplash.com/photo-1575936123452-b67c3203c357?q=80&w=1000&auto=format&fit=crop"
    
    html_content = f"""
    <!-- FORCE HIDE BLOGGER DEFAULT THUMBNAILS -->
    <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
    
    <!-- MAIN IMAGE CONTAINER -->
    <div style="margin-bottom:20px;text-align:center;">
        <img src="{image_url}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.3);border:1px solid #333;" alt="Test Image">
    </div>
    
    <!-- TEXT CONTENT -->
    <div style="font-size:17px;line-height:2.1;color:inherit;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
        <p>این یک پست آزمایشی برای بررسی نمایش صحیح تصاویر در قالب جدید تاریک (Dark Mode) است. اگر این تصویر را می‌بینید، یعنی مشکل فنی برطرف شده است.</p>
        <p>خبرگزاری ایران پول متعهد به انتشار اخبار دقیق و شفاف است.</p>
    </div>
    
    <!-- SOURCE BOX -->
    <div style="margin-top:40px;padding:20px;background:rgba(255,255,255,0.05);border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;display:flex;align-items:center;justify-content:flex-end;">
        <p style="margin:0;font-size:14px;color:#aaa;">
            <span style="opacity:0.7;">منبع:</span> 
            <span style="color:#ce0000;font-weight:bold;margin-right:8px;">تیم فنی ایران پول</span>
        </p>
    </div>
    """
    
    body = {
        'title': title,
        'content': html_content,
        'labels': ['Test', 'System Check']
    }
    
    try:
        print("Creating test post...")
        posts = service.posts().insert(blogId=BLOG_ID, body=body).execute()
        print(f"Created Post: {posts.get('url')}")
        print("PLEASE CHECK THE BLOG NOW.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    create_test_post()
