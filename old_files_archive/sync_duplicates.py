"""
Sync duplicate detector database with existing blog posts
همگام‌سازی دیتابیس تشخیص تکرار با پست‌های موجود

This script reads all existing blog posts and adds them to the duplicate detector
to prevent re-publishing existing content.
"""

import os
import sys
import pickle
from googleapiclient.discovery import build
from dotenv import load_dotenv
from duplicate_detector import DuplicateDetector

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

def sync_with_blog():
    print("=" * 60)
    print("SYNCING DUPLICATE DETECTOR WITH EXISTING BLOG POSTS")
    print("=" * 60)
    
    # Init detector
    detector = DuplicateDetector()
    print(f"\nCurrent stats: {detector.get_stats()}")
    
    # Init Blogger API
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('blogger', 'v3', credentials=creds)
    
    # Fetch all posts
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
    
    print(f"\nFound {len(all_posts)} existing posts in blog")
    
    # Add each post to detector
    added = 0
    for post in all_posts:
        title = post.get('title', '')
        url = post.get('url', '')
        content = post.get('content', '')[:500]  # First 500 chars for fingerprint
        post_id = post.get('id', '')
        
        # Check if already in detector
        is_dup, _ = detector.is_duplicate(title, url)
        if not is_dup:
            detector.mark_as_published(
                title=title,
                url=url,
                content=content,
                post_id=post_id
            )
            added += 1
            print(f"  + Added: {title[:50]}...")
    
    print(f"\n✅ Synced! Added {added} new entries to detector")
    print(f"Final stats: {detector.get_stats()}")

if __name__ == "__main__":
    sync_with_blog()
