import os
import re
import urllib.request
import ssl

def download_all_images():
    print("Starting download of custom images...")
    
    # Create images directory
    os.makedirs("images", exist_ok=True)
    
    # Read main.py to extract all image URLs
    with open("main.py", "r", encoding="utf-8") as f:
        main_content = f.read()
        
    # Find the _B base URL
    base_match = re.search(r'_B\s*=\s*["\'](https://[^"\']+)["\']', main_content)
    if not base_match:
        print("Could not find _B base URL in main.py")
        return
        
    base_url = base_match.group(1)
    print(f"Base URL: {base_url}")
    
    # Find all image IDs matching the f-string format f"{_B}/<id>/image.png"
    image_ids = re.findall(r'_B\}/([a-zA-Z0-9]+)/image\.png', main_content)
    
    # Make unique
    unique_ids = list(set(image_ids))
    print(f"Found {len(unique_ids)} unique image IDs to download.")
    
    # Bypass SSL verification if needed
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    downloaded = 0
    failed = []
    
    for img_id in unique_ids:
        url = f"{base_url}/{img_id}/image.png"
        filename = f"images/{img_id}.png"
        
        print(f"Downloading {img_id}...")
        try:
            # Use a proper browser User-Agent
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req, context=ctx) as response, open(filename, 'wb') as out_file:
                out_file.write(response.read())
            print(f"  Saved as {filename}")
            downloaded += 1
        except Exception as e:
            print(f"  Failed to download {url}: {e}")
            failed.append((url, e))
                
    print("\n" + "="*40)
    print(f"Download complete: {downloaded} downloaded, {len(failed)} failed.")
    if failed:
        print("Failed URLs:")
        for url, err in failed:
            print(f"  - {url}: {err}")
    print("="*40)

if __name__ == "__main__":
    download_all_images()
