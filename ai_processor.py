
import os
import google.generativeai as genai
from config import GEMINI_API_KEY, AI_SYSTEM_PROMPT

class AIProcessor:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    def process_news(self, title, content):
        if not self.model:
            return title, content
        
        try:
            prompt = f"{AI_SYSTEM_PROMPT}\n\nTitle: {title}\nContent: {content}"
            response = self.model.generate_content(prompt)
            return title, response.text
        except:
            return title, content
