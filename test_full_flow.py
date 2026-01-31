
from blogger_poster import BloggerPoster
from news_fetcher import NewsFetcher
from ai_processor import AIProcessor
import sys

# Fix encoding
def manual_post_full_test():
    print("🚀 Starting Full Integration Test...")
    
    # 1. Init Components
    fetcher = NewsFetcher()
    ai = AIProcessor()
    poster = BloggerPoster()
    
    # 2. Mock a news item (Radio Farda Style)
    mock_item = {
        'id': 'test_manual_001',
        'title': 'خبر فوری: تست نهایی سیستم هوشمند خبری',
        'link': 'https://google.com',
        'description': 'این یک خبر آزمایشی است تا ببینیم آیا عکس و HTML به درستی در قالب جدید سایت نمایش داده می‌شود یا خیر.',
        'image_url': 'https://gdb.rferl.org/086c0000-0aff-0242-4f36-08dc6eb21c7d_cx0_cy10_cw100_w1023_r1_s.jpg', # Actual Radio Farda image
        'source': 'تست سیستم',
        'language': 'fa'
    }
    
    print("🤖 Processing with AI...")
    processed = ai.process_news(mock_item)
    html_content = ai.generate_blog_html(processed)
    
    print("📝 Publishing to Blogger...")
    result = poster.create_post(
        title=processed.get('processed_title', mock_item['title']),
        content=html_content,
        labels=['تست سیستم', 'خبر فوری'],
        is_draft=False # Publish immediately
    )
    
    if result:
        print(f"✅ SUCCESS! Post published at: {result.get('url')}")
    else:
        print("❌ Failed to publish.")

if __name__ == "__main__":
    manual_post_full_test()
