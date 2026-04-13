import sys
import os
from bs4 import BeautifulSoup
import re

sys.path.append(r'c:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot')
from blogger_poster import BloggerPoster

def fix_duplicates():
    poster = BloggerPoster()
    page_token = None
    count = 0
    fixed_count = 0
    
    while True:
        try:
            resp = poster.service.posts().list(
                blogId=poster.blog_id, 
                maxResults=50,
                pageToken=page_token
            ).execute()
            
            posts = resp.get('items', [])
            if not posts:
                break
                
            for p in posts:
                count += 1
                content = p.get('content', '')
                
                # Use BeautifulSoup to parse and find the Persian Section
                soup = BeautifulSoup(content, 'html.parser')
                
                # In main.py, it's wrapped in: <div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
                fa_divs = soup.find_all('div', attrs={'style': lambda value: value and 'direction:rtl' in value and 'text-align:justify' in value})
                
                needs_update = False
                new_content_html = content
                
                # Wait, "کانون حقوق بشر ایران" comes from news_fetcher.py. Maybe the text duplication is inside the div itself.
                # Let's write a simple deduplicator for the text inside the persian section.
                # Actually, wait, let's just find the text inside the persian section, check if it's mirrored (i.e., Text A repeated as Text A).
                
                # Check for duplication
                for div in fa_divs:
                    original_html = str(div)
                    
                    # Split child nodes by string or <br> etc. Instead, let's just check the raw text.
                    text = div.get_text(separator='\n').strip()
                    
                    if not text or len(text) < 100: continue
                    
                    # A simple check: if text can be split in half and the two halves are strongly similar, or one is a substring of the other.
                    # e.g., text = X + "\n" + X (or similar)
                    
                    # Let's find duplicated block of at least 150 chars
                    clean_text = re.sub(r'\s+', ' ', text).strip()
                    if len(clean_text) < 100: continue
                    
                    part1 = clean_text[:len(clean_text)//2]
                    part2 = clean_text[len(clean_text)//2:]
                    
                    # if they are literally the same (ignoring spaces), or almost the same:
                    # Let's do a more robust string search
                    
                    chunk = clean_text[:100]
                    first_pos = clean_text.find(chunk)
                    second_pos = clean_text.find(chunk, first_pos + len(chunk))
                    
                    if second_pos > 0:
                        print(f"Post '{p['title']}' URL: {p['url']} has a duplicate!")
                        
                        # Fix it
                        # The duplication might be in the raw text, let's find the exact middle or the second_pos in the original string (with HTML tags).
                        # Let's just grab the HTML of the first occurrence.
                        
                        # Let's print out the content to see what it's like.
                        print("==== BEFORE ====")
                        print(original_html)
                        
            page_token = resp.get('nextPageToken')
            if not page_token:
                break
                
        except Exception as e:
            print("Error:", e)
            break
            
    print(f"Total processed: {count}")

if __name__ == '__main__':
    fix_duplicates()
