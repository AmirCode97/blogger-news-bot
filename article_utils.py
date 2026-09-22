"""Article identity, text and timezone handling."""
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')

def normalize_text(value):
    value = unescape(value or '').translate(DIGITS).replace('ي', 'ی').replace('ك', 'ک')
    return re.sub(r'\s+', ' ', value.replace('\u200c', ' ').replace('\u200f', '')).strip().lower()

def canonical_url(value):
    parts = urlsplit(value or '')
    if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username:
        return ''
    host = parts.netloc.lower().removeprefix('www.')
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in ('fbclid', 'gclid')]
    return urlunsplit(('https', host, parts.path.rstrip('/') or '/', urlencode(sorted(query)), ''))

def article_key(url):
    canonical = canonical_url(url)
    if not canonical:
        raise ValueError('Article requires an HTTP(S) source URL')
    return hashlib.sha256(canonical.encode()).hexdigest()

def parse_datetime(value):
    if isinstance(value, datetime):
        result = value
    elif not value:
        return None
    else:
        try:
            result = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except ValueError:
            try:
                result = parsedate_to_datetime(str(value))
            except (ValueError, TypeError, OverflowError):
                return None
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)

def utc_now():
    return datetime.now(timezone.utc)

def atomic_json(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)

def plain_article_text(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html or '', 'html.parser')
    for node in soup.select('script,style,nav,footer,aside,form,.related-posts-widget,.sharedaddy'):
        node.decompose()
    container = soup.select_one('article') or soup
    blocks = container.find_all(['p', 'h2', 'h3', 'li'])
    texts = [b.get_text(' ', strip=True) for b in blocks] if blocks else [container.get_text(' ', strip=True)]
    return '\n\n'.join(dict.fromkeys(t for t in texts if t))
