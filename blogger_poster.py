
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
                if os.getenv('GITHUB_ACTIONS') or os.getenv('CI'):
                    raise RuntimeError('Blogger token is missing/invalid; renew BLOGGER_TOKEN_BASE64 locally with reauth.py')
                flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=8080, prompt='consent')
            
            with open('token_auth_fixed.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('blogger', 'v3', credentials=self.creds)

    def create_post(self, title, content, labels=None, is_draft=False, published_date=None):
        post_body = {
            'kind': 'blogger#post',
            'blog': {'id': self.blog_id},
            'title': title,
            'content': content,
            'labels': labels or []
        }
        if published_date:
            post_body['published'] = published_date
            
        try:
            return self.service.posts().insert(
                blogId=self.blog_id, body=post_body, isDraft=is_draft
            ).execute()
        except Exception as e:
            print(f"[Error] Posting: {e}")
            return None

    def create_post_with_slug(self, slug, title, content, labels=None):
        """Blogger's API has no custom-permalink field: publish under the slug first.

        Once published, changing the title keeps its permalink. The article carries
        recovery metadata so a failed title patch can be retried on the next run.
        """
        result = self.create_post(title=slug, content=content, labels=labels, is_draft=False)
        if not result or not result.get('id'):
            raise RuntimeError('Blogger insert failed; retry only after next-run reconciliation')
        updated = self.update_post_title(result['id'], title)
        if not updated or updated.get('title') != title:
            raise RuntimeError(f"Blogger created post {result['id']} but title update failed; recovery will retry")
        if 'blog-post' in result.get('url', '').rsplit('/', 1)[-1]:
            print(f"[PERMALINK WARNING] Blogger returned a generic URL for post {result['id']}")
        updated.setdefault('id', result['id'])
        return updated

    def publish_draft(self, post_id):
        try:
            self.service.posts().publish(blogId=self.blog_id, postId=post_id).execute()
            return True
        except: return False

    def list_posts(self, start_date=None, labels=None):
        """Read published posts only; all pages or an explicit failure (never partial stats)."""
        posts = []
        token = None
        for _ in range(100):
            options = {'blogId': self.blog_id, 'maxResults': 100, 'fetchBodies': True,
                       'status': 'LIVE', 'orderBy': 'PUBLISHED'}
            if start_date:
                options['startDate'] = start_date
            if labels:
                options['labels'] = labels
            if token:
                options['pageToken'] = token
            response = self.service.posts().list(**options).execute(num_retries=2)
            posts.extend(response.get('items', []))
            token = response.get('nextPageToken')
            if not token:
                return posts
        raise RuntimeError('Blogger pagination limit reached; refusing incomplete results')

    def update_post_title(self, post_id, new_title):
        try:
            post_body = {'title': new_title}
            return self.service.posts().patch(
                blogId=self.blog_id, postId=post_id, body=post_body
            ).execute(num_retries=2)
        except Exception as e:
            print(f"[Error] Updating post title: {e}")
            return None
