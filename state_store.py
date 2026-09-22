"""Persist non-secret publication history on a dedicated GitHub branch, not an evictable cache."""
import base64
import json
import os
import sys
from pathlib import Path
import requests
from article_utils import atomic_json, utc_now

FILES = ('news_cache.json', 'duplicate_cache.json')
BRANCH = 'bot-state'
STATE_PATH = '.bot-state/state.json'

def validate_state(data):
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('Invalid state snapshot')
    files = data.get('files', {})
    if set(files) != set(FILES) or not all(isinstance(files[n], dict) for n in FILES):
        raise ValueError('Incomplete state snapshot')
    for name, keys in [('news_cache.json', ('seen_ids', 'seen_titles')),
                       ('duplicate_cache.json', ('seen_urls', 'published_entries'))]:
        if not all(isinstance(files[name].get(k), list) for k in keys):
            raise ValueError('Invalid state indexes')
    return files

class GitHubState:
    def __init__(self):
        self.base = 'https://api.github.com/repos/' + os.environ['GITHUB_REPOSITORY']
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
                                     'Accept': 'application/vnd.github+json'})

    def request(self, method, path, **kwargs):
        response = self.session.request(method, self.base + path, timeout=40, **kwargs)
        if response.status_code not in (200, 201, 404):
            raise RuntimeError(f'GitHub state {method} failed: HTTP {response.status_code}')
        return response

    def current(self):
        return self.request('GET', '/contents/' + STATE_PATH, params={'ref': BRANCH})

    def restore(self):
        response = self.current()
        if response.status_code == 404:
            print('[STATE] First durable-state run; retaining legacy cache, reconciling against Blogger')
            return
        metadata = response.json()
        if metadata.get('encoding') == 'base64' and metadata.get('content'):
            snapshot = json.loads(base64.b64decode(metadata['content']))
        else:
            # GitHub omits inline content above 1 MiB. Legacy publication history can exceed this.
            raw = self.request('GET', '/contents/' + STATE_PATH, params={'ref': BRANCH},
                               headers={'Accept': 'application/vnd.github.raw+json'})
            if raw.status_code != 200:
                raise RuntimeError('Could not download complete state snapshot')
            snapshot = raw.json()
        files = validate_state(snapshot)
        for path, data in files.items():
            atomic_json(path, data)
        print('[STATE] Restored durable publication history')

    def save(self):
        defaults = {'news_cache.json': {'seen_ids': [], 'seen_titles': []},
                    'duplicate_cache.json': {'seen_urls': [], 'published_entries': []}}
        files = {name: json.loads(Path(name).read_text(encoding='utf-8')) if Path(name).exists() else defaults[name]
                 for name in FILES}
        snapshot = {'version': 1, 'updated_at': utc_now().isoformat(), 'files': files}
        validate_state(snapshot)
        current = self.current()
        if current.status_code == 404:
            branch = self.request('GET', '/git/ref/heads/' + BRANCH)
            if branch.status_code == 404:
                head = self.request('GET', '/git/ref/heads/main')
                if head.status_code != 200:
                    raise RuntimeError('Cannot initialize state branch')
                self.request('POST', '/git/refs', json={'ref': 'refs/heads/' + BRANCH, 'sha': head.json()['object']['sha']})
        body = {'message': 'Save bot publication history', 'branch': BRANCH,
                'content': base64.b64encode(json.dumps(snapshot, ensure_ascii=False).encode()).decode()}
        if current.status_code == 200:
            body['sha'] = current.json()['sha']
        response = self.request('PUT', '/contents/' + STATE_PATH, json=body)
        if response.status_code not in (200, 201):
            raise RuntimeError('Could not persist publication history')
        print('[STATE] Publication history saved')

if __name__ == '__main__':
    store = GitHubState()
    if sys.argv[1:] == ['restore']:
        store.restore()
    elif sys.argv[1:] == ['save']:
        store.save()
    else:
        raise SystemExit('Usage: python state_store.py restore|save')
