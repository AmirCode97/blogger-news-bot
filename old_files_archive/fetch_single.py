import sys
import os
from bs4 import BeautifulSoup
import codecs

sys.path.append(r'c:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot')
from blogger_poster import BloggerPoster

poster = BloggerPoster()
try:
    resp = poster.service.posts().list(
        blogId=poster.blog_id, 
        maxResults=50,
    ).execute()
    
    posts = resp.get('items', [])
    for p in posts:
        if 'blog-post_729.html' in p['url']:
            with codecs.open('single_post.html', 'w', 'utf-8') as f:
                f.write(p['content'])
            print("Saved to single_post.html", p['id'])
            break
except Exception as e:
    print(e)
