
import requests
from bs4 import BeautifulSoup
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
}

def debug_url(url, selectors):
    print(f"\n--- Debugging {url} ---")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Test article selector
        article_sel = selectors.get('articles')
        articles = soup.select(article_sel)
        print(f"Found {len(articles)} items with selector '{article_sel}'")
        
        if len(articles) > 0:
            first = articles[0]
            # Debug Image
            img = first.select_one('img')
            print(f"First item image tag: {img}")
            if img:
                print(f"Image Source: {img.get('src') or img.get('data-src')}")
                
    except Exception as e:
        print(f"Error: {e}")

# IranHRS Config
iranhrs_sel = {
    "articles": "article",
    "image": "img"
}

# Radio Farda Config
radio_sel = {
    "articles": ".media-block__content",
    "image": "img"
}

debug_url("https://iranhrs.org/", iranhrs_sel)
debug_url("https://www.radiofarda.com/", radio_sel)
