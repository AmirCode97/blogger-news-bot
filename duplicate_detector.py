"""Persistent URL identities and conservative near-duplicate matching."""
import hashlib
import json
import os
import re
from datetime import timedelta
from difflib import SequenceMatcher
from article_utils import atomic_json, canonical_url, normalize_text, parse_datetime, utc_now

class DuplicateDetector:
    def __init__(self, cache_file='duplicate_cache.json'):
        self.cache_file = cache_file
        self.published_entries = []
        self.seen_urls, self.full_titles, self.content_hashes = set(), set(), set()
        if os.path.exists(cache_file):
            with open(cache_file, encoding='utf-8') as stream:
                data = json.load(stream)
            self.published_entries = data.get('published_entries', [])
            self.seen_urls = {canonical_url(u) for u in data.get('seen_urls', []) if canonical_url(u)}
            self.full_titles = set(data.get('full_titles', []))
        self._index()

    def _index(self):
        for entry in self.published_entries:
            url = canonical_url(entry.get('url', ''))
            if url:
                self.seen_urls.add(url)
            for field in ('title', 'original_title'):
                if entry.get(field):
                    self.full_titles.add(entry[field])
            if entry.get('content_hash'):
                self.content_hashes.add(entry['content_hash'])

    def _save_cache(self):
        atomic_json(self.cache_file, {'version': 2, 'seen_urls': sorted(self.seen_urls),
                    'full_titles': sorted(self.full_titles), 'published_entries': self.published_entries,
                    'last_updated': utc_now().isoformat()})

    def _normalize_title(self, title):
        return re.sub(r'[^\w\s]', '', normalize_text(title))

    def _normalize_url(self, url):
        return canonical_url(url)

    def _get_content_hash(self, content):
        return hashlib.sha256(normalize_text(content).encode()).hexdigest()

    def _title_similarity(self, a, b):
        return SequenceMatcher(None, self._normalize_title(a), self._normalize_title(b)).ratio()

    def is_duplicate(self, title, url, content='', published=None):
        if canonical_url(url) in self.seen_urls:
            return True, 'Source URL already published'
        if len(content) >= 150 and self._get_content_hash(content) in self.content_hashes:
            return True, 'Identical source content'
        normalized = self._normalize_title(title)
        now = utc_now()
        for entry in reversed(self.published_entries[-2000:]):
            when = parse_datetime(entry.get('timestamp'))
            if when and now - when > timedelta(days=7):
                continue
            source_date = parse_datetime(published)
            other_date = parse_datetime(entry.get('source_published'))
            if source_date and other_date and abs(source_date - other_date) > timedelta(hours=36):
                continue
            for old in (entry.get('original_title', ''), entry.get('title', '')):
                if not old:
                    continue
                other = self._normalize_title(old)
                if normalized == other:
                    return True, 'Identical recent title'
                a, b = set(normalized.split()), set(other.split())
                same_numbers = re.findall(r'\d+', normalized) == re.findall(r'\d+', other)
                if min(len(a), len(b)) >= 7 and same_numbers and a == b and self._title_similarity(title, old) >= .90:
                    return True, 'Same recent title words'
        return False, 'New article'

    def mark_as_published(self, title, url, content='', post_id='', original_title='', source_published=None):
        canonical = canonical_url(url)
        if canonical and canonical in self.seen_urls:
            return
        self.published_entries.append({'title': title, 'original_title': original_title or title,
            'url': canonical, 'post_id': post_id, 'timestamp': utc_now().isoformat(),
            'source_published': source_published,
            'content_hash': self._get_content_hash(content) if len(content) >= 150 else ''})
        self._index()
        self._save_cache()

    def seed_from_posts(self, posts):
        """Read-only recovery after a cache miss or ambiguous Blogger insert."""
        from bs4 import BeautifulSoup
        existing_ids = {e.get('post_id') for e in self.published_entries}
        for post in posts:
            if post['id'] in existing_ids or 'آمار_زنده' in post.get('labels', []):
                continue
            soup = BeautifulSoup(post.get('content', ''), 'html.parser')
            marker = soup.select_one('[data-source-url]')
            self.published_entries.append({'title': post.get('title', ''),
                'original_title': marker.get('data-source-title', '') if marker else '',
                'url': canonical_url(marker.get('data-source-url', '')) if marker else '',
                'post_id': post['id'], 'timestamp': post.get('published', utc_now().isoformat()),
                'source_published': marker.get('data-source-published') if marker else None})
            existing_ids.add(post['id'])
        self._index()
        self._save_cache()

    def get_stats(self):
        return {'total_titles': len(self.full_titles), 'total_urls': len(self.seen_urls),
                'total_entries': len(self.published_entries)}
