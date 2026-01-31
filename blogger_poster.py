"""
Blogger Poster Module
ماژول ارسال پست به وبلاگ Blogger
"""

import sys
import io
import os
import pickle
from typing import Dict, List, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import BLOG_ID, GOOGLE_CREDENTIALS_FILE


# Scopes needed for Blogger API
SCOPES = ['https://www.googleapis.com/auth/blogger']


class BloggerPoster:
    """Posts content to Google Blogger"""
    
    def __init__(self):
        self.blog_id = BLOG_ID
        self.service = None
        self.creds = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Blogger API"""
        token_file = 'token_auth_fixed.pickle'
        
        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(GOOGLE_CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Credentials file not found: {GOOGLE_CREDENTIALS_FILE}\n"
                        "Please download credentials.json from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CREDENTIALS_FILE, SCOPES
                )
                self.creds = flow.run_local_server(port=8080, prompt='consent')
            
            # Save credentials
            with open(token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Build service
        self.service = build('blogger', 'v3', credentials=self.creds)
        print("[OK] Authenticated with Blogger API")
    
    def get_blog_info(self) -> Optional[Dict]:
        """Get blog information"""
        try:
            blog = self.service.blogs().get(blogId=self.blog_id).execute()
            return {
                'name': blog.get('name'),
                'url': blog.get('url'),
                'posts_count': blog.get('posts', {}).get('totalItems', 0),
                'pages_count': blog.get('pages', {}).get('totalItems', 0)
            }
        except HttpError as e:
            print(f"[Error] Getting blog info: {e}")
            return None
    
    def create_post(self, title: str, content: str, labels: List[str] = None, 
                    is_draft: bool = True) -> Optional[Dict]:
        """
        Create a new blog post
        
        Args:
            title: Post title
            content: HTML content
            labels: List of tags/labels
            is_draft: If True, saves as draft (for review)
        
        Returns:
            Post data or None if failed
        """
        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': self.blog_id},
            'title': title,
            'content': content,
        }
        
        if labels:
            post_body['labels'] = labels
        
        try:
            post = self.service.posts().insert(
                blogId=self.blog_id,
                body=post_body,
                isDraft=is_draft
            ).execute()
            
            status = "[Draft]" if is_draft else "[Published]"
            print(f"{status}: {title}")
            
            return {
                'id': post.get('id'),
                'title': post.get('title'),
                'url': post.get('url'),
                'status': 'draft' if is_draft else 'published',
                'published': post.get('published'),
                'labels': post.get('labels', [])
            }
            
        except HttpError as e:
            print(f"[Error] Creating post: {e}")
            return None
    
    def publish_draft(self, post_id: str) -> bool:
        """Publish a draft post"""
        try:
            self.service.posts().publish(
                blogId=self.blog_id,
                postId=post_id
            ).execute()
            print(f"[Published] Post ID: {post_id}")
            return True
        except HttpError as e:
            print(f"[Error] Publishing post: {e}")
            return False
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post"""
        try:
            self.service.posts().delete(
                blogId=self.blog_id,
                postId=post_id
            ).execute()
            print(f"[Deleted] Post ID: {post_id}")
            return True
        except HttpError as e:
            print(f"[Error] Deleting post: {e}")
            return False
    
    def get_drafts(self) -> List[Dict]:
        """Get all draft posts"""
        try:
            result = self.service.posts().list(
                blogId=self.blog_id,
                status='DRAFT'
            ).execute()
            
            posts = result.get('items', [])
            return [{
                'id': p.get('id'),
                'title': p.get('title'),
                'updated': p.get('updated')
            } for p in posts]
            
        except HttpError as e:
            print(f"[Error] Getting drafts: {e}")
            return []
    
    def get_recent_posts(self, max_results: int = 10) -> List[Dict]:
        """Get recent published posts"""
        try:
            result = self.service.posts().list(
                blogId=self.blog_id,
                status='LIVE',
                maxResults=max_results
            ).execute()
            
            posts = result.get('items', [])
            return [{
                'id': p.get('id'),
                'title': p.get('title'),
                'url': p.get('url'),
                'published': p.get('published')
            } for p in posts]
            
        except HttpError as e:
            print(f"[Error] Getting posts: {e}")
            return []
    
    def test_connection(self):
        """Test the connection to Blogger API"""
        info = self.get_blog_info()
        if info:
            print(f"\n[SUCCESS] Connected to blog!")
            print(f"Blog Name: {info['name']}")
            print(f"URL: {info['url']}")
            print(f"Total Posts: {info['posts_count']}")
            return True
        return False


# Test the poster
if __name__ == "__main__":
    try:
        poster = BloggerPoster()
        
        # Get blog info
        info = poster.get_blog_info()
        if info:
            print(f"\nBlog: {info['name']}")
            print(f"URL: {info['url']}")
            print(f"Posts: {info['posts_count']}")
        
        # Get drafts
        drafts = poster.get_drafts()
        if drafts:
            print(f"\nDrafts ({len(drafts)}):")
            for d in drafts:
                print(f"  - {d['title']}")
        
    except FileNotFoundError as e:
        print(f"\n[Warning] {e}")
        print("\nTo set up Blogger API:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project")
        print("3. Enable Blogger API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download and save as 'credentials.json'")
