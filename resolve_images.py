import urllib.request
import re
import ssl
import os
import json
import time

def resolve_and_download_all():
    # Bypass SSL verification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    os.makedirs("images", exist_ok=True)
    
    # Read main.py to get all unique IDs
    with open("main.py", "r", encoding="utf-8") as f:
        main_content = f.read()
        
    image_ids = re.findall(r'_B\}/([a-zA-Z0-9]+)/image\.(?:png|jpg)', main_content)
    # Also look for any direct IDs in comments or code
    direct_ids = re.findall(r'https://kommodo\.ai/i/([a-zA-Z0-9]+)', main_content)
    
    unique_ids = list(set(image_ids + direct_ids))
    print(f"Found {len(unique_ids)} unique image IDs to resolve.")
    
    resolved_mapping = {}
    downloaded = 0
    failed = []
    
    for idx, img_id in enumerate(unique_ids):
        print(f"\n[{idx+1}/{len(unique_ids)}] Resolving {img_id}...")
        url = f"https://kommodo.ai/i/{img_id}"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, context=ctx) as response:
                html = response.read().decode('utf-8')
                
            # Find the actual image URL hosted on komododecks.com
            matches = re.findall(r'https://plain-weur-prod-public\.komododecks\.com/[^\s"\'()]+', html)
            
            real_url = None
            for m in matches:
                m_lower = m.lower()
                if any(ext in m_lower for ext in ['.png', '.jpg', '.jpeg']) and img_id in m:
                    real_url = m
                    break
                    
            if not real_url and matches:
                # Fallback to the first image match if ID isn't in URL
                real_url = matches[0]
                
            if not real_url:
                print(f"  Failed to find real image URL in HTML for {img_id}")
                failed.append(img_id)
                continue
                
            # Determine extension
            ext = ".png"
            if ".jpg" in real_url.lower() or ".jpeg" in real_url.lower():
                ext = ".jpg"
                
            filename = f"images/{img_id}{ext}"
            print(f"  Real URL: {real_url}")
            print(f"  Saving to: {filename}")
            
            # Download the actual image
            img_req = urllib.request.Request(real_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(img_req, context=ctx) as img_response, open(filename, 'wb') as out_file:
                out_file.write(img_response.read())
                
            resolved_mapping[img_id] = f"{img_id}{ext}"
            downloaded += 1
            print("  Successfully downloaded!")
            
        except Exception as e:
            print(f"  Error resolving/downloading: {e}")
            failed.append(img_id)
            
        time.sleep(0.5) # Avoid hitting rate limits
        
    # Save the mapping to a JSON file
    with open("resolved_images.json", "w", encoding="utf-8") as f:
        json.dump(resolved_mapping, f, indent=2, ensure_ascii=False)
        
    print("\n" + "="*40)
    print(f"Process finished: {downloaded} downloaded, {len(failed)} failed.")
    print("Mapping saved to resolved_images.json")
    print("="*40)

if __name__ == "__main__":
    resolve_and_download_all()
