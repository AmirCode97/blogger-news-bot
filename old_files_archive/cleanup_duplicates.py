"""
Find and Delete Duplicate Posts from Blogger
یافتن و حذف پست‌های تکراری از بلاگر

This script:
1. Fetches all posts from the blog
2. Identifies duplicates using title similarity
3. Shows duplicates for review
4. Deletes duplicate posts (keeping the original)
"""

import os
import sys
import pickle
import re
from datetime import datetime
from difflib import SequenceMatcher
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")
SIMILARITY_THRESHOLD = 0.80  # 80% similarity = duplicate

def normalize_title(title):
    """Normalize title for comparison"""
    title = re.sub(r'^(خبر|گزارش|ویدیو|عکس|فوری)[:\s]+', '', title)
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title.lower()

def title_similarity(title1, title2):
    """Calculate similarity between two titles"""
    t1 = normalize_title(title1)
    t2 = normalize_title(title2)
    return SequenceMatcher(None, t1, t2).ratio()

def main():
    print("=" * 70)
    print("🔍 FINDING AND REMOVING DUPLICATE POSTS")
    print("=" * 70)
    
    # Init Blogger API
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('blogger', 'v3', credentials=creds)
    
    # Fetch ALL posts
    print("\n📥 Fetching all posts from blog...")
    all_posts = []
    page_token = None
    
    while True:
        result = service.posts().list(
            blogId=BLOG_ID,
            maxResults=50,
            pageToken=page_token
        ).execute()
        
        posts = result.get('items', [])
        all_posts.extend(posts)
        
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    
    print(f"📊 Found {len(all_posts)} total posts")
    
    # Find duplicates
    print("\n🔎 Analyzing for duplicates...")
    duplicates_to_delete = []
    seen_titles = {}  # title -> post info (keep first/oldest)
    
    # Sort by published date (oldest first) so we keep the original
    all_posts.sort(key=lambda x: x.get('published', ''), reverse=False)
    
    for post in all_posts:
        title = post.get('title', '')
        post_id = post.get('id', '')
        url = post.get('url', '')
        published = post.get('published', '')[:10]  # Just the date
        
        normalized = normalize_title(title)
        
        # Check for exact match first
        if normalized in seen_titles:
            original = seen_titles[normalized]
            duplicates_to_delete.append({
                'id': post_id,
                'title': title,
                'url': url,
                'published': published,
                'reason': 'Exact title match',
                'original_title': original['title']
            })
            continue
        
        # Check for similar titles
        is_duplicate = False
        for seen_normalized, seen_info in seen_titles.items():
            similarity = SequenceMatcher(None, normalized, seen_normalized).ratio()
            if similarity >= SIMILARITY_THRESHOLD:
                duplicates_to_delete.append({
                    'id': post_id,
                    'title': title,
                    'url': url,
                    'published': published,
                    'reason': f'Similar ({similarity:.0%})',
                    'original_title': seen_info['title']
                })
                is_duplicate = True
                break
        
        if not is_duplicate:
            seen_titles[normalized] = {
                'id': post_id,
                'title': title,
                'url': url
            }
    
    # Report findings
    print(f"\n📋 RESULTS:")
    print(f"   • Total posts: {len(all_posts)}")
    print(f"   • Unique posts: {len(seen_titles)}")
    print(f"   • Duplicates found: {len(duplicates_to_delete)}")
    
    if not duplicates_to_delete:
        print("\n✅ No duplicates found! Blog is clean.")
        return
    
    # Show duplicates
    print("\n" + "=" * 70)
    print("🗑️  DUPLICATES TO DELETE:")
    print("=" * 70)
    
    for i, dup in enumerate(duplicates_to_delete, 1):
        print(f"\n{i}. {dup['title'][:60]}...")
        print(f"   📅 Published: {dup['published']}")
        print(f"   🔗 URL: {dup['url']}")
        print(f"   ⚠️  Reason: {dup['reason']}")
        print(f"   📄 Original: {dup['original_title'][:50]}...")
    
    # Confirm deletion
    print("\n" + "=" * 70)
    print(f"⚠️  WARNING: About to delete {len(duplicates_to_delete)} duplicate posts!")
    print("=" * 70)
    
    # Auto-confirm for this run
    confirm = input("\nType 'DELETE' to confirm deletion: ")
    
    if confirm.strip().upper() != 'DELETE':
        print("❌ Deletion cancelled.")
        return
    
    # Delete duplicates
    print("\n🗑️  Deleting duplicates...")
    deleted_count = 0
    
    for dup in duplicates_to_delete:
        try:
            service.posts().delete(
                blogId=BLOG_ID,
                postId=dup['id']
            ).execute()
            
            print(f"   ✅ Deleted: {dup['title'][:50]}...")
            deleted_count += 1
            
        except Exception as e:
            print(f"   ❌ Error deleting {dup['id']}: {e}")
    
    print(f"\n✅ DONE! Deleted {deleted_count} duplicate posts.")
    print(f"📊 Remaining posts: {len(all_posts) - deleted_count}")

if __name__ == "__main__":
    main()
