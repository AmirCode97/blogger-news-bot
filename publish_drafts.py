"""
Publish all drafts script
اسکریپت انتشار همه پیش‌نویس‌ها
"""

import time
import os
import pickle
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Settings
BLOG_ID = "1276802394255833723"
SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_service():
    """Get authenticated Blogger service"""
    token_file = 'token.pickle'
    creds = None
    
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('blogger', 'v3', credentials=creds)

def publish_all_drafts():
    service = get_service()
    print("Authenticated!")
    
    try:
        # Get all drafts
        result = service.posts().list(blogId=BLOG_ID, status='DRAFT').execute()
        drafts = result.get('items', [])
        
        print(f"Found {len(drafts)} drafts")
        print()
        
        # Publish each draft
        published = 0
        for i, draft in enumerate(drafts, 1):
            title = draft.get('title', 'Untitled')
            # Safe print for console
            safe_title = title.encode('ascii', 'replace').decode() if os.name == 'nt' else title
            post_id = draft.get('id')
            
            print(f"[{i}/{len(drafts)}] Publishing...")
            
            try:
                service.posts().publish(blogId=BLOG_ID, postId=post_id).execute()
                print("   -> Published!")
                published += 1
            except HttpError as e:
                print(f"   -> Failed: {e}")
            
            time.sleep(2)  # Delay to avoid rate limit
        
        print()
        print(f"Done! Published {published}/{len(drafts)} posts.")
        print()
        print("View your blog at: http://iranpolnews.blogspot.com/")
        
    except HttpError as e:
        print(f"Error listing drafts: {e}")

if __name__ == "__main__":
    publish_all_drafts()
