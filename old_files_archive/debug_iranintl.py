"""
Deep debug: Why Iran International news is not coming through
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fa-IR,fa;q=0.9,en;q=0.8',
}

print("="*70)
print("TEST 1: Direct fetch https://www.iranintl.com/iran")
print("="*70)
try:
    r = requests.get("https://www.iranintl.com/iran", headers=HEADERS, timeout=15, verify=False)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type','?')}")
    print(f"Content length: {len(r.text)}")
    
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Test the config selector: a[href*='2026']
    articles = soup.select("a[href*='2026']")
    print(f"\nSelector 'a[href*=2026]': {len(articles)} matches")
    for a in articles[:5]:
        print(f"  - {a.get_text().strip()[:60]} → {a.get('href','')[:80]}")
    
    # Try other selectors
    all_articles = soup.find_all('article')
    print(f"\nSelector 'article': {len(all_articles)} matches")
    
    all_a = soup.find_all('a')
    print(f"\nTotal <a> tags: {len(all_a)}")
    
    # Check if it's a JS-rendered page
    scripts = soup.find_all('script')
    print(f"\nTotal <script> tags: {len(scripts)}")
    
    # Check for Next.js / React indicators
    if soup.find('div', id='__next'):
        print("⚠️ FOUND __next div - This is a Next.js app (client-side rendered!)")
    if soup.find('div', id='root'):
        print("⚠️ FOUND #root div - This is a React SPA (client-side rendered!)")
    
    # Show raw HTML snippet
    print(f"\n--- First 2000 chars of HTML ---")
    print(r.text[:2000])
    
except Exception as e:
    print(f"ERROR: {e}")

print(f"\n\n{'='*70}")
print("TEST 2: Try RSS feeds for Iran International")
print("="*70)

rss_urls = [
    "https://www.iranintl.com/feed",
    "https://www.iranintl.com/rss",
    "https://www.iranintl.com/rss.xml",
    "https://www.iranintl.com/feed.xml",
    "https://www.iranintl.com/atom.xml",
    "https://www.iranintl.com/api/rss",
    "https://www.iranintl.com/sitemap.xml",
]

import feedparser

for url in rss_urls:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        print(f"\n{url}")
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            feed = feedparser.parse(r.text)
            print(f"  Entries: {len(feed.entries)}")
            if feed.entries:
                for e in feed.entries[:3]:
                    print(f"    - {e.get('title','?')[:60]}")
        else:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

print(f"\n\n{'='*70}")
print("TEST 3: Try Google News RSS for Iran International")
print("="*70)
google_rss = "https://news.google.com/rss/search?q=site:iranintl.com&hl=fa&gl=IR&ceid=IR:fa"
try:
    r = requests.get(google_rss, headers=HEADERS, timeout=10, verify=False)
    print(f"Status: {r.status_code}")
    feed = feedparser.parse(r.text)
    print(f"Entries: {len(feed.entries)}")
    for e in feed.entries[:5]:
        print(f"  - {e.get('title','?')[:60]}")
        print(f"    Link: {e.get('link','?')[:80]}")
except Exception as e:
    print(f"Error: {e}")
