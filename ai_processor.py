
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
                self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
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
            ai_text = response.text
            
            # Try to extract unique title if AI provided one
            new_title = title
            if "===TITLE===" in ai_text:
                try:
                    title_part = ai_text.split("===TITLE===")[1].split("===PERSIAN===")[0]
                    new_title = title_part.strip()
                except:
                    pass
            
            return new_title, ai_text
        except Exception as e:
            print(f"[Error] AI Processing failed: {e}")
            return title, content
