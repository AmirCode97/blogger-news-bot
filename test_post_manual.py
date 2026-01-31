
from blogger_poster import BloggerPoster
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

def create_test_post():
    print("🚀 Starting Manual Post Test...")
    poster = BloggerPoster()
    
    # 1. Test Image URL (Wikimedia Commons)
    test_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_Homepage.svg/1200px-Google_Homepage.svg.png"
    
    # 2. Test Content with HTML
    title = "TEST POST: Does the image show?"
    content = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="{test_image}" alt="Test Image" style="max-width: 100%; border: 2px solid red;" />
    </div>
    <h2>This is a test post</h2>
    <p>We are testing if the <strong>HTML content</strong> and <em>Images</em> are rendering correctly in the new theme.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    """
    
    print("📝 Sending request to Blogger API...")
    result = poster.create_post(
        title=title,
        content=content,
        labels=['Test', 'Debug'],
        is_draft=True # Try draft first
    )
    
    if result:
        print(f"✅ Post created! URL: {result.get('url')}")
        print("Please check the blog explicitly for this post.")
    else:
        print("❌ Failed to create post.")

if __name__ == "__main__":
    create_test_post()
