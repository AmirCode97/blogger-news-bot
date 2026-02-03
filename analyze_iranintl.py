# Extract article content from Iran Intl ArticleBody
import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.iranintl.com/202602036458'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

print(f"Fetching: {url}\n")
r = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(r.text, 'html.parser')

# Try ArticleBody selector
print("=== Method 1: ArticleBody ===")
article_body = soup.select_one('div[class*="ArticleBody"]')
if article_body:
    print("Found ArticleBody!")
    paragraphs = article_body.find_all('p')
    print(f"Found {len(paragraphs)} <p> tags inside ArticleBody")
    for i, p in enumerate(paragraphs, 1):
        text = p.get_text(strip=True)
        if text:
            print(f"\n[P{i}]: {text[:150]}...")
else:
    print("ArticleBody not found")

# Try main > article structure
print("\n\n=== Method 2: main article content ===")
main = soup.select_one('article main')
if main:
    print("Found article > main!")
    paragraphs = main.find_all('p')
    print(f"Found {len(paragraphs)} <p> tags")
    for i, p in enumerate(paragraphs[:5], 1):
        text = p.get_text(strip=True)
        if text:
            print(f"\n[P{i}]: {text[:150]}...")

# Try direct p tag search with Persian content
print("\n\n=== Method 3: All Persian <p> tags ===")
all_ps = soup.find_all('p')
persian_ps = []
for p in all_ps:
    text = p.get_text(strip=True)
    # Check if Persian (has Persian characters)
    persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    if persian_chars > 30 and len(text) > 50:
        persian_ps.append(text)

print(f"Found {len(persian_ps)} Persian paragraphs")
for i, text in enumerate(persian_ps[:5], 1):
    print(f"\n[P{i}]: {text[:150]}...")
