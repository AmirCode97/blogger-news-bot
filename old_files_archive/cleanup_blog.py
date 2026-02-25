
import time
from blogger_poster import BloggerPoster

def cleanup_duplicates():
    print("Initializing Blogger connection for cleanup...")
    poster = BloggerPoster()
    
    print("Fetching all posts (Live and Draft)...")
    
    all_posts = []
    page_token = None
    
    while True:
        try:
            # Note: status='LIVE' or 'DRAFT'. To get both we might need separate calls or a list if supported.
            # Blogger API usually takes one status or a list. Let's try iterating statuses.
            # Actually, standard is usually one status per call or comma separated?? 
            # The python lib usually handles list for 'status' param if supported.
            # Let's try fetching LIVE first, then DRAFT.
            break # Logic handled below
        except:
             break
             
    # Implementation with separate loops for safety
    statuses = ['LIVE', 'DRAFT']
    for status in statuses:
        page_token = None
        while True:
            try:
                request = poster.service.posts().list(
                    blogId=poster.blog_id,
                    status=status,
                    maxResults=50,
                    pageToken=page_token
                )
                response = request.execute()
                items = response.get('items', [])
                all_posts.extend(items)
                
                print(f"  Fetched {len(items)} {status} posts...")
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            except Exception as e:
                print(f"Error fetching {status} posts: {e}")
                break
            
    print(f"Total posts found: {len(all_posts)}")
    
    # Group by title
    posts_by_title = {}
    for post in all_posts:
        title = post.get('title')
        if not title:
            continue
        
        # Normalize title (trim spaces)
        title = title.strip()
        
        if title not in posts_by_title:
            posts_by_title[title] = []
        posts_by_title[title].append(post)
        
    # Find duplicates
    print("\nChecking for duplicates...")
    duplicates_found = 0
    deleted_count = 0
    
    for title, posts in posts_by_title.items():
        if len(posts) > 1:
            duplicates_found += 1
            try:
                print(f"\n[Duplicate] Found {len(posts)} versions of: {title[:60]}...")
            except UnicodeEncodeError:
                print(f"\n[Duplicate] Found {len(posts)} versions of: [Title with special characters]...")
            
            # Sort by published date (newest first)
            # If date is missing (draft?), use 'updated'
            posts.sort(key=lambda x: x.get('published') or x.get('updated') or '', reverse=True)
            
            # Keep the newest one
            to_keep = posts[0]
            to_delete = posts[1:]
            
            print(f"  Keeping: ID {to_keep['id']} | Date: {to_keep.get('published') or to_keep.get('updated')} | Status: {to_keep.get('status')}")
            
            for p in to_delete:
                print(f"  Deleting: ID {p['id']} | Date: {p.get('published') or p.get('updated')} | Status: {p.get('status')}")
                try:
                    poster.delete_post(p['id'])
                    # poster class prints status
                    deleted_count += 1
                    time.sleep(0.5) # Avoid hitting rate limits
                except Exception as e:
                    print(f"    Failed to delete: {e}")
                
    if duplicates_found == 0:
        print("\nNo duplicates found.")
    else:
        print(f"\nCleanup complete. Found {duplicates_found} sets of duplicates. Deleted {deleted_count} posts.")

if __name__ == "__main__":
    cleanup_duplicates()
