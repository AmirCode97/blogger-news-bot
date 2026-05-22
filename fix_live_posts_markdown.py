# -*- coding: utf-8 -*-
import sys
import os
import time
import re
from urllib.parse import quote

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from blogger_poster import BloggerPoster

# Reconfigure stdout for UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def safe_print(text):
    try:
        print(text)
    except:
        try:
            print(text.encode('utf-8', errors='replace').decode('utf-8'))
        except:
            print("[Print Error] Cannot encode text.")

def strip_markdown(text):
    """Remove all Markdown formatting symbols from text while preserving the actual content."""
    if not text:
        return text
    # Remove heading markers (##, ###, etc.)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Remove bold+italic (***text*** or ___text___)
    text = re.sub(r'\*{3}(.+?)\*{3}', r'\1', text)
    text = re.sub(r'_{3}(.+?)_{3}', r'\1', text)
    # Remove bold (**text** or __text__)
    text = re.sub(r'\*{2}(.+?)\*{2}', r'\1', text)
    text = re.sub(r'_{2}(.+?)_{2}', r'\1', text)
    # Remove italic (*text* or _text_)
    text = re.sub(r'(?<!\w)\*([^\*\n]+?)\*(?!\w)', r'\1', text)
    # Remove inline code (`text`)
    text = re.sub(r'`([^`]+?)`', r'\1', text)
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[\-\*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove blockquote markers (> text)
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove bullet point markers (* item, - item) at start of lines
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    # Remove numbered list markers (1. item)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    # Remove any remaining standalone ** or ***
    text = re.sub(r'\*{2,3}', '', text)
    # Remove === markers that weren't parsed
    text = re.sub(r'={3,}[A-Z]+={3,}', '', text)
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def strip_ai_noise(text):
    """Remove AI meta-commentary, analysis, and thinking-out-loud lines that should not appear in blog posts."""
    if not text:
        return text
    # Patterns that indicate AI analysis/commentary (not actual news content)
    noise_patterns = [
        r'^.*بسیار عالی.*$',
        r'^.*با توجه به نقش.*$',
        r'^.*پیشنهادات بازنویسی.*$',
        r'^.*سناریوی \d.*$',
        r'^.*عنوان پیشنهادی.*$',
        r'^.*گزینه [الفب].*$',
        r'^.*چرا\?\!?\?.*$',
        r'^.*نکات سئو.*$',
        r'^.*محتوای پیشنهادی.*$',
        r'^.*بهینه‌سازی برای جستجو.*$',
        r'^.*لینک‌سازی داخلی.*$',
        r'^.*عنوان اصلی \(پیشنهادی.*$',
        r'^.*تاکید بر فوریت.*$',
        r'^.*تاکید بر گستردگی.*$',
        r'^.*ساختار پاراگراف.*$',
        r'^.*کلمات کلیدی در عنوان.*$',
        r'^.*قالب‌بندی:.*$',
        r'^.*خوانایی:.*$',
        r'^.*first appeared on.*$',
        r'^.*The post.*appeared.*$',
        r'^.*بازنویسی می‌کنم.*$',
        r'^.*تمرکز بر سردبیری.*$',
        r'^.*مناسب برای تیتر.*$',
        r'^.*بار دراماتیک.*$',
        r'^.*مخاطب را به خواندن.*$',
        r'^.*عنوان:\s*$',
        r'^.*محتوا:\s*$',
        r'^.*پیوند اول:.*$',
        r'^.*اطلاعات تکمیلی:\s*$',
        r'^.*توضیحات\s*\(Meta Description\).*$',
        r'^.*در صورتی که خبرگزاری.*$',
        r'^.*تاریخ انتشار.*در انتهای متن.*$',
        r'^.*درج واضح منبع.*$',
        r'^.*استفاده از لیست.*$',
        r'^.*استفاده از جملات کوتاه.*$',
        r'^.*عنوان \(Title\).*$',
        r'^.*عنوان خبری و مستقیم.*$',
        r'^.*محتوای بازنویسی شده.*$',
        r'^.*هشدار شدید حقوق بشر.*$',
        r'^.*عنوان اصلی \(پیشنهادی.*$',
        r'^.*چرا\?\?.*$',
        r'^.*گستردگی را نشان.*$',
        r'^.*احساس فوریت و اهمیت.*$',
        r'^.*کلمات کلیدی قوی.*$',
        r'^.*موتورهای جستجو.*مفید.*$',
        r'^.*کمک می‌کند تا اطلاعات.*$',
        r'^.*حفظ اعتبار.*$',
        r'^.*سئو بسیار مهم.*$',
        r'^.*در یک سناریوی واقعی.*$',
        r'^.*رعایت شده.*$',
        r'^.*خبرگزاری در ابتدای.*$',
        r'^.*اضافه کردن نام.*$',
        r'^.*توضیح:.*در خروجی بالا.*$',
        r'^.*در پاراگراف اول پوشش.*$',
        r'^.*صفحه به صورت ضمنی.*$',
        r'^.*منابع معتبر.*دیده می‌شود.*$',
        r'^.*جذابیت یا اطلاعاتی ندارد.*$',
        r'^.*عبارت به طور معمول.*$',
        r'^.*حاوی کلمات کلیدی اصلی.*$',
    ]
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            clean_lines.append(line)
            continue
        is_noise = False
        for pattern in noise_patterns:
            if re.search(pattern, stripped):
                is_noise = True
                break
        if not is_noise:
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def clean_html_content(html):
    """Processes HTML content by extracting paragraph texts, cleaning them, and re-building HTML."""
    if not html:
        return html
    
    # 1. First extract existing figure or images to preserve them
    figures = re.findall(r'(<figure style=".*?">.*?</figure>)', html, re.DOTALL)
    image_divs = re.findall(r'(<div style="text-align:center;.*?">.*?</div>)', html, re.DOTALL)
    simple_imgs = re.findall(r'(<img src=".*?"\s*/>)', html)
    
    # Find all paragraph texts
    # Matches <p style="...">Text</p>
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
    
    if not paragraphs:
        # Fallback: if not using standard p tags, split by <br> or double newlines
        plain_text = re.sub(r'<[^>]+>', '\n', html)
        paragraphs = [p.strip() for p in plain_text.split('\n') if p.strip()]
        
    cleaned_paragraphs = []
    for p in paragraphs:
        # Remove any HTML tags inside paragraph first
        text = re.sub(r'<[^>]+>', '', p).strip()
        if not text:
            continue
        # Apply cleanups
        text = strip_ai_noise(text)
        text = strip_markdown(text)
        if text:
            cleaned_paragraphs.append(text)
            
    # Re-build beautiful paragraphs
    formatted_p = []
    for p in cleaned_paragraphs:
        formatted_p.append(f'<p style="margin-bottom:18px;">{p}</p>')
    
    new_body = "\n".join(formatted_p)
    
    # Prepend figures or images back if they existed
    lead_media = ""
    if figures:
        lead_media = figures[0]
    elif image_divs:
        lead_media = image_divs[0]
    elif simple_imgs:
        lead_media = f'<div style="margin-bottom:25px;text-align:center;">{simple_imgs[0]}</div>'
        
    if lead_media:
        # Remove any duplicated media in the body if it got caught
        new_body = re.sub(r'<img[^>]+src="[^"]+"[^>]*>', '', new_body)
        new_body = lead_media + "\n" + new_body
        
    return new_body

def run_markdown_fix():
    safe_print("=" * 60)
    safe_print("  Live Posts Markdown & AI Noise Cleaner")
    safe_print("=" * 60)

    poster = BloggerPoster()
    safe_print(f"Connected to Blog ID: {poster.blog_id}")

    # Fetch last 30 posts to check and fix
    safe_print("Fetching last 30 posts from weblog...")
    try:
        response = poster.service.posts().list(blogId=poster.blog_id, maxResults=30).execute()
        items = response.get('items', [])
    except Exception as e:
        safe_print(f"Error fetching posts: {e}")
        return

    safe_print(f"Found {len(items)} posts to audit.")
    fixed_count = 0

    for idx, item in enumerate(items):
        post_id = item["id"]
        old_title = item.get("title", "")
        old_content = item.get("content", "")
        labels = item.get("labels", [])

        # Clean title
        new_title = strip_markdown(old_title)
        new_title = strip_ai_noise(new_title)
        
        # Clean content
        new_content = clean_html_content(old_content)

        # Check if there are changes
        title_changed = (old_title.strip() != new_title.strip())
        content_changed = (old_content.strip() != new_content.strip())

        if title_changed or content_changed:
            safe_print(f"\n[{idx+1}/30] Fixing Post ID: {post_id}")
            if title_changed:
                safe_print(f"  Old Title: '{old_title}'")
                safe_print(f"  New Title: '{new_title}'")
            if content_changed:
                safe_print(f"  Content cleaning required (Markdown or AI Noise found).")

            try:
                body = {
                    'id': post_id,
                    'title': new_title,
                    'content': new_content,
                    'labels': labels
                }
                
                poster.service.posts().update(
                    blogId=poster.blog_id,
                    postId=post_id,
                    body=body
                ).execute()

                safe_print(f"  [SUCCESS] Post updated successfully!")
                fixed_count += 1
                time.sleep(1.5) # small delay to avoid rate limit
            except Exception as e:
                safe_print(f"  [ERROR] Failed to update post {post_id}: {e}")
        else:
            # safe_print(f"[{idx+1}/30] Post '{old_title[:40]}...' is clean.")
            pass

    safe_print("\n" + "=" * 60)
    safe_print(f"  Audit completed. Successfully cleaned {fixed_count} live posts!")
    safe_print("=" * 60)

if __name__ == '__main__':
    run_markdown_fix()
