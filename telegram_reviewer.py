"""
Telegram Reviewer Module
ماژول بررسی و تأیید اخبار از طریق تلگرام
"""

import json
import requests
from typing import Dict, List, Optional, Callable
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID


class TelegramReviewer:
    """
    Sends news to Telegram for admin review
    Admin can approve or reject via inline buttons
    """
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.admin_chat_id = TELEGRAM_ADMIN_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.pending_reviews = {}  # Store pending news items
        self.pending_file = "pending_reviews.json"
        self._load_pending()
    
    def _load_pending(self):
        """Load pending reviews from file"""
        try:
            with open(self.pending_file, 'r', encoding='utf-8') as f:
                self.pending_reviews = json.load(f)
        except:
            self.pending_reviews = {}
    
    def _save_pending(self):
        """Save pending reviews to file"""
        with open(self.pending_file, 'w', encoding='utf-8') as f:
            json.dump(self.pending_reviews, f, ensure_ascii=False, indent=2)
    
    def _send_request(self, method: str, data: dict) -> Optional[Dict]:
        """Send request to Telegram API"""
        try:
            # For long polling (getUpdates), the requests timeout should be 
            # slightly longer than the API timeout to avoid "Read timed out" noise.
            req_timeout = 45 if method == 'getUpdates' else 30
            
            response = requests.post(
                f"{self.base_url}/{method}",
                json=data,
                timeout=req_timeout
            )
            result = response.json()
            
            if not result.get('ok'):
                print(f"❌ Telegram API error: {result.get('description')}")
                return None
            
            return result.get('result')
            
        except requests.exceptions.ReadTimeout:
            # This is normal for long polling, just return empty list or None
            return [] if method == 'getUpdates' else None
        except Exception as e:
            print(f"❌ Telegram request error: {e}")
            return None
    
    def send_for_review(self, news_item: Dict, blogger_post_id: str = None) -> bool:
        """
        Send news item to Telegram for admin review
        
        Args:
            news_item: Processed news item
            blogger_post_id: ID of the draft post in Blogger
        """
        title = news_item.get('processed_title', news_item.get('title', ''))
        content = news_item.get('processed_content', news_item.get('description', ''))
        source = news_item.get('source', '')
        link = news_item.get('link', '')
        image_url = news_item.get('image_url', '')
        tags = news_item.get('tags', [])
        news_id = news_item.get('id', '')
        
        # Create message text
        message = f"""
📰 <b>خبر جدید برای بررسی</b>

<b>عنوان:</b> {title}

<b>خلاصه:</b>
{content[:500]}{'...' if len(content) > 500 else ''}

<b>منبع:</b> {source}
<b>تگ‌ها:</b> {', '.join(tags) if tags else '-'}

🔗 <a href="{link}">لینک اصلی</a>
"""
        
        # Create inline keyboard for approve/reject
        callback_approve = f"approve_{news_id}"
        callback_reject = f"reject_{news_id}"
        
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "✅ تأیید و انتشار", "callback_data": callback_approve},
                    {"text": "❌ رد کردن", "callback_data": callback_reject}
                ],
                [
                    {"text": "✏️ ویرایش در Blogger", "url": f"https://www.blogger.com/blog/post/edit/{news_item.get('blog_id', '')}/{blogger_post_id}" if blogger_post_id else link}
                ]
            ]
        }
        
        # Send image if available
        if image_url:
            result = self._send_request('sendPhoto', {
                'chat_id': self.admin_chat_id,
                'photo': image_url,
                'caption': message[:1024],  # Telegram caption limit
                'parse_mode': 'HTML',
                'reply_markup': keyboard
            })
        else:
            result = self._send_request('sendMessage', {
                'chat_id': self.admin_chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'reply_markup': keyboard,
                'disable_web_page_preview': False
            })
        
        if result:
            # Store pending review
            self.pending_reviews[news_id] = {
                'news_item': news_item,
                'blogger_post_id': blogger_post_id,
                'message_id': result.get('message_id'),
                'status': 'pending'
            }
            self._save_pending()
            print(f"📤 Sent for review: {title[:50]}...")
            return True
        
        return False
    
    def get_updates(self, offset: int = None) -> List[Dict]:
        """Get updates from Telegram (callback queries)"""
        data = {'timeout': 30}
        if offset:
            data['offset'] = offset
        
        result = self._send_request('getUpdates', data)
        return result if result else []
    
    def process_callback(self, callback_query: Dict) -> tuple[str, str]:
        """
        Process callback query from inline button
        
        Returns:
            (action, news_id) - action is 'approve' or 'reject'
        """
        callback_data = callback_query.get('data', '')
        
        if callback_data.startswith('approve_'):
            return 'approve', callback_data.replace('approve_', '')
        elif callback_data.startswith('reject_'):
            return 'reject', callback_data.replace('reject_', '')
        
        return None, None
    
    def answer_callback(self, callback_query_id: str, text: str):
        """Answer callback query with notification"""
        self._send_request('answerCallbackQuery', {
            'callback_query_id': callback_query_id,
            'text': text,
            'show_alert': True
        })
    
    def update_message(self, chat_id: int, message_id: int, new_text: str):
        """Update message after decision"""
        self._send_request('editMessageText', {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': new_text,
            'parse_mode': 'HTML'
        })
    
    def send_notification(self, message: str):
        """Send notification message to admin"""
        self._send_request('sendMessage', {
            'chat_id': self.admin_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        })
    
    def get_pending_review(self, news_id: str) -> Optional[Dict]:
        """Get pending review by news ID"""
        return self.pending_reviews.get(news_id)
    
    def mark_reviewed(self, news_id: str, status: str):
        """Mark news as reviewed"""
        if news_id in self.pending_reviews:
            self.pending_reviews[news_id]['status'] = status
            self._save_pending()


# Test the reviewer
if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        print("⚠️ Telegram credentials not set")
        print("\nTo set up Telegram bot:")
        print("1. Message @BotFather on Telegram")
        print("2. Create a new bot with /newbot")
        print("3. Copy the bot token to .env")
        print("4. Get your chat ID from @userinfobot")
        print("5. Add chat ID to .env")
    else:
        reviewer = TelegramReviewer()
        
        # Test sending a notification
        reviewer.send_notification("🤖 ربات بررسی اخبار فعال شد!")
        print("✅ Test notification sent")
