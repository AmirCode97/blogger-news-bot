"""Choose article-specific images and verify their bytes before publication."""
import json
import re
from io import BytesIO
from urllib.parse import urljoin, urlsplit

import requests
from PIL import Image, UnidentifiedImageError
from article_utils import canonical_url

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
    """Resolve the current article's schema image; never scan site-wide thumbnails."""
    candidates = []
    nodes = []

    def collect(value):
        if isinstance(value, list):
            for node in value:
                collect(node)
        elif isinstance(value, dict):
            nodes.append(value)
            collect(value.get('@graph'))

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            collect(json.loads(script.string or script.get_text()))
        except (ValueError, TypeError):
            continue
    references = {urljoin(page_url, node['@id']): node for node in nodes
                  if isinstance(node.get('@id'), str)}

    def add(value, visited=frozenset()):
        if isinstance(value, list):
            for entry in value:
                add(entry, visited)
        elif isinstance(value, dict):
            direct = value.get('contentUrl') or value.get('url')
            if direct:
                add(direct, visited)
            else:
                ref = value.get('@id')
                if isinstance(ref, str):
                    key = urljoin(page_url, ref)
                    if key in references and key not in visited:
                        add(references[key], visited | {key})
        elif isinstance(value, str):
            key = urljoin(page_url, value)
            if key in references:
                if key not in visited:
                    add(references[key], visited | {key})
                return
            if value.startswith('#'):
                return
            url = image_url(value, page_url)
            if url and url not in candidates:
                candidates.append(url)

    def is_current_page(node):
        # A page can also describe related articles; their images are not fallbacks.
        identity = node.get('mainEntityOfPage') or node.get('url') or node.get('@id')
        if isinstance(identity, dict):
            identity = identity.get('@id') or identity.get('url')
        if not isinstance(identity, str):
            return True
        try:
            return canonical_url(urljoin(page_url, identity)) == canonical_url(page_url)
        except ValueError:
            return False

    for node in nodes:
        kinds = node.get('@type', [])
        kinds = [kinds] if isinstance(kinds, str) else kinds
        if not isinstance(kinds, list) or not is_current_page(node):
            continue
        if any(k in ('Article', 'NewsArticle', 'BlogPosting', 'ReportageNewsArticle') for k in kinds):
            add(node.get('image'))
            add(node.get('thumbnailUrl'))

    def ancillary(element):
        for parent in [element, *element.parents]:
            if parent.name in ('aside', 'nav', 'footer'):
                return True
            markers = ' '.join(parent.get('class', [])) + ' ' + str(parent.get('id', ''))
            if re.search(r'sidebar|widget|relate[dt]|recommend|comment|share|social', markers, re.I):
                return True
        return False

    # HRANA's .single-page contains the featured photo above .single-post-content.
    # On other WordPress themes, use the article with the page heading or its body.
    root = next((node for node in soup.select('.single-page, article')
                 if not ancillary(node) and ('single-page' in node.get('class', []) or node.find('h1'))), None)
    if root is None:
        root = next((node for node in soup.select(
            '.single-post-content, .entry-content, .td-post-content, .post-content')
            if not ancillary(node)), None)

    def add_img(img):
        if ancillary(img):
            return
        # Nested article cards are separate stories, even inside the main article.
        owner = img.find_parent('article')
        if owner is not None and owner is not root and root in owner.parents:
            return
        if any(str(img.get(k, '')).isdigit() and int(img[k]) < 100 for k in ('width', 'height')):
            return
        add(img.get('data-src') or img.get('data-lazy-src') or img.get('src'))

    if root is not None:
        for img in root.select('img.wp-post-image, .post-thumbnail img, .featured-image img'):
            add_img(img)
    for hint in hints:
        add(hint)
    for meta in soup.select('meta[property="og:image"], meta[name="twitter:image"]'):
        add(meta.get('content'))
    if root is not None:
        for img in root.select('img'):
            add_img(img)
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
