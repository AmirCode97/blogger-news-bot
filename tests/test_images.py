import json
from io import BytesIO
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup
from PIL import Image

from article_images import article_image_candidates, image_url, verified_image, ImageUnavailable
from main import build_post_html
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
        soup = BeautifulSoup('<img class="wp-post-image" src="data:image/gif;base64,x" data-src="/photo.jpg">'
                             '<div class="entry-content"><img width="20" height="20" src="/share.png"></div>', 'html.parser')
        self.assertEqual(article_image_candidates(soup, 'https://example.org/news'), ['https://example.org/photo.jpg'])

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
