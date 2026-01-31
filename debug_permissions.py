
from blogger_poster import BloggerPoster
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

def debug_permissions():
    print("🚀 Debugging Permissions...")
    poster = BloggerPoster()
    service = poster.service
    
    print("\n1. Testing READ access (Get Blog Info)...")
    try:
        blog = service.blogs().get(blogId=poster.blog_id).execute()
        print(f"✅ READ Success! Blog Name: {blog.get('name')}")
    except Exception as e:
        print(f"❌ READ Failed: {e}")
        
    print("\n2. Testing WRITE access (Create Draft)...")
    try:
        post = service.posts().insert(
            blogId=poster.blog_id,
            body={
                'title': 'Debug Permission Test',
                'content': 'Testing permissions...',
                'blog': {'id': poster.blog_id}
            },
            isDraft=True
        ).execute()
        print(f"✅ WRITE Success! Draft created ID: {post.get('id')}")
    except Exception as e:
        print(f"❌ WRITE Failed: {e}")
        print("\nPossible causes:")
        print("- You signed in with the wrong Google account.")
        print("- You dind't 'Allow' the app to manage your posts.")
        print("- The API Console project doesn't have the Blogger API enabled (unlikely if Read works).")

if __name__ == "__main__":
    debug_permissions()
