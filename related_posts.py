"""Render related-story cards for newly published articles."""
import re
from datetime import datetime
from urllib.parse import quote

import jdatetime

HAS_JDATETIME = True

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
        # Prevent double proxying if it's already a wsrv.nl or googleusercontent link
        if "wsrv.nl" in img_url or "googleusercontent" in img_url or "wp.com" in img_url:
            return img_url
        
        # Proxy standard external images with wsrv.nl instead of googleusercontent
        if img_url.startswith("http"):
            return f"https://wsrv.nl/?url={quote(img_url)}&w=600&output=webp&q=75"
        return img_url
        
    return get_fallback_image(label, resolved_images)

def get_fallback_image(label, resolved_images):
    # Disable stock images as per user preference
    return ""


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
    
    import base64
    import uuid
    # Encode HTML to base64 to hide it from RSS readers and text extractors
    encoded_html = base64.b64encode(widget_html.encode('utf-8')).decode('utf-8')
    uid = uuid.uuid4().hex
    
    js_wrapper = f"""
    <div id="related-{uid}"></div>
    <script>
    (function() {{
        var init = function() {{
            var b64 = "{encoded_html}";
            // Using a safe decoding method for UTF-8
            var html = decodeURIComponent(escape(window.atob(b64)));
            var placeholder = document.getElementById("related-{uid}");
            if (placeholder && !placeholder.getAttribute('data-loaded')) {{
                placeholder.setAttribute('data-loaded', 'true');
                var wrapper = document.createElement('div');
                wrapper.innerHTML = html;
                
                // Find post body to insert outside of it
                var postBody = placeholder.closest('.post-body') || placeholder.closest('.entry-content');
                if (postBody && postBody.parentNode) {{
                    postBody.parentNode.insertBefore(wrapper, postBody.nextSibling);
                }} else {{
                    placeholder.parentNode.insertBefore(wrapper, placeholder.nextSibling);
                }}
            }}
        }};
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', init);
        }} else {{
            init();
        }}
    }})();
    </script>
    """
    return js_wrapper
