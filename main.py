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
        
        for item in news_items:
            try:
                print(f"\n📄 Processing: {item['title'][:50]}...")
                
                # Process with AI
                if self.ai:
                    processed_item = self.ai.process_news(item)
                    html_content = self.ai.generate_blog_html(processed_item)
                else:
                    processed_item = item
                    html_content = f"<p>{item['description']}</p>"
                
                # Create draft in Blogger
                blogger_post_id = None
                if self.blogger:
                    post_result = self.blogger.create_post(
                        title=processed_item.get('processed_title', item['title']),
                        content=html_content,
                        labels=processed_item.get('tags', ['ایران', 'اخبار']),
                        is_draft=True  # Always create as draft first
                    )
                    if post_result:
                        blogger_post_id = post_result['id']
                        processed_item['blog_id'] = BLOG_ID
                
                # Send to Telegram for review
                if self.telegram:
                    self.telegram.send_for_review(processed_item, blogger_post_id)
                else:
                    print("⚠️ Telegram review disabled - drafts created in Blogger")
                
                # Mark as seen
                self.fetcher.mark_as_seen(item['id'])
                processed_count += 1
                
                # Small delay between items
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error processing item: {e}")
                continue
        
        print(f"\n✅ Processed {processed_count} news items")
        
        # Send summary to Telegram
        if self.telegram:
            self.telegram.send_notification(
                f"📊 <b>خلاصه عملکرد</b>\n\n"
                f"📰 اخبار دریافت شده: {len(news_items)}\n"
                f"✅ پردازش شده: {processed_count}\n"
                f"⏰ زمان: {datetime.now().strftime('%H:%M')}"
            )
    
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
