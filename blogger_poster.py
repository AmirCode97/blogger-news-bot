
import os
import pickle
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import BLOG_ID, GOOGLE_CREDENTIALS_FILE

SCOPES = ['https://www.googleapis.com/auth/blogger']

class BloggerPoster:
    def __init__(self):
        self.blog_id = BLOG_ID
        self.service = None
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        token_base64 = os.environ.get('BLOGGER_TOKEN_BASE64')
        if token_base64:
            try:
                token_bytes = base64.b64decode(token_base64)
                self.creds = pickle.loads(token_bytes)
            except: pass

        if not self.creds and os.path.exists('token_auth_fixed.pickle'):
            with open('token_auth_fixed.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=8080, prompt='consent')
            
            with open('token_auth_fixed.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('blogger', 'v3', credentials=self.creds)

    def create_post(self, title, content, labels=None, is_draft=False):
        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': self.blog_id},
            'title': title,
            'content': content,
            'labels': labels or []
        }
        try:
            return self.service.posts().insert(
                blogId=self.blog_id, body=post_body, isDraft=is_draft
            ).execute()
        except Exception as e:
            print(f"[Error] Posting: {e}")
            return None

    def publish_draft(self, post_id):
        try:
            self.service.posts().publish(blogId=self.blog_id, postId=post_id).execute()
            return True
        except: return False
