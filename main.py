
import os
import sys
import time
import schedule
from datetime import datetime, timedelta
from typing import List, Dict

from config import (
    BLOG_ID, 
    MAX_NEWS_PER_CHECK, 
    CHECK_INTERVAL_HOURS
)
from news_fetcher import NewsFetcher
from ai_processor import AIProcessor
from blogger_poster import BloggerPoster
from telegram_reviewer import TelegramReviewer

class BloggerNewsBot:
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.ai = None
        self.blogger = None
        self.telegram = None
        self.use_telegram_review = False # Manually disabled as it's not in config
        
        print("[INFO] Initializing Blogger News Bot...")
        print(f"[INFO] Blog ID: {BLOG_ID}")
        print(f"[INFO] Check interval: Every {CHECK_INTERVAL_HOURS} hours")
        print(f"[INFO] Telegram review: {'Enabled' if self.use_telegram_review else 'Disabled'}")

    def _init_ai(self):
        if not self.ai:
            self.ai = AIProcessor()
            print("[OK] AI Processor initialized")

    def _init_blogger(self):
        if not self.blogger:
            try:
                self.blogger = BloggerPoster()
                print("[OK] Blogger API initialized")
            except Exception as e:
                print(f"[ERROR] Blogger initialization failed: {e}")

    def _init_telegram(self):
        if self.use_telegram_review and not self.telegram:
            try:
                self.telegram = TelegramReviewer()
                print("[OK] Telegram Reviewer initialized")
            except Exception as e:
                print(f"[ERROR] Telegram initialization failed: {e}")

    def fetch_and_process_news(self):
        print("\n" + "="*60)
        print(f"Starting news fetch at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        news_items = self.fetcher.fetch_all_news(max_items=MAX_NEWS_PER_CHECK)
        
        if not news_items:
            print("[INFO] No new relevant news found")
            return
        
        self._init_ai()
        self._init_blogger()
        self._init_telegram()
        
        published_count = 0
        posted_titles = []
        
        for item in news_items:
            try:
                # 1. TIME FILTER: Skip older than 24h
                pub_date_str = item.get('published')
                if pub_date_str:
                    try:
                        pub_date = datetime.fromisoformat(pub_date_str)
                        if datetime.now() - pub_date > timedelta(hours=24):
                            print(f"  [Skip] News too old ({pub_date.strftime('%Y-%m-%d')}): {item['title'][:50]}")
                            continue
                    except:
                        pass
                
                # 2. DUPLICATE CHECK
                if self.fetcher.is_duplicate(item['title'], item['id']):
                    continue

                safe_title = item['title'][:50].encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                print(f"\nProcessing: {safe_title}...")
                
                # Prepare content
                article_link = item.get('link', '')
                article_title = item['title']
                
                print(f"  [Fetching] Getting full content...")
                full_article = self.fetcher.fetch_full_article(article_link, item.get('source', ''))
                
                description = full_article['full_content'] if full_article['success'] else item.get('description', '')
                main_image = full_article.get('main_image') or item.get('image_url', '')

                # Build HTML
                image_html = f'<div style="margin-bottom:25px;"><img src="{main_image}" style="width:100%;max-width:700px;border-radius:8px;"></div>' if main_image else ""
                html_content = f"""
                <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
                {image_html}
                <div style="font-size:16px;line-height:2.2;color:#333;">{description}</div>
                <div style="margin-top:30px;padding:15px;background:#f9f9f9;border-right:4px solid #ce0000;">
                    <p style="margin:0;font-size:13px;">Source: <a href="{article_link}" target="_blank" style="color:#ce0000;">{item.get('source', 'Source')}</a></p>
                </div>
                """

                # 3. PUBLISH
                if self.blogger:
                    post_result = self.blogger.create_post(
                        title=article_title,
                        content=html_content,
                        labels=[item.get('source_category', 'News'), 'Iran'],
                        is_draft=False
                    )
                    if post_result:
                        print(f"[OK] Published: {post_result.get('url')}")
                        published_count += 1
                        self.fetcher.mark_as_seen(article_title, item['id'])
                        
                        # 4. ANTI-429 DELAY
                        print("  [Wait] 20s delay to avoid Blogger rate limits...")
                        time.sleep(20)
                    else:
                        print(f"[FAILED] Could not post to Blogger")
                
            except Exception as e:
                print(f"[ERROR] Processing item: {e}")

        print(f"\nFinished. Published {published_count} items.")

    def run_once(self):
        self.fetch_and_process_news()

def main():
    bot = BloggerNewsBot()
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        bot.run_once()
    else:
        bot.run_once() # For now run once as default

if __name__ == "__main__":
    import sys
    main()
