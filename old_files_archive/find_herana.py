import cloudscraper
from bs4 import BeautifulSoup

def find_workers_link():
    print("Connecting to HRA-News to find the exact category link...")
    scraper = cloudscraper.create_scraper()
    response = scraper.get('https://www.hra-news.org/')
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for a in soup.find_all('a'):
            if a.text and 'کارگر' in a.text:
                href = a.get('href')
                if href and href.startswith('http'):
                    links.add(href)
        
        print("\n--- Found these exact links for 'کارگران' ---")
        for link in links:
            print(link)
    else:
        print(f"Failed to load homepage. Status: {response.status_code}")

if __name__ == "__main__":
    find_workers_link()
