"""
Blogger News Bot - Main Script
ربات اصلی دریافت و ارسال اخبار به وبلاگ
"""

import time
import schedule
from datetime import datetime
from typing import Dict, List

from config import (
    BLOG_ID, CHECK_INTERVAL_HOURS, MAX_NEWS_PER_CHECK,
    TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID
)
from news_fetcher import NewsFetcher
from ai_processor import AIProcessor
from blogger_poster import BloggerPoster
from telegram_reviewer import TelegramReviewer


class BloggerNewsBot:
    """
    Main bot that orchestrates:
    1. Fetching news from sources
    2. Processing with AI
    3. Creating drafts in Blogger
    4. Sending to Telegram for review
    5. Publishing approved posts
    """
    
    def __init__(self):
        print("🚀 Initializing Blogger News Bot...")
        
        self.fetcher = NewsFetcher()
        self.ai = None  # Lazy load when needed
        self.blogger = None  # Lazy load when needed
        self.telegram = None  # Lazy load when needed
        
        self.use_telegram_review = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID)
        
        print(f"📌 Blog ID: {BLOG_ID}")
        print(f"⏰ Check interval: Every {CHECK_INTERVAL_HOURS} hours")
        print(f"📱 Telegram review: {'Enabled' if self.use_telegram_review else 'Disabled'}")
    
    def _init_ai(self):
        """Initialize AI processor"""
        if not self.ai:
            try:
                self.ai = AIProcessor()
                print("✅ AI Processor initialized")
            except Exception as e:
                print(f"⚠️ AI initialization failed: {e}")
    
    def _init_blogger(self):
        """Initialize Blogger poster"""
        if not self.blogger:
            try:
                self.blogger = BloggerPoster()
                print("✅ Blogger API initialized")
            except Exception as e:
                print(f"⚠️ Blogger initialization failed: {e}")
    
    def _init_telegram(self):
        """Initialize Telegram reviewer"""
        if not self.telegram and self.use_telegram_review:
            try:
                self.telegram = TelegramReviewer()
                print("✅ Telegram Reviewer initialized")
            except Exception as e:
                print(f"⚠️ Telegram initialization failed: {e}")
    
    def fetch_and_process_news(self):
        """Main job: fetch, process, and queue news for review"""
        print(f"\n{'='*60}")
        print(f"📰 Starting news fetch at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*60)
        
        # Fetch news
        news_items = self.fetcher.fetch_all_news(max_items=MAX_NEWS_PER_CHECK)
        
        if not news_items:
            print("ℹ️ No new relevant news found")
            return
        
        # Initialize components
        self._init_ai()
        self._init_blogger()
        self._init_telegram()
        
        processed_count = 0
        published_count = 0
        posted_titles = []  # Track posted news titles
        failed_titles = []  # Track failed posts
        
        for item in news_items:
            try:
                print(f"\n📄 Processing: {item['title'][:50]}...")
                
                # Get category from source (default to حقوق بشر)
                source_category = item.get('source_category', 'حقوق بشر')
                default_tags = [source_category, 'ایران', 'اخبار']
                
                article_link = item.get('link', '')
                article_title = item.get('title', '')
                
                # تشخیص liveblog با anchor (#)
                is_liveblog_anchor = '#' in article_link
                
                # برای همه اخبار (غیر از liveblog با #) محتوای کامل را بگیر
                description = ""
                main_image = item.get('image_url', '')  # عکس از scrape اولیه
                
                if is_liveblog_anchor:
                    # Liveblog با anchor - از description استفاده کن
                    print(f"  [Liveblog#] Using description")
                    description = item.get('description', article_title)
                else:
                    # خبر معمولی - محتوای کامل را بگیر
                    print(f"  [Fetching] Getting full article content...")
                    full_article = self.fetcher.fetch_full_article(article_link, item.get('source', ''))
                    
                    if full_article['success'] and full_article['full_content']:
                        description = full_article['full_content']
                        # عکس اصلی از مقاله (og:image)
                        if full_article.get('main_image'):
                            main_image = full_article['main_image']
                        print(f"  ✓ Got full content, Image: {'Yes' if main_image else 'No'}")
                    else:
                        # Fallback به description
                        description = item.get('description', article_title)
                        print(f"  ⚠ Using fallback description")
                
                # ساخت HTML تمیز - با عکس اصلی
                image_html = ""
                if main_image:
                    image_html = f'''
                    <div style="margin-bottom: 25px;">
                        <img src="{main_image}" alt="{article_title}" style="width: 100%; max-width: 700px; border-radius: 8px; display: block;">
                    </div>
                    '''
                
                html_content = f'''
                <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
                {image_html}
                <div style="font-size: 16px; line-height: 2.2; color: #ddd;">
                    {description}
                </div>
                <div style="margin-top: 30px; padding: 15px; background: #222; border-right: 4px solid #c0392b; border-radius: 4px;">
                    <p style="margin: 0; font-size: 13px; color: #888;">
                        📰 منبع: <a href="{article_link}" target="_blank" style="color: #c0392b;">{item.get('source', 'منبع خبر')}</a>
                    </p>
                </div>
                '''
                
                # Get the title
                news_title = item['title']
                
                # AUTO-PUBLISH: Directly publish to Blogger
                if self.blogger:
                    post_result = self.blogger.create_post(
                        title=news_title,
                        content=html_content,
                        labels=default_tags,
                        is_draft=False  # Publish directly!
                    )
                    if post_result:
                        print(f"✅ Published: {post_result.get('url')}")
                        posted_titles.append(f"✅ {news_title[:50]}...")
                        published_count += 1
                        # Mark as seen ONLY if successful
                        self.fetcher.mark_as_seen(item['title'], item['id'])
                    else:
                        print(f"❌ Failed to publish: {news_title[:50]}")
                        failed_titles.append(f"❌ {news_title[:50]}...")
                else:
                    print(f"⚠️ Blogger not available - skipping publish")
                    failed_titles.append(f"⚠️ {news_title[:50]}...")
                
                processed_count += 1
                
                # Small delay between items
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing item: {e}")
                failed_titles.append(f"❌ Error: {str(e)[:30]}...")
                continue
        
        print(f"\n✅ Processed {processed_count} news items, Published {published_count}")
        
        # Send detailed summary to Telegram
        if self.telegram:
            success_list = "\n".join(posted_titles) if posted_titles else "هیچ خبری منتشر نشد"
            fail_list = "\n".join(failed_titles) if failed_titles else ""
            
            report = (
                f"📊 <b>گزارش اجرای ربات</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📰 اخبار دریافت شده: {len(news_items)}\n"
                f"✅ منتشر شده در وبلاگ: {published_count}\n"
                f"⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>📝 اخبار منتشر شده:</b>\n{success_list}"
            )
            
            if fail_list:
                report += f"\n\n<b>⚠️ خطاها:</b>\n{fail_list}"
            
            self.telegram.send_notification(report)
    
    def process_telegram_callbacks(self):
        """Process approve/reject callbacks from Telegram"""
        if not self.telegram:
            return
        
        self._init_blogger()
        
        offset = None
        updates = self.telegram.get_updates(offset)
        
        for update in updates:
            offset = update.get('update_id', 0) + 1
            
            callback_query = update.get('callback_query')
            if not callback_query:
                continue
            
            action, news_id = self.telegram.process_callback(callback_query)
            
            if not action or not news_id:
                continue
            
            pending = self.telegram.get_pending_review(news_id)
            if not pending:
                continue
            
            blogger_post_id = pending.get('blogger_post_id')
            news_title = pending.get('news_item', {}).get('processed_title', 'Unknown')
            
            if action == 'approve':
                # Publish the post
                if self.blogger and blogger_post_id:
                    success = self.blogger.publish_draft(blogger_post_id)
                    if success:
                        self.telegram.answer_callback(
                            callback_query['id'],
                            "✅ خبر منتشر شد!"
                        )
                        self.telegram.mark_reviewed(news_id, 'published')
                    else:
                        self.telegram.answer_callback(
                            callback_query['id'],
                            "❌ خطا در انتشار"
                        )
            
            elif action == 'reject':
                # Delete the draft
                if self.blogger and blogger_post_id:
                    self.blogger.delete_post(blogger_post_id)
                
                self.telegram.answer_callback(
                    callback_query['id'],
                    "🗑️ خبر رد شد"
                )
                self.telegram.mark_reviewed(news_id, 'rejected')
    
    def run_once(self):
        """Run the bot once (for testing)"""
        self.fetch_and_process_news()
    
    def run_scheduled(self):
        """Run the bot on schedule"""
        print(f"\n🤖 Bot started - Running every {CHECK_INTERVAL_HOURS} hours")
        print("Press Ctrl+C to stop\n")
        
        # Run immediately on start
        self.fetch_and_process_news()
        
        # Schedule regular runs
        schedule.every(CHECK_INTERVAL_HOURS).hours.do(self.fetch_and_process_news)
        
        # Check Telegram callbacks every minute
        if self.use_telegram_review:
            schedule.every(1).minutes.do(self.process_telegram_callbacks)
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(10)
            except KeyboardInterrupt:
                print("\n👋 Bot stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(60)  # Wait before retrying


def main():
    """Main entry point"""
    import sys
    
    bot = BloggerNewsBot()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once for testing
        bot.run_once()
    else:
        # Run on schedule
        bot.run_scheduled()


if __name__ == "__main__":
    main()
