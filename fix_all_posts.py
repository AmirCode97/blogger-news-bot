import sys
import os

sys.path.append(r'c:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot')
from blogger_poster import BloggerPoster

def process_html(html):
    div_start = html.find('<!-- Persian Section -->')
    if div_start == -1: 
        return html, False
    
    div_tag_start = html.find('<div', div_start)
    div_inner_start = html.find('>', div_tag_start) + 1
    
    # We must find the closing div of this exact div.
    div_end = html.find('</div>', div_inner_start)
    if div_end == -1:
        return html, False
        
    persian_html = html[div_inner_start:div_end]
    lines = persian_html.split('\n')
    
    repeated_index = -1
    for i, line in enumerate(lines):
        clean_line = line.strip()
        # Find a meaty sentence without HTML tags
        if len(clean_line) > 60 and "<" not in clean_line:
            # Check if this exact line appears again
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == clean_line:
                    repeated_index = j
                    break
        if repeated_index != -1:
            break
            
    if repeated_index != -1:
        # Look backwards from repeated_index to see if there is a "Tags:" line to remove as well
        cut_index = repeated_index
        for k in range(repeated_index - 1, max(-1, repeated_index - 8), -1):
            cline = lines[k].strip()
            if 'Tags:' in cline or ('کانون حقوق بشر' in cline and 'دنبال کنید' in cline):
                cut_index = k
            elif cline == '':
                continue
            else:
                break
                
        new_persian_html = '\n'.join(lines[:cut_index]) + '\n'
        new_html = html[:div_inner_start] + new_persian_html + html[div_end:]
        return new_html, True
        
    return html, False

def fix_all_posts():
    poster = BloggerPoster()
    page_token = None
    count = 0
    fixed_count = 0
    
    # Let's use standard output without unicode errors
    # Or just print safe strings
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
                
                new_content, needed_fix = process_html(content)
                if needed_fix:
                    print("Fixing duplicate in post ID:", p['id'])
                    # Update post
                    body = {
                        'id': p['id'],
                        'title': p['title'],
                        'content': new_content,
                        'labels': p.get('labels', [])
                    }
                    poster.service.posts().update(
                        blogId=poster.blog_id, 
                        postId=p['id'], 
                        body=body
                    ).execute()
                    fixed_count += 1
                    
            page_token = resp.get('nextPageToken')
            if not page_token:
                break
                
        except Exception as e:
            print("Error:", e)
            break
            
    print("Total posts checked:", count)
    print("Total posts fixed:", fixed_count)

if __name__ == '__main__':
    fix_all_posts()
