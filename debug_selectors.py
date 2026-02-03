# Debug selectors specifically
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

def debug_selectors(url):
    print(f"\nDebugging: {url}")
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    articles = soup.select('article')
    print(f"Articles found: {len(articles)}")
    
    if articles:
        first_article = articles[0]
        print("\n--- First Article Structure ---")
        print(first_article.prettify()[:1500])  # Show first 1500 chars
        
        # Test finding link
        link = first_article.select_one('h2 a, h3 a, h4 a')
        print(f"\nLink check: {link}")

debug_selectors('https://fa.iran-hrm.com/')
debug_selectors('https://persian.iranhumanrights.org/')
