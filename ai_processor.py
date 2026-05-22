"""
AI Processor Module
ماژول پردازش اخبار با هوش مصنوعی Gemini
"""

import google.generativeai as genai
from typing import Dict, Optional
from config import GEMINI_API_KEY, APP_EXTRA_CONFIG, AI_TRANSLATE_PROMPT


class AIProcessor:
    """Process news content using Gemini AI"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment")
        
        genai.configure(api_key=GEMINI_API_KEY)
        # Use gemini-2.5-flash-lite model which works for the current API key
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    def process_news(self, title: str, description: str, language: str = 'fa'):
        """
        Process a news item:
        - Translate if English
        - Summarize and format for blog
        - Generate tags
        """
        try:
            if language == 'en':
                # Translate and process English news
                processed = self._translate_and_process(title, description)
            else:
                # Process Persian news
                processed = self._process_persian(title, description)
            
            return processed.get('title', title), processed.get('content', description)
            
        except Exception as e:
            print(f"❌ AI Processing error: {e}")
            return title, description
    
    def _translate_and_process(self, title: str, description: str) -> Dict:
        """Translate English news to Persian and format"""
        
        prompt = f"""
{AI_TRANSLATE_PROMPT}

عنوان انگلیسی: {title}
متن خبر: {description}

لطفاً خروجی را به این فرمت JSON بده:
{{
    "title": "عنوان فارسی جذاب",
    "content": "متن کامل خبر به فارسی (۲-۳ پاراگراف)",
    "tags": ["تگ۱", "تگ۲", "تگ۳"]
}}

فقط JSON خالص برگردان، بدون هیچ توضیح اضافی.
نکته مهم: از هیچ علامت نگارشی مثل ستاره (**) یا هشتگ (##) در متن استفاده نکن و نام خبرگزاری یا منبع را در متن ذکر نکن.
"""
        
        response = self.model.generate_content(prompt)
        return self._parse_ai_response(response.text)
    
    def _process_persian(self, title: str, description: str) -> Dict:
        """Process and enhance Persian news"""
        
        prompt = f"""
{APP_EXTRA_CONFIG}

عنوان خبر: {title}
متن خبر: {description}

لطفاً خروجی را به این فرمت JSON بده:
{{
    "title": "عنوان بهبود یافته و جذاب",
    "content": "متن خبر به صورت روان و مناسب وبلاگ (۲-۳ پاراگراف)",
    "tags": ["تگ۱", "تگ۲", "تگ۳"]
}}

فقط JSON خالص برگردان، بدون هیچ توضیح اضافی.
نکته بسیار مهم: از هیچ علامت نگارشی مثل ستاره (**) یا هشتگ (##) در متن استفاده نکن. همچنین به هیچ وجه نام منبع خبر یا خبرگزاری را در داخل متن نیاور!
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
            if lines[0].startswith('```json'):
                text = '\n'.join(lines[1:-1])
            else:
                text = '\n'.join(lines[1:-1])
        
        text = text.replace('**', '').replace('##', '')
        
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
        
        # Build HTML
        html_parts = []
        
        # Add content formatted as neat paragraphs
        paragraphs = content.split('\n')
        for p in paragraphs:
            if p.strip():
                html_parts.append(f'<p style="line-height: 1.8; text-align: justify; margin-bottom: 15px; font-size: 16px;">{p.strip()}</p>')
        
        # Note: The beautiful image at the top and the footer with source and labels 
        # are now added in main.py, so we don't add them here.
        
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
