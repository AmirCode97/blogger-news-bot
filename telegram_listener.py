"""
Telegram Listener - Waits for approval and publishes to Blogger
این اسکریپت منتظر تایید شما در تلگرام می‌ماند و بعد از تایید، خبر را منتشر می‌کند
"""

import json
import time
from telegram_reviewer import TelegramReviewer
from blogger_poster import BloggerPoster
from config import BLOG_ID

def main():
    print("🤖 Telegram Approval Listener Started")
    print("=" * 50)
    print("منتظر تایید شما در تلگرام هستم...")
    print("وقتی دکمه ✅ تأیید و انتشار را بزنید، خبر منتشر می‌شود")
    print("=" * 50)
    
    reviewer = TelegramReviewer()
    blogger = None
    
    last_update_id = 0
    
    while True:
        try:
            # Get updates from Telegram
            updates = reviewer.get_updates(offset=last_update_id + 1 if last_update_id else None)
            
            for update in updates:
                last_update_id = update.get('update_id', 0)
                
                # Check for callback query (button press)
                callback = update.get('callback_query')
                if callback:
                    action, news_id = reviewer.process_callback(callback)
                    
                    if action == 'approve':
                        print(f"\n✅ تایید دریافت شد برای خبر: {news_id}")
                        
                        # Get pending review data
                        pending = reviewer.get_pending_review(news_id)
                        if pending:
                            news_item = pending.get('news_item', {})
                            html_content = news_item.get('html_content', '')
                            title = news_item.get('processed_title', news_item.get('title', ''))
                            tags = news_item.get('tags', ['ایران', 'اخبار'])
                            
                            # Initialize Blogger if not done
                            if blogger is None:
                                print("🔐 Connecting to Blogger...")
                                blogger = BloggerPoster()
                            
                            # Publish to Blogger
                            print(f"📝 Publishing to Blogger: {title[:50]}...")
                            result = blogger.create_post(
                                title=title,
                                content=html_content,
                                labels=tags,
                                is_draft=False  # Publish immediately
                            )
                            
                            if result:
                                post_url = result.get('url', '')
                                print(f"✅ Published! URL: {post_url}")
                                
                                # Answer callback and update message
                                reviewer.answer_callback(
                                    callback.get('id'),
                                    "✅ خبر با موفقیت منتشر شد!"
                                )
                                
                                # Send confirmation with link
                                reviewer.send_notification(
                                    f"✅ خبر منتشر شد!\n\n🔗 <a href=\"{post_url}\">مشاهده در وبلاگ</a>"
                                )
                                
                                reviewer.mark_reviewed(news_id, 'approved')
                            else:
                                reviewer.answer_callback(
                                    callback.get('id'),
                                    "❌ خطا در انتشار! لطفاً دوباره تلاش کنید"
                                )
                        else:
                            reviewer.answer_callback(
                                callback.get('id'),
                                "❌ خبر پیدا نشد"
                            )
                    
                    elif action == 'reject':
                        print(f"\n❌ خبر رد شد: {news_id}")
                        reviewer.answer_callback(
                            callback.get('id'),
                            "❌ خبر رد شد"
                        )
                        reviewer.mark_reviewed(news_id, 'rejected')
            
            # Small delay to avoid hitting API limits
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
