import sys
import os
import re
import json
import time
from urllib.parse import quote
from datetime import datetime

# Adjust path to import custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from blogger_poster import BloggerPoster

sys.stdout.reconfigure(encoding='utf-8')

# Import jdatetime or define fallback Jalali converter
try:
    import jdatetime
    HAS_JDATETIME = True
except ImportError:
    HAS_JDATETIME = False

# Import BeautifulSoup
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

def gregorian_to_jalali(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 335]
    if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
        leap = 1
    else:
        leap = 0
    
    gd_in_year = g_d_m[gm - 1] + gd
    if gm > 2:
        gd_in_year += leap
        
    g_day_no = 365 * (gy - 1) + (gy - 1) // 4 - (gy - 1) // 100 + (gy - 1) // 400 + gd_in_year
    j_day_no = g_day_no - 226899
    
    j_np = j_day_no // 12053
    j_day_no %= 12053
    
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365
        
    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        jm = 7 + (j_day_no - 186) // 30
        jd = 1 + (j_day_no - 186) % 30
        
    return jy, jm, jd

def get_persian_date(date_iso_str):
    try:
        # standard ISO format like: "2026-05-22T21:57:12Z" or "2026-05-22"
        # Extract date parts
        date_clean = date_iso_str.split('T')[0]
        dt = datetime.strptime(date_clean, "%Y-%m-%d")
        
        months = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        if HAS_JDATETIME:
            jd_obj = jdatetime.date.fromgregorian(date=dt)
            jy, jm, jd = jd_obj.year, jd_obj.month, jd_obj.day
        else:
            jy, jm, jd = gregorian_to_jalali(dt.year, dt.month, dt.day)
            
        # Convert to Persian digits
        fa_digits = "۰۱۲۳۴۵۶۷۸۹"
        def to_fa(n):
            return "".join(fa_digits[int(d)] for d in str(n))
            
        return f"{to_fa(jd)} {months[jm-1]} {to_fa(jy)}"
    except Exception as e:
        print(f"Error parsing date {date_iso_str}: {e}")
        return "۲۸ اردیبهشت ۱۴۰۵"

def extract_first_image(content, label, resolved_images):
    if not content:
        return get_fallback_image(label, resolved_images)
    
    # Try finding an image URL
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if match:
        img_url = match.group(1)
        # Ensure wsrv is applied if it's an external image
        if img_url.startswith("http") and "wsrv.nl" not in img_url and "jsdelivr.net" not in img_url:
            img_url = f"https://wsrv.nl/?url={quote(img_url)}"
        return img_url
        
    return get_fallback_image(label, resolved_images)


BLOGGER_STOCK_IMAGES = {
    "3XhhBrieVpJFtVtLookz": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjXs7Rr_lIoLkhtvXAkTM3iNzA3HqTWvXsTm50jzHwJJD6EWoynvn4pN9NX18wUbIUlZ2VIQ7rgXNzEEuvOpfCfXhYdDLe0o0ylK37rZUE-4ka1HCxr1Ips1N-OSTSd9hTb4uAHHmg2h8-HV-nhJCiiD-gFmoDl4XbFE9CanDkI-bx3hCR3nBnBOPGV3lU5/s1200/3XhhBrieVpJFtVtLookz.jpg",
    "4LsX7qJLZi06uBnW8ONx": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjqc8d2smdC9GAbeTPQrG7AvBVg0MGlN2hhzRiKiVr4eyARtPhDSMyyQHUg3v2hJiB5lMTZrNgLDlnObOFdjR4pRHKaV9A7DMlPtRwWDmU7eUiEH8MVVFjTSsYyU4Y4Ug8AtM-ZdkzFIMQZPHrXMoaouQZoRWd_ckXAauvRZUrkUdtqmlkqZf3dhIA7Qnty/s1200/4LsX7qJLZi06uBnW8ONx.png",
    "43j4MvIyLLHNRaUR4xyK": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg5zXnDWrUHUj9ch7WiJa65oESzZa5ibhsXoKnNtjFqrA6D97-USQRsSaUVEd3QkXO-x0ICUDBmujSWm1fanca-qGPxzKtn8uQJRl9vkeOp9f7gejZvikIcycmlD7W3xoJhaWjSpBBNG0BOq4PX25Jj3FPwn7oVi_NkOK3QutQErCL4fiq4G9rA7SvTxSdy/s1200/43j4MvIyLLHNRaUR4xyK.png",
    "bMWHv8lA1GzcwnImumn7": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi4O7sj-0CRivOX9omV1LkFTd9y9qZeyDi_jShCPn0Owep1Q2lguZdJNp7j9gwui9yhEFXhyXTwWh52LYep0L4kNMy2ycSUSYDeW1_7Je26PYgbxJfzAWoDKpQwgQHehgiA09za96U2AnLBnTfzXvhc9IzuesFm0o3r75qnXQyfHZEH_hl2M5o5M5hX1Oxd/s1200/bMWHv8lA1GzcwnImumn7.png",
    "bwStazSQyv0rHfPwsKqS": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhRMSTKt8_I6Zgvdoq7uuiKZ9RZU3d4L7fTBFavjiRVGMqztgdfXHfhrR6muorDRWyqasassEhbT211CbRfsT4fLy1iPe7w3qalfWOsSxNWrGqrFybEYN-W_rVSzURL8qIn_jBnVHAl9by_g7SzFIPOd3CFVjLpNJgOP2fIjrDAPLXKLkLi8bdBCF9DGZAb/s1200/bwStazSQyv0rHfPwsKqS.png",
    "fTPZtAObAols1lEMuvse": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhE5JIcdtphZgw5KW-ABUbeBK3fZr0cbfodMvqOkFXMNoIvllDiYz-VGUR1UiY7kQw4_I6OZr0T-o9lHUYK73IV7Z51azGLgejdmno-9_4z8Z_GDMtFZQUSEUjdaiGHEhWpcyOWe3oMW-_sF-oAYor7Rn7gvilkg30HtyO5e3Mnc5ELrDhSNV0e_1uqSp2b/s1200/fTPZtAObAols1lEMuvse.png",
    "h0D5PmQziVoH8bwSfVJn": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhVR7B_zksIcEWSDBIyIM8ZuuTSKHeOQl5WdL53HYSlb5wtI_su1FytB090SMUiJGD71pSb4wySTFHlB08d7H5AnsmsrNiJstJx5FFYJtp4X4DjTy6f3tUsA5GmYp3RjcVIaiQhq7NEG1cOdyMzHIfujtYZJcwBe_lPb9GALxdnIRrWnZ1shVfuj7VxGMFc/s1200/h0D5PmQziVoH8bwSfVJn.png",
    "K6pWnYcCIIlNtoh4cDKF": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgkh7n_GTfCARZe6vTSPhvureJwTUvoXwXrOucxqKWmu-9b0geE0OZ9H89XwhH9i7w2ybPJ5yGIhtwGzJ0KnjCJa-NAYkObDU299oGQbdvi7VQIYsZYQjZvJAt59XrUAVGYxZszdkCBBcRKNaKBzkLqxFv-gpAovQKe2LYiUeqFwaNL7N5vnKrrztHxgWZo/s1200/K6pWnYcCIIlNtoh4cDKF.png",
    "p54CDjq7NrukeAnOYpIq": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgdyuk1Au7bEdZ6MSTGAH21rNQG4ZSNl8euVrITDA1rAHgdnZsZtlyZvef8pYI3Lyo-Wj1PKgCswprHZv2gHmK99B39rG3CQYqMZnoDxDKyxWZ6r4-ykkwg84GHbQGRXY9LqBW466izAJfmUjlo37BtubACBtyEJl_ZdQYPf8V-1hbwi_-d95H-hTrqHZt1/s1200/p54CDjq7NrukeAnOYpIq.png",
    "T4C2bHaksBsaY3DOLobO": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgXpBZDhHEN51ZR2RhkIe9Sg9k5JBLSYNb1dJfxwvODQ5qf3aU3QEgy3NRjhznnxpbiCN7UxhEswr1NjwTFIS7N9_UYXGfowa5VvX5AW4TIOvRoehtZ9hQOy49sBgU9HXzvEnwFuWIaHxkPe0ML70JcNCHoscvwssgUvSTr-iZfV7Ll0ymdLf5tHujxIa1q/s1200/T4C2bHaksBsaY3DOLobO.png"
}


def get_fallback_image(label, resolved_images):
    import random
    category_fallbacks = {
        'وضعیت زندانیان': ["bMWHv8lA1GzcwnImumn7", "p54CDjq7NrukeAnOYpIq", "T4C2bHaksBsaY3DOLobO"],
        'حقوق بشر': ["3XhhBrieVpJFtVtLookz", "K6pWnYcCIIlNtoh4cDKF"],
        'بین‌الملل': ["K6pWnYcCIIlNtoh4cDKF"],
        'کارگران': ["4LsX7qJLZi06uBnW8ONx", "43j4MvIyLLHNRaUR4xyK", "bwStazSQyv0rHfPwsKqS"]
    }
    
    fallback_id = None
    if label in category_fallbacks:
        fallback_id = random.choice(category_fallbacks[label])
    else:
        fallback_id = random.choice(list(BLOGGER_STOCK_IMAGES.keys()))
        
    if fallback_id:
        return BLOGGER_STOCK_IMAGES.get(fallback_id)
    
    return "https://wsrv.nl/?url=https%3A//images.unsplash.com/photo-1504917595217-d4dc5ebe6122"

def clean_html_content(content):
    """Remove extra/duplicated tags (like multiple footers, multiple styles, multiple JSON-LDs)
    and return the clean body."""
    if not content:
        return "", ""
        
    if HAS_BS4:
        soup = BeautifulSoup(content, 'lxml' if 'lxml' in sys.modules else 'html.parser')
        
        # Remove all style tags
        for style in soup.find_all('style'):
            style.decompose()
            
        # Remove all json-ld scripts
        for script in soup.find_all('script', type='application/ld+json'):
            script.decompose()
            
        # Remove all footers
        for footer in soup.find_all('footer'):
            footer.decompose()
            
        # Remove any divs representing source box or tag cloud if bs4 couldn't catch them as footer
        for div in soup.find_all('div'):
            if div.attrs is None:
                continue
            style_attr = div.get('style', '')
            class_attr = div.get('class', [])
            # Check for background:#161616 or background:#1a1a1a or border-left:3px or contains "منبع خبر"
            if 'border-right:3px' in style_attr or 'border-left:3px' in style_attr or 'منبع خبر' in div.get_text():
                div.decompose()
            elif 'برچسب‌های مرتبط' in div.get_text() and ('border-top' in style_attr or 'margin-top' in style_attr):
                div.decompose()
            elif 'related-posts-widget' in class_attr or ('مطالب مرتبط' in div.get_text() and 'border' in style_attr):
                div.decompose()
                
        # Extract main image if any (inside figure or img)
        main_image = ""
        img_tag = soup.find('img')
        if img_tag:
            main_image = img_tag.get('src', '')
            # Keep it or remove it from body? Let's keep it or decompose the parent figure if we want to rebuild it
            figure = img_tag.find_parent('figure')
            if figure:
                figure.decompose()
            else:
                img_tag.decompose()
                
        # Reconstruct clean text paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text:
                # Avoid keeping previous meta-description as lead paragraph if it's already inside article
                # (but typically we can just keep paragraphs)
                paragraphs.append(text)
                
        # In case there were no <p> tags, split by newline and get text
        if not paragraphs:
            text = soup.get_text()
            for line in text.split('\n'):
                line_clean = line.strip()
                if line_clean and len(line_clean) > 20:
                    paragraphs.append(line_clean)
                    
        return paragraphs, main_image
    else:
        # Fallback regex parsing if bs4 is not available
        # Remove style blocks
        clean = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        # Remove script blocks
        clean = re.sub(r'<script.*?>.*?</script>', '', clean, flags=re.DOTALL)
        # Remove footers
        clean = re.sub(r'<footer.*?>.*?</footer>', '', clean, flags=re.DOTALL)
        
        # Extract paragraphs
        paragraphs = []
        for p in re.findall(r'<p.*?>(.*?)</p>', clean, flags=re.DOTALL):
            p_text = re.sub(r'<.*?>', '', p).strip()
            if p_text:
                paragraphs.append(p_text)
                
        # Extract first image URL
        main_image = ""
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        if img_match:
            main_image = img_match.group(1)
            
        return paragraphs, main_image

def build_related_posts_widget(related_posts, current_label):
    cards_html = []
    
    for post in related_posts:
        title = post['title']
        url = post['url']
        label = post['label']
        image = post['image']
        date_str = post['date']
        
        card = f"""
        <a href="{url}" style="text-decoration:none; display:flex; flex-direction:column; background:#181818; border-radius:10px; overflow:hidden; border:1px solid #282828; transition:all 0.3s ease; box-shadow:0 4px 15px rgba(0,0,0,0.3);" onmouseover="this.style.transform='translateY(-5px)'; this.style.borderColor='#c0392b'; this.style.boxShadow='0 8px 25px rgba(192, 57, 43, 0.2)';" onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='#282828'; this.style.boxShadow='0 4px 15px rgba(0,0,0,0.3)';">
            <!-- Image Section -->
            <div style="position:relative; width:100%; height:140px; overflow:hidden; background:#222;">
                <img src="{image}" alt="{title}" loading="lazy" style="width:100%; height:100%; object-fit:cover;" />
                <!-- Red Capsule Tag on Image -->
                <span style="position:absolute; top:10px; right:10px; background:#c0392b; color:#fff; font-size:10px; font-weight:bold; padding:2px 8px; border-radius:4px; box-shadow:0 2px 5px rgba(0,0,0,0.3);">{label}</span>
            </div>
            
            <!-- Text Content Section -->
            <div style="padding:12px; display:flex; flex-direction:column; justify-content:space-between; flex-grow:1;">
                <!-- Title -->
                <h3 style="font-size:14px; line-height:1.6; color:#eee; margin:0 0 12px 0; font-weight:bold; height:45px; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;">{title}</h3>
                
                <!-- Card Footer -->
                <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #222; padding-top:8px; font-size:11px;">
                    <span style="color:#e74c3c; font-weight:bold; display:flex; align-items:center; gap:2px;">
                        بیشتر
                        <svg width="10" height="10" fill="currentColor" viewBox="0 0 16 16" style="transform:scaleX(-1);">
                            <path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>
                        </svg>
                    </span>
                    <span style="color:#777;">{date_str}</span>
                </div>
            </div>
        </a>
        """
        cards_html.append(card)
        
    # Standard related posts layout (mimicking Image 2)
    widget_html = f"""
    <div class="related-posts-widget" style="margin-top:40px; margin-bottom:20px; background:#121212; border:1px solid #222; border-top:4px solid #c0392b; border-radius:12px; padding:20px; direction:rtl; text-align:right; font-family:'Vazir',sans-serif; box-shadow:0 10px 30px rgba(0,0,0,0.5);">
        <!-- Widget Header -->
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid #222; padding-bottom:15px;">
            <!-- Left: Category Capsule -->
            <span style="background:rgba(192, 57, 43, 0.15); border:1px solid #c0392b; color:#e74c3c; font-size:12px; font-weight:bold; padding:4px 12px; border-radius:20px;">{current_label}</span>
            
            <!-- Right: Title and Icon -->
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:18px; font-weight:bold; color:#fff;">مطالب مرتبط</span>
                <div style="background:#c0392b; color:#fff; width:30px; height:30px; border-radius:8px; display:flex; align-items:center; justify-content:center;">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1v-1z"/>
                        <path d="M9.5 3h-4a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1zm0 2.5h-4a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1zm0 2.5h-4a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1zm0 2.5h-4a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1z"/>
                    </svg>
                </div>
            </div>
        </div>
        
        <!-- 3-Column Layout -->
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:15px;">
            {"".join(cards_html)}
        </div>
    </div>
    """
    return widget_html

def update_posts(dry_run=False, limit=150):
    print("=" * 70)
    print(f"  Blogger Clean-up & Related Posts Engine (Dry-run: {dry_run}, Limit: {limit})")
    print("=" * 70)
    
    poster = BloggerPoster()
    print(f"[OK] Connected to Blogger. Blog ID: {poster.blog_id}")
    
    # Load resolved stock images mapping
    resolved_images = BLOGGER_STOCK_IMAGES

    # Step 1: Fetch ALL posts on the blog to index them
    print("\nFetching all posts to build index...")
    all_posts = []
    next_page_token = None
    
    # Only fetch up to 300 posts to build a rich recent index and avoid memory/time overhead
    max_index_fetch = 300
    while len(all_posts) < max_index_fetch:
        try:
            response = poster.service.posts().list(
                blogId=poster.blog_id,
                maxResults=100,
                pageToken=next_page_token
            ).execute()
            
            items = response.get('items', [])
            if not items:
                break
                
            for item in items:
                content = item.get('content', '')
                labels = item.get('labels', [])
                
                # Get clean label
                default_label = labels[0] if labels else "حقوق بشر"
                
                # Extract image or fallback
                img_url = extract_first_image(content, default_label, resolved_images)
                
                all_posts.append({
                    'id': item['id'],
                    'title': item['title'],
                    'url': item.get('url', ''),
                    'labels': labels,
                    'label': default_label,
                    'image': img_url,
                    'published': item.get('published', ''),
                    'content': content
                })
                
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
        except Exception as e:
            print(f"[ERROR] Fetching posts: {e}")
            break
            
    print(f"[OK] Indexed {len(all_posts)} posts.")
    
    # Process each post up to the limit
    updated_count = 0
    
    for idx, post in enumerate(all_posts):
        if idx >= limit and not dry_run:
            print(f"\nReached update limit of {limit} posts. Stopping updates.")
            break
            
        print(f"\n[{idx+1}/{min(len(all_posts), limit) if not dry_run else 3}] Processing: {post['title'][:50]} (ID: {post['id']})")
        
        # Determine 3 related posts based on labels
        current_labels = set(post['labels'])
        related_candidates = []
        
        for cand in all_posts:
            if cand['id'] == post['id']:
                continue
            # Calculate overlapping labels
            overlap = len(current_labels.intersection(set(cand['labels'])))
            related_candidates.append((overlap, cand))
            
        # Sort related candidates: highest label overlap first, then newest published date
        related_candidates.sort(key=lambda x: (x[0], x[1]['published']), reverse=True)
        
        # Pick top 3
        selected_posts = []
        for score, cand in related_candidates[:3]:
            # Convert Gregorian date of candidates to elegant Jalali
            persian_date_cand = get_persian_date(cand['published'])
            selected_posts.append({
                'title': cand['title'],
                'url': cand['url'],
                'label': cand['label'],
                'image': cand['image'],
                'date': persian_date_cand
            })
            
        # If less than 3, fill up using top candidates
        while len(selected_posts) < 3 and len(all_posts) > len(selected_posts) + 1:
            for cand in all_posts:
                if cand['id'] == post['id'] or cand['url'] in [p['url'] for p in selected_posts]:
                    continue
                persian_date_cand = get_persian_date(cand['published'])
                selected_posts.append({
                    'title': cand['title'],
                    'url': cand['url'],
                    'label': cand['label'],
                    'image': cand['image'],
                    'date': persian_date_cand
                })
                if len(selected_posts) == 3:
                    break
                    
        # Parse and clean post content
        paragraphs, main_image = clean_html_content(post['content'])
        
        if not paragraphs:
            print("  [Warning] Could not extract paragraphs, skipping cleanup to avoid empty content.")
            continue
            
        # Ensure we have a valid main image
        if not main_image:
            main_image = post['image']
            
        # Format the lead paragraph and body
        lead_paragraph = paragraphs[0]
        body_paragraphs = paragraphs[1:]
        
        description_html = ""
        for p in body_paragraphs:
            description_html += f'<p style="margin-bottom:18px;">{p}</p>\n'
            
        # Build JSON-LD SEO Schema
        schema_data = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": post['title'],
            "image": [main_image] if main_image else [],
            "datePublished": post['published'],
            "dateModified": post['published'],
            "author": {
                "@type": "Organization",
                "name": "iranpolnews",
                "url": "https://iranpolnews.blogspot.com"
            },
            "publisher": {
                "@type": "Organization",
                "name": "iranpolnews",
                "logo": {
                    "@type": "ImageObject",
                    "url": BLOGGER_STOCK_IMAGES.get("K6pWnYcCIIlNtoh4cDKF", "https://wsrv.nl/?url=https%3A//images.unsplash.com/photo-1504917595217-d4dc5ebe6122")
                }
            },
            "description": lead_paragraph[:160] + "..." if len(lead_paragraph) > 160 else lead_paragraph
        }
        
        schema_json = json.dumps(schema_data, ensure_ascii=False)
        schema_script = f'<script type="application/ld+json">{schema_json}</script>'
        
        # Build tag links for the single correct footer
        labels_to_use = post['labels'] if post['labels'] else [post['label']]
        tag_links = []
        for label in labels_to_use:
            tag_links.append(f'<a href="/search/label/{quote(label)}" style="color:#c0392b;text-decoration:none;margin-left:12px;font-weight:bold;transition:color 0.2s;" onmouseover="this.style.color=\'#e74c3c\'" onmouseout="this.style.color=\'#c0392b\'">#{label}</a>')
        tags_html = " ".join(tag_links)
        
        # Build featured image HTML
        image_html = ""
        if main_image:
            image_html = f'''<figure style="margin:0 0 25px 0;text-align:center;">
    <img src="{main_image}" alt="{post['title']}" title="{post['title']}" loading="lazy" decoding="async" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);" />
    <figcaption style="display:none;">{post['title']}</figcaption>
</figure>'''

        # Build "مطالب مرتبط" Widget
        related_widget_html = build_related_posts_widget(selected_posts, post['label'])
        
        # Reconstruct clean, single footer
        single_footer_html = f"""
        <footer style="margin-top:35px;border-top:1px solid #222;padding-top:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;direction:rtl;text-align:right;">
            <div style="font-size:14px;color:#888;margin-bottom:10px;">
                <span style="color:#aaa;margin-left:8px;font-weight:bold;">برچسب‌های مرتبط:</span>
                {tags_html}
            </div>
            <div style="background:#161616;padding:10px 20px;border-radius:8px;border-right:3px solid #c0392b;font-weight:bold;color:#ddd;font-size:13px;box-shadow:0 4px 10px rgba(0,0,0,0.4);margin-bottom:10px;">
                <span style="color:#c0392b;margin-left:8px;">منبع خبر:</span> iranpolnews
            </div>
        </footer>
        """
        
        # NOTE: The Blogger template already has a built-in related-posts section
        # (div.rp-section#related-posts) that dynamically loads via JS/Blogger Feed API.
        # We do NOT inject our own widget to avoid duplicates on the page.
        
        # Assemble complete post HTML
        new_html = f"""
        <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
        {schema_script}
        {image_html}
        
        <!-- Semantic Article Body -->
        <article style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
            <!-- SEO Meta Lead Paragraph -->
            <p style="font-weight:bold;font-size:18px;color:#eee;border-bottom:1px solid #333;padding-bottom:15px;margin-bottom:20px;">
                {lead_paragraph}
            </p>
            
            <!-- Article Content -->
            <div>
                {description_html}
            </div>
        </article>
        
        <!-- Clean SEO Footer -->
        {single_footer_html}
        """
        
        if dry_run:
            print("  [DRY-RUN] Success! Cleaned HTML created.")
            # Write a test file for the first processed post to inspect it
            if updated_count == 0:
                inspect_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dry_run_post_sample.html")
                with open(inspect_file, "w", encoding="utf-8") as f:
                    f.write(new_html)
                print(f"  [DRY-RUN] Saved sample HTML to {inspect_file}")
            updated_count += 1
            if updated_count >= 3:
                print("\n[DRY-RUN] Processed 3 sample posts. Stopping dry-run.")
                break
        else:
            # Check if the new HTML is exactly the same as the existing content
            # We strip both to ignore trailing newlines or whitespace differences at the very ends
            if new_html.strip() == post.get('content', '').strip():
                print(f"  [SKIP] Post already has the latest correct layout and HTML. Skipping API call.")
                continue

            # Update post on Blogger
            try:
                body = {
                    'id': post['id'],
                    'title': post['title'],
                    'content': new_html,
                    'labels': post['labels']
                }
                
                poster.service.posts().update(
                    blogId=poster.blog_id,
                    postId=post['id'],
                    body=body
                ).execute()
                
                print("  [SUCCESS] Post successfully updated on Blogger!")
                updated_count += 1
                
                # Small anti-rate limit delay
                time.sleep(2)
            except Exception as e:
                print(f"  [ERROR] Failed to update post {post['id']}: {e}")
                time.sleep(5)
                
    print("\n" + "=" * 70)
    print(f"  Engine finished. Processed {updated_count} posts.")
    print("=" * 70)

if __name__ == '__main__':
    # Parse CLI argument to determine dry run vs production
    is_dry_run = '--prod' not in sys.argv
    limit_val = 150
    for idx, arg in enumerate(sys.argv):
        if arg == '--limit' and idx + 1 < len(sys.argv):
            try:
                limit_val = int(sys.argv[idx + 1])
            except ValueError:
                pass
    update_posts(dry_run=is_dry_run, limit=limit_val)
