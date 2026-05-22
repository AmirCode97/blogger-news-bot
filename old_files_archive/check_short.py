import urllib.request
import re
import ssl

def check():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    url = 'https://kommodo.ai/i/3XhhBrieVpJFtVtLookz'
    print(f"Checking {url}...")
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            html = response.read().decode('utf-8')
            
        print("Page HTML length:", len(html))
        
        # Look for any image URLs
        urls = re.findall(r'https://[^\s"\'()]+', html)
        img_urls = [u for u in urls if any(ext in u.lower() for ext in ['.png', '.jpg', '.jpeg', '/image'])]
        
        print("Found image URLs:")
        for u in set(img_urls):
            print(f"  - {u}")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check()
