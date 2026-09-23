"""Choose article-specific images and verify their bytes before publication."""
import json
import re
from io import BytesIO
from urllib.parse import urljoin, urlsplit

import requests
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_BYTES = 12 * 1024 * 1024


class ImageUnavailable(RuntimeError):
    pass


def image_url(value, page_url=''):
    if not isinstance(value, str) or not value.strip():
        return ''
    try:
        url = urljoin(page_url, value.strip())
        parts = urlsplit(url)
        if parts.scheme not in ('https', 'http') or not parts.hostname or parts.username:
            return ''
        # Never reuse the site's logo, sharing icons or tracking placeholders as news photos.
        if re.search(r'/plugins/|gravatar|favicon|site[-_]icon|/logo[^/]*[.]|cropped-----|placeholder', url, re.I):
            return ''
        return url
    except ValueError:
        return ''


def article_image_candidates(soup, page_url, hints=()):
    """Article JSON-LD wins over site-wide og:image (broken on humanrightsinir)."""
    candidates = []

    def add(value):
        if isinstance(value, list):
            for entry in value:
                add(entry)
        elif isinstance(value, dict):
            add(value.get('url') or value.get('contentUrl') or '')
        else:
            url = image_url(value, page_url)
            if url and url not in candidates:
                candidates.append(url)

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or script.get_text())
            nodes = data if isinstance(data, list) else data.get('@graph', [data])
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                kinds = node.get('@type', [])
                kinds = [kinds] if isinstance(kinds, str) else kinds
                if any(k in ('Article', 'NewsArticle', 'BlogPosting', 'ReportageNewsArticle') for k in kinds):
                    add(node.get('image'))
        except (ValueError, TypeError, AttributeError):
            continue
    for img in soup.select('img.wp-post-image, .post-thumbnail img, .featured-image img, .single-post-content img, .entry-content img'):
        if any(str(img.get(k, '')).isdigit() and int(img[k]) < 100 for k in ('width', 'height')):
            continue
        add(img.get('data-src') or img.get('data-lazy-src') or img.get('src'))
    for hint in hints:
        add(hint)
    for meta in soup.select('meta[property="og:image"], meta[name="twitter:image"]'):
        add(meta.get('content'))
    return candidates


def verified_image(candidates, session):
    """Return the directly usable URL; never nest image proxies or emit a broken img."""
    urls = list(dict.fromkeys(u for value in candidates if (u := image_url(value))))
    if not urls:
        return ''
    for url in urls[:5]:
        try:
            with session.get(url, timeout=(10, 20), stream=True) as response:
                if response.status_code != 200 or not response.headers.get('Content-Type', '').lower().startswith('image/'):
                    continue
                data = bytearray()
                for chunk in response.iter_content(65536):
                    data.extend(chunk)
                    if len(data) > MAX_IMAGE_BYTES:
                        raise ImageUnavailable('Image exceeds size limit')
                with Image.open(BytesIO(data)) as picture:
                    if picture.width < 200 or picture.height < 100:
                        continue
                    picture.verify()
                # JPEG verify() only checks headers; decode to reject truncated files too.
                with Image.open(BytesIO(data)) as picture:
                    picture.load()
                return image_url(response.url) or url
        except (requests.RequestException, OSError, ValueError, UnidentifiedImageError,
                Image.DecompressionBombError, ImageUnavailable):
            continue
    raise ImageUnavailable('No usable article image; publication deferred for retry')
