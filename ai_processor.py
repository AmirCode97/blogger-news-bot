
import os
try:
    import google.generativeai as genai
    from config import GEMINI_API_KEY, AI_SYSTEM_PROMPT
    HAS_AI = True
except Exception as e:
    print(f"[Warning] AI Library failed to load: {e}")
    HAS_AI = False

class AIProcessor:
    def __init__(self):
        if HAS_AI and GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
            except:
                self.model = None
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
