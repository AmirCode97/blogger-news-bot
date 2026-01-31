"""
AI Processor Module
ماژول پردازش اخبار با هوش مصنوعی Gemini
"""

import google.generativeai as genai
from typing import Dict, Optional
from config import GEMINI_API_KEY, AI_SYSTEM_PROMPT, AI_TRANSLATE_PROMPT


class AIProcessor:
    """Process news content using Gemini AI"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment")
        
        genai.configure(api_key=GEMINI_API_KEY)
        # Use verified available model: gemini-2.0-flash
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def process_news(self, news_item: Dict) -> Dict:
        """
        Process a news item:
        - Translate if English
        - Summarize and format for blog
        - Generate tags
        """
        title = news_item.get('title', '')
        description = news_item.get('description', '')
        language = news_item.get('language', 'fa')
        
        try:
            if language == 'en':
                # Translate and process English news
                processed = self._translate_and_process(title, description)
            else:
                # Process Persian news
                processed = self._process_persian(title, description)
            
            return {
                **news_item,
                'processed_title': processed.get('title', title),
                'processed_content': processed.get('content', description),
                'tags': processed.get('tags', []),
                'ai_processed': True
            }
            
        except Exception as e:
            print(f"❌ AI Processing error: {e}")
            return {
                **news_item,
                'processed_title': title,
                'processed_content': description,
                'tags': ['ایران', 'اخبار'],
                'ai_processed': False
            }
    
    def _translate_and_process(self, title: str, description: str) -> Dict:
        """Translate English news to Persian and format"""
        
        prompt = f"""
{AI_TRANSLATE_PROMPT}

عنوان انگلیسی: {title}
متن خبر: {description}

لطفاً خروجی را به این فرمت JSON بده. در متن (content) از تگ‌های HTML مثل <p>, <strong>, <ul> استفاده کن تا متن زیبا و خوانا شود:
{{
    "title": "عنوان فارسی جذاب",
    "content": "متن کامل خبر به فارسی با فرمت HTML (۲-۳ پاراگراف)",
    "tags": ["تگ۱", "تگ۲", "تگ۳"]
}}

فقط JSON خالص برگردان، بدون هیچ توضیح اضافی.
"""
        
        response = self.model.generate_content(prompt)
        return self._parse_ai_response(response.text)
    
    def _process_persian(self, title: str, description: str) -> Dict:
        """Process and enhance Persian news"""
        
        prompt = f"""
{AI_SYSTEM_PROMPT}

عنوان خبر: {title}
متن خبر: {description}

لطفاً خروجی را به این فرمت JSON بده. در متن (content) از تگ‌های HTML مثل <p>, <strong>, <ul> استفاده کن تا متن زیبا و خوانا شود:
{{
    "title": "عنوان بهبود یافته و جذاب",
    "content": "متن خبر به صورت روان و مناسب وبلاگ با فرمت HTML (۲-۳ پاراگراف)",
    "tags": ["تگ۱", "تگ۲", "تگ۳"]
}}

فقط JSON خالص برگردان، بدون هیچ توضیح اضافی.
"""
        
        response = self.model.generate_content(prompt)
        return self._parse_ai_response(response.text)
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse JSON response from AI"""
        import json
        
        # Clean up response
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1])
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                'title': '',
                'content': response_text,
                'tags': ['ایران', 'اخبار']
            }
    
    def generate_blog_html(self, news_item: Dict) -> str:
        """Generate HTML content for Blogger post"""
        
        title = news_item.get('processed_title', news_item.get('title', ''))
        content = news_item.get('processed_content', news_item.get('description', ''))
        image_url = news_item.get('image_url', '')
        source = news_item.get('source', '')
        link = news_item.get('link', '')
        
        # Build HTML
        html_parts = []
        
        # Add image if available
        if image_url:
            html_parts.append(f'''
<div class="news-image" style="text-align: center; margin-bottom: 20px;">
    <img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px;" />
</div>
''')
        
        # Add content
        # Check if content already contains HTML tags
        if '<p>' in content or '<div>' in content:
            html_parts.append(f'<div class="post-text" style="font-size: 18px; line-height: 1.8; text-align: justify;">{content}</div>')
        else:
            # Fallback for plain text
            paragraphs = content.split('\n')
            for p in paragraphs:
                if p.strip():
                    html_parts.append(f'<p style="font-size: 18px; line-height: 1.8; text-align: justify;">{p.strip()}</p>')
        
        # Add source

        html_parts.append(f'''
<hr style="margin: 30px 0;" />
<p style="font-size: 0.9em; color: #666;">
    📌 منبع: <a href="{link}" target="_blank" rel="noopener">{source}</a>
</p>
''')
        
        return '\n'.join(html_parts)


# Test the processor
if __name__ == "__main__":
    # Test with sample news
    sample_news = {
        'title': 'Iran protests continue amid internet blackout',
        'description': 'Protests have continued across Iran despite widespread internet restrictions imposed by authorities.',
        'language': 'en',
        'source': 'Test Source',
        'link': 'https://example.com'
    }
    
    processor = AIProcessor()
    processed = processor.process_news(sample_news)
    
    print("Processed Title:", processed.get('processed_title'))
    print("Tags:", processed.get('tags'))
    print("\nHTML Content:")
    print(processor.generate_blog_html(processed))
