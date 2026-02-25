"""
Test content extraction from specific news sources
"""
import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Test URLs from different sources
TEST_URLS = [
    ("https://www.iranintl.com/202502072306", "ایران اینترنشنال"),
    ("https://iranhrs.org/2026/02/08/%d8%a8%d8%a7%d8%b2%d8%af%d8%a7%d8%b4%d8%aa-%d8%a2%d8%b0%d8%b1-%d9%85%d9%86%d8%b5%d9%88%d8%b1%db%8c/", "کانون حقوق بشر"),
    ("https://fa.iran-hrm.com/", "ناظران حقوق بشر"),
]

def fetch_article_content(url, source_name):
    """Fetch and extract article content"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"URL: {url}")
        print(f"Source: {source_name}")
        print("="*60)
        
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different selectors
        content_areas = [
            soup.find('article'),
            soup.find('div', class_='entry-content'),
            soup.find('div', class_='post-content'),
            soup.find('div', class_='article-content'),
            soup.find('main'),
        ]
        
        main_div = None
        for area in content_areas:
            if area:
                main_div = area
                print(f"Found content in: {area.name}")
                break
        
        if not main_div:
            main_div = soup.body
            print("Using body as fallback")
        
        # Extract paragraphs
        paragraphs = []
        for p in main_div.find_all('p'):
            text = p.get_text().strip()
            if len(text) > 50:
                paragraphs.append(text)
        
        print(f"\nFound {len(paragraphs)} paragraphs")
        
        # Get image
        og_image = soup.find('meta', property='og:image')
        image = og_image.get('content') if og_image else "No image"
        print(f"Image: {image[:80] if image else 'None'}...")
        
        # Show first few paragraphs
        print("\n--- CONTENT PREVIEW ---")
        for i, par in enumerate(paragraphs[:3]):
            print(f"\nParagraph {i+1} ({len(par)} chars):")
            print(par[:200] + "..." if len(par) > 200 else par)
        
        return {
            'success': len(paragraphs) > 0,
            'paragraphs': len(paragraphs),
            'text_length': sum(len(p) for p in paragraphs),
            'image': image
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {'success': False, 'error': str(e)}

# Test each URL
import urllib3
urllib3.disable_warnings()

print("=" * 80)
print("CONTENT EXTRACTION TEST")
print("=" * 80)

for url, source in TEST_URLS:
    result = fetch_article_content(url, source)
    print(f"\nResult: {result}")
