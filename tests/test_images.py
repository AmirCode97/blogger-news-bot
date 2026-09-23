import json
import base64
import re
from io import BytesIO
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup
from PIL import Image

from article_images import article_image_candidates, image_url, verified_image, ImageUnavailable
from main import build_post_html
from news_fetcher import NewsFetcher
from test_bot import IsolatedTest, BODY


class ImageTests(IsolatedTest):
    def response(self, data=None, status=200, content_type='image/jpeg', url='https://example.org/photo.jpg'):
        if data is None:
            buffer = BytesIO()
            Image.new('RGB', (640, 420), 'navy').save(buffer, format='JPEG')
            data = buffer.getvalue()
        response = Mock(status_code=status, headers={'Content-Type': content_type}, url=url)
        response.iter_content.return_value = [data]
        context = Mock()
        context.__enter__ = Mock(return_value=response)
        context.__exit__ = Mock(return_value=False)
        return context

    def test_article_schema_precedes_broken_site_logo(self):
        photo = 'https://i0.wp.com/example.org/person.jpg?fit=1280%2C852&ssl=1'
        schema = {'@graph': [{'@type': 'Organization', 'image': 'https://example.org/brand.png'},
                            {'@type': 'BlogPosting', 'image': {'url': photo}}]}
        soup = BeautifulSoup('<meta property="og:image" content="https://example.org/cropped-----.jpg">'
                             '<script type="application/ld+json">' + json.dumps(schema) + '</script>', 'html.parser')
        self.assertEqual(article_image_candidates(soup, 'https://example.org/news'), [photo])

    def test_lazy_featured_image_and_relative_url(self):
        soup = BeautifulSoup('<article><h1>News</h1><img class="wp-post-image" src="data:image/gif;base64,x" data-src="/photo.jpg">'
                             '<div class="entry-content"><img width="20" height="20" src="/share.png"></div></article>', 'html.parser')
        self.assertEqual(article_image_candidates(soup, 'https://example.org/news'), ['https://example.org/photo.jpg'])

    def hrana_page(self, article_id, filename, schema=True):
        # Reduced from the two reported HRANA pages: the sidebar precedes the story.
        page = f'https://www.hra-news.org/2026/hranews/{article_id}/'
        photo = f'https://www.hra-news.org/wp-content/uploads/2026/09/{filename}.jpg'
        graph = [
            {'@type': 'Article', '@id': page + '#article',
             'mainEntityOfPage': {'@id': page}, 'image': {'@id': page + '#primaryimage'}},
            {'@type': 'ImageObject', '@id': page + '#primaryimage', 'contentUrl': photo},
        ]
        html = ('<div class="left-sidebar"><div class="post-item">'
                '<img class="wp-post-image" width="400" height="400" src="/unrelated-person.jpg">'
                '</div></div><div class="centeral"><div class="single-page">'
                '<h2 class="single-post-title">News</h2><img class="wp-post-image" src="' + photo.replace('.jpg', '-300x191.jpg') + '">'
                '<div class="single-post-content"><p>' + BODY + '</p></div>'
                '<div class="relatet-post"><img class="wp-post-image" src="/other-story.jpg"></div>'
                '</div></div>')
        if schema:
            html += '<script type="application/ld+json">' + json.dumps({'@graph': graph}) + '</script>'
        return page, photo, html

    def test_reported_hrana_articles_resolve_primary_image_reference(self):
        for article_id, filename in [('a-84c8eb3e', 'Kargar_4'), ('a-a93827db', 'Havades_6')]:
            with self.subTest(article=article_id):
                page, photo, html = self.hrana_page(article_id, filename)
                candidates = article_image_candidates(BeautifulSoup(html, 'html.parser'), page)
                self.assertEqual(candidates, [photo, photo.replace('.jpg', '-300x191.jpg')])

    def test_hrana_scoped_featured_image_without_schema(self):
        page, photo, html = self.hrana_page('a-84c8eb3e', 'Kargar_4', schema=False)
        self.assertEqual(article_image_candidates(BeautifulSoup(html, 'html.parser'), page),
                         [photo.replace('.jpg', '-300x191.jpg')])

    def test_broken_hrana_photos_never_fall_back_to_sidebar(self):
        page, _, html = self.hrana_page('a-84c8eb3e', 'Kargar_4')
        candidates = article_image_candidates(BeautifulSoup(html, 'html.parser'), page)
        session = Mock()
        session.get.return_value = self.response(status=404)
        with self.assertRaises(ImageUnavailable):
            verified_image(candidates, session)
        self.assertEqual(session.get.call_count, 2)
        self.assertTrue(all('Kargar_4' in call.args[0] for call in session.get.call_args_list))

    def test_hrana_rss_full_text_still_uses_correct_detail_photo(self):
        page, photo, html = self.hrana_page('a-a93827db', 'Havades_6')
        fetcher = NewsFetcher()
        fetcher._make_request = Mock(return_value=Mock(status_code=200, content=html.encode()))
        fetcher.session = Mock()
        fetcher.session.get.return_value = self.response(url=photo)
        item = {'link': page, 'source': 'هرانا - کارگران', 'image_url': None}
        self.assertEqual(fetcher.resolve_article_image(item, {'success': True, 'full_content': BODY}), photo)
        self.assertEqual(fetcher.session.get.call_args.args[0], photo)

    def test_jsonld_references_across_scripts_ignore_other_articles_and_cycles(self):
        nodes = [
            {'@type': 'Article', '@id': 'https://example.org/other#article', 'image': '/wrong.jpg'},
            {'@type': 'NewsArticle', '@id': '#article', 'image': [{'@id': '#loop'}, {'@id': '#photo'}]},
            {'@type': 'ImageObject', '@id': '#loop', 'url': {'@id': '#loop'}},
            {'@type': 'ImageObject', '@id': '#photo', 'url': '/right.jpg'},
        ]
        html = ''.join('<script type="application/ld+json">' + json.dumps(n) + '</script>' for n in nodes)
        self.assertEqual(article_image_candidates(BeautifulSoup(html, 'html.parser'), 'https://example.org/news'),
                         ['https://example.org/right.jpg'])

    def test_unresolved_jsonld_reference_is_not_an_image_url(self):
        html = '<script type="application/ld+json">' + json.dumps(
            {'@type': 'Article', 'image': {'@id': '#missing'}}) + '</script>'
        self.assertEqual(article_image_candidates(BeautifulSoup(html, 'html.parser'), 'https://example.org/news'), [])

    def test_sidebar_and_related_body_images_are_excluded(self):
        html = ('<aside><article><h1>Sidebar story</h1><img class="wp-post-image" src="/wrong.jpg"></article></aside>'
                '<article><h1>Actual story</h1><div class="entry-content"><img src="/right.jpg">'
                '<div class="related-posts"><img src="/related.jpg"></div></div></article>'
                '<article><h2>Other story</h2><img class="wp-post-image" src="/other.jpg"></article>')
        self.assertEqual(article_image_candidates(BeautifulSoup(html, 'html.parser'), 'https://example.org/news'),
                         ['https://example.org/right.jpg'])

    def test_invalid_or_empty_urls_are_not_images(self):
        for value in ['', None, 'javascript:alert(1)', 'https://user:pass@example.org/img.jpg']:
            self.assertEqual(image_url(value), '')

    def test_falls_back_after_broken_image(self):
        session = Mock()
        session.get.side_effect = [self.response(status=404), self.response()]
        self.assertEqual(verified_image(['https://example.org/broken.jpg', 'https://example.org/photo.jpg'], session),
                         'https://example.org/photo.jpg')
        self.assertEqual(session.get.call_count, 2)

    def test_html_and_corrupt_image_bytes_are_rejected(self):
        for data, content_type in [(b'<html>denied</html>', 'text/html'), (b'not an image', 'image/jpeg')]:
            session = Mock()
            session.get.return_value = self.response(data=data, content_type=content_type)
            with self.assertRaises(ImageUnavailable):
                verified_image(['https://example.org/photo.jpg'], session)

    def test_oversized_response_is_rejected(self):
        session = Mock()
        session.get.return_value = self.response(data=b'x' * 20)
        with patch('article_images.MAX_IMAGE_BYTES', 10), self.assertRaises(ImageUnavailable):
            verified_image(['https://example.org/photo.jpg'], session)

    def test_truncated_jpeg_is_rejected(self):
        buffer = BytesIO()
        Image.new('RGB', (640, 420), 'navy').save(buffer, format='JPEG')
        session = Mock()
        session.get.return_value = self.response(data=buffer.getvalue()[:-200])
        with self.assertRaises(ImageUnavailable):
            verified_image(['https://example.org/photo.jpg'], session)

    def test_output_uses_verified_image_without_nested_proxy(self):
        url = 'https://i0.wp.com/example.org/photo.jpg?fit=1280%2C852&ssl=1'
        html = build_post_html({'title': 'عنوان اصلی', 'link': 'https://example.org/news', 'source': 'منبع'},
                               'عنوان خبر جدید', BODY, url, ['حقوق بشر'])
        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(soup.find('img')['src'], url)
        self.assertNotIn('wsrv.nl', html)
        footer = soup.select_one('.news-source-footer')
        self.assertIn('display:flex', footer['style'])
        self.assertIn('direction:rtl', footer['style'])
        self.assertEqual([node.get('class') for node in footer.find_all('div', recursive=False)],
                         [['news-related-labels'], ['news-source-credit']])
        source = footer.select_one('.news-source-credit')
        self.assertEqual(source.get_text(' ', strip=True), 'منبع خبر: منبع')
        self.assertIsNone(source.find('a'))
        self.assertIsNotNone(footer.select_one('.news-related-labels a'))

    def test_related_stories_still_render_after_legacy_script_removal(self):
        recent = [
            {'title': f'خبر مرتبط {i}', 'url': f'https://example.org/story-{i}',
             'labels': ['حقوق بشر'], 'published': '2026-09-23T12:00:00Z',
             'content': '<figure><img src="https://example.org/photo.jpg"></figure>'}
            for i in range(3)
        ]
        html = build_post_html(
            {'title': 'خبر منبع', 'link': 'https://example.org/new', 'source': 'منبع'},
            'عنوان تازه', BODY, '', ['حقوق بشر'], recent)
        encoded = re.search(r'var b64 = "([A-Za-z0-9+/=]+)"', html)
        self.assertIsNotNone(encoded)
        widget = base64.b64decode(encoded.group(1)).decode('utf-8')
        self.assertIn('خبر مرتبط 0', widget)
        self.assertIn('https://example.org/story-2', widget)
        self.assertIn('photo.jpg', widget)
