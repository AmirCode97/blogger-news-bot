import os
import sys
import json
from urllib.parse import quote
from dotenv import load_dotenv

# Import the updated function from update_all_posts
from update_all_posts import build_related_posts_widget, extract_first_image, get_persian_date, clean_html_content
from blogger_poster import BloggerPoster

# Load config
load_dotenv()
BLOG_ID = os.getenv("BLOG_ID")

def main():
    blogger = BloggerPoster()
    service = blogger.service
    
    # The URL is https://iranpolnews.blogspot.com/2026/06/blog-post_875.html
    path = "/2026/06/blog-post_875.html"
    
    print(f"Fetching post with path: {path}")
    response = service.posts().getByPath(blogId=BLOG_ID, path=path).execute()
    
    post_id = response['id']
    post_title = response['title']
    print(f"Found post ID: {post_id} - {post_title}")
    
    # Fetch all posts for "related posts" logic
    all_response = service.posts().list(blogId=BLOG_ID, maxResults=50).execute()
    items = all_response.get('items', [])
    
    all_posts = []
    for it in items:
        lbls = it.get('labels', [])
        it_lbl = lbls[0] if lbls else "حقوق بشر"
        it_img = extract_first_image(it.get('content', ''), it_lbl, {})
        all_posts.append({
            'id': it['id'],
            'title': it['title'],
            'url': it.get('url', ''),
            'label': it_lbl,
            'image': it_img,
            'published': it.get('published', '')
        })
        
    post_labels = response.get('labels', [])
    current_label = post_labels[0] if post_labels else "حقوق بشر"
    
    # Find candidates
    candidates = []
    for cand in all_posts:
        if cand['id'] == post_id: continue
        overlap = 1 if cand['label'] in post_labels else 0
        candidates.append((overlap, cand))
        
    candidates.sort(key=lambda x: (x[0], x[1]['published']), reverse=True)
    
    selected_posts = []
    for _, cand in candidates[:3]:
        selected_posts.append({
            'title': cand['title'],
            'url': cand['url'],
            'label': cand['label'],
            'image': cand['image'],
            'date': get_persian_date(cand['published'])
        })
        
    # Build JS wrapper
    related_widget_html = build_related_posts_widget(selected_posts, current_label)
    
    paragraphs, main_image = clean_html_content(response['content'])
    if not main_image:
        main_image = extract_first_image(response['content'], current_label, {})
        
    if paragraphs:
        p0 = paragraphs[0].replace('**', '').replace('تیتر:', '').replace('عنوان:', '').strip()
        title = post_title.strip()
        if title in p0 or p0 in title:
            paragraphs = paragraphs[1:]
            
    lead_paragraph = paragraphs[0] if paragraphs else ""
    description_html = ""
    for p in paragraphs:
        description_html += f'<p style="margin-bottom:18px;">{p}</p>\n'
        
    # Schema
    schema_data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": post_title,
        "image": [main_image] if main_image else [],
        "description": lead_paragraph[:160] + "..." if len(lead_paragraph) > 160 else lead_paragraph
    }
    schema_script = f'<script type="application/ld+json">{json.dumps(schema_data, ensure_ascii=False)}</script>'
    
    tag_links = []
    for label in (post_labels if post_labels else [current_label]):
        tag_links.append(f'<a href="/search/label/{quote(label)}" style="color:#c0392b;text-decoration:none;margin-left:12px;font-weight:bold;transition:color 0.2s;" onmouseover="this.style.color=\'#e74c3c\'" onmouseout="this.style.color=\'#c0392b\'">#{label}</a>')
    tags_html = " ".join(tag_links)
    
    image_html = ""
    if main_image:
        image_html = f'''<figure style="margin:0 0 25px 0;text-align:center;">
    <img src="{main_image}" alt="{post_title}" title="{post_title}" loading="lazy" decoding="async" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);" />
    <figcaption style="display:none;">{post_title}</figcaption>
</figure>'''

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
    
    # Construct new HTML body
    new_html = f"""
    <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
    {schema_script}
    {image_html}
    
    <article style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
        <div>{description_html}</div>
    </article>
    
    {single_footer_html}
    
    {related_widget_html}
    """
    
    # Update Blogger
    update_body = {
        'title': post_title,
        'content': new_html,
        'labels': post_labels
    }
    
    print("Updating post on Blogger...")
    service.posts().update(blogId=BLOG_ID, postId=post_id, body=update_body).execute()
    print("Post updated successfully!")

if __name__ == "__main__":
    main()
