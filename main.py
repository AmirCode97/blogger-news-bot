
import os
import sys
import re
import time
import schedule
from datetime import datetime

def deduplicate_text(text):
    """Detect and remove duplicated text content.
    If the text contains the same content repeated twice, keep only the first occurrence."""
    if not text or len(text) < 50:
        return text
    
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    unique_paragraphs = []
    seen = set()
    
    for p in paragraphs:
        # Simplify paragraph for comparison
        clean_p = re.sub(r'[^\w\s]', '', p).strip()
        words = clean_p.split()
        
        # We need at least 5 words to consider it a deduplicable sentence
        if len(words) < 5:
            unique_paragraphs.append(p)
            continue
            
        fingerprint = " ".join(words[:40]) # check up to 40 words
        
        if fingerprint not in seen:
            seen.add(fingerprint)
            unique_paragraphs.append(p)
        else:
            print(f"  [Dedup] Removed duplicated paragraph: len={len(p)}")

    return "\n\n".join(unique_paragraphs)

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
from duplicate_detector import DuplicateDetector

class BloggerNewsBot:
    def __init__(self):
        self.fetcher = NewsFetcher()
        self.duplicate_detector = DuplicateDetector()  # Advanced duplicate detection
        self.ai = None
        self.blogger = None
        self.telegram = None
        self.use_telegram_review = False
        
        print("[INFO] Initializing Blogger News Bot...")
        print(f"[INFO] Blog ID: {BLOG_ID}")
        print(f"[INFO] Check interval: Every {CHECK_INTERVAL_HOURS} hours")
        print(f"[INFO] Duplicate cache: {self.duplicate_detector.get_stats()}")

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
                
                # 2. ADVANCED DUPLICATE CHECK
                is_dup, dup_reason = self.duplicate_detector.is_duplicate(
                    item['title'], 
                    item.get('link', ''),
                    item.get('description', '')
                )
                if is_dup:
                    safe_title = item['title'][:40].encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                    print(f"  [SKIP] Duplicate: {safe_title}... ({dup_reason})")
                    continue

                safe_title = item['title'][:50].encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                print(f"\nProcessing: {safe_title}...")
                
                # Prepare content
                article_link = item.get('link', '')
                article_title = item['title']
                
                print(f"  [Fetching] Getting full content...")
                full_article = self.fetcher.fetch_full_article(article_link, item.get('source', ''))
                
                # Get content from article or fallback to item description
                description = full_article.get('full_content', '') if full_article.get('success') else ''
                if not description:
                    description = item.get('description', '')
                
                main_image = full_article.get('main_image') or item.get('image_url', '')
                
                # If still no content, use AI to GENERATE content from title
                if not description or len(description) < 50:
                    print(f"  [Warning] No content found, asking AI to generate from title...")
                    description = f"[این خبر نیاز به تحلیل دارد: {article_title}]"

                # Call AI for Multi-language processing
                # This also fixes content if it was minimal
                if self.ai:
                    print(f"  [AI] Paraphrasing and generating unique title...")
                    processed_title, ai_response = self.ai.process_news(article_title, description)
                    
                    # Update title to the unique one generated by AI
                    article_title = processed_title
                    
                    # Parse AI response
                    # Parse AI response - Persian only (no translations)
                    final_fa = description # Fallback
                    
                    if "===PERSIAN===" in ai_response:
                        try:
                            persian_part = ai_response.split("===PERSIAN===")[1]
                            # Remove TAGS or any other sections if present
                            for marker in ["===TAGS===", "===ENGLISH===", "===GERMAN==="]:
                                if marker in persian_part:
                                    persian_part = persian_part.split(marker)[0]
                            final_fa = persian_part.strip()
                        except:
                            pass
                    elif len(ai_response) > 100: 
                        # If AI failed to structure but returned long text, use it
                        final_fa = ai_response

                    description = final_fa
                else:
                    pass

                # VALIDATE: Skip if no content was extracted
                if not description or len(description) < 50:
                    print(f"  [SKIP] No content extracted for this article")
                    continue
                
                # DEDUPLICATION CHECK: Remove any repeated text content
                description = deduplicate_text(description)
                
                print(f"  [Content] {len(description)} characters")
                
                # Build HTML compatible with Dark Theme (White Text) + White Source Box
                image_html = ""
                if main_image:
                    print(f"  [Image] {main_image[:60]}...")
                    image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{main_image}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);"></div>'
                else:
                    print(f"  [Warning] No image found for this article")
                
                source_name = item.get('source', 'Source')
                
                # No jump break (<!--more-->) used anymore. Posts are short enough to display fully.
                description_with_break = description

                # HTML Structure - Persian only
                html_content = f"""
                <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
                {image_html}
                
                <!-- Persian Section -->
                <div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
                    {description_with_break}
                </div>
                
                <!-- Source Box -->
                <div style="text-align: right; direction: rtl;">
                    <div style="background:#1a1a1a; padding:12px 25px; border-radius:8px; border-right:3px solid #c0392b; font-weight:bold; color:#ddd; display:inline-block; margin:30px 0 10px 0; font-size: 13px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);">
                        <span style="color:#c0392b; margin-left:8px;">خبرگزاری:</span> iranpolnews
                    </div>
                </div>
                """

                # 3. PUBLISH
                if self.blogger:
                    # Smart label classification
                    post_labels = []
                    search_text = (article_title + " " + description).lower()
                    
                    # Keywords for specific categories
                    worker_keywords = ['کارگر', 'کارگران', 'اعتصاب', 'حقوق معوقه', 'سندیکا', 'کولبر', 'سوخت‌بر', 'اخراج', 'بازنشستگان', 'حداقل دستمزد', 'حوادث کار']
                    prisoner_keywords = ['زندان', 'بازداشت', 'اوین', 'اعدام', 'حبس', 'وثیقه', 'سلول انفرادی', 'اعتصاب غذا', 'شکنجه', 'بند نسوان', 'زندانی سیاسی']
                    
                    # 1. Check for Workers news
                    if any(kw in search_text for kw in worker_keywords):
                        post_labels.append('کارگران')
                    # 2. Check for Prisoners news
                    elif any(kw in search_text for kw in prisoner_keywords):
                        post_labels.append('وضعیت زندانیان')
                    # 3. Default for Iran International is International
                    elif 'ایران اینترنشنال' in source_name:
                        post_labels.append('بین‌الملل')
                    # 4. Default for Human Rights sources
                    else:
                        post_labels.append('حقوق بشر')
                        

                        
                    # Ensure uniqueness
                    post_labels = list(set(post_labels))
                    
                    post_result = self.blogger.create_post(
                        title=article_title,
                        content=html_content,
                        labels=post_labels,
                        is_draft=False
                    )
                    if post_result:
                        print(f"[OK] Published: {post_result.get('url')}")
                        published_count += 1
                        
                        # Mark as published in BOTH systems
                        self.fetcher.mark_as_seen(article_title, item['id'])
                        self.duplicate_detector.mark_as_published(
                            title=article_title,
                            url=article_link,
                            content=description,
                            post_id=post_result.get('id', '')
                        )
                        
                        # 4. ANTI-429 DELAY
                        print("  [Wait] 20s delay to avoid Blogger rate limits...")
                        time.sleep(20)
                    else:
                        print(f"[FAILED] Could not post to Blogger")
                
            except Exception as e:
                print(f"[ERROR] Processing item: {e}")

        print(f"\nFinished. Published {published_count} items.")
        
        # Finally, update the live statistics
        try:
            from stats_updater import fetch_and_calculate_stats, update_stats_post
            print("\n[INFO] Running Live Stats Engine...")
            stats_data = fetch_and_calculate_stats()
            if stats_data and self.blogger:
                update_stats_post(self.blogger, stats_data)
        except Exception as e:
            print(f"[Error] Failed to update stats: {e}")

    def run_once(self):
        self.fetch_and_process_news()

    def run_scheduler(self):
        print(f"[SCHEDULER] Bot started. Checking news every {CHECK_INTERVAL_HOURS} hours.")
        
        # Run immediately on start
        self.fetch_and_process_news()
        
        # Schedule next runs
        schedule.every(CHECK_INTERVAL_HOURS).hours.do(self.fetch_and_process_news)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

def main():
    bot = BloggerNewsBot()
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        bot.run_once()
    else:
        # Default mode: Continuous Loop
        bot.run_scheduler()

if __name__ == "__main__":
    import sys
    main()
