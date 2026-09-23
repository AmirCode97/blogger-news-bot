import base64
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

from ai_processor import AIProcessor, AIProcessingError
from article_utils import atomic_json, canonical_url, parse_datetime, utc_now
from blogger_poster import BloggerPoster
from duplicate_detector import DuplicateDetector
from main import BloggerNewsBot, build_post_html, deduplicate_text, labels_for
from news_fetcher import NewsFetcher
from state_store import GitHubState, validate_state
from stats_updater import calculate_stats, classify, month_window, update_stats_post, STATS_TITLE

BODY = 'بر اساس گزارش این خبرگزاری، کارگران یک واحد تولیدی برای پیگیری حقوق معوقه خود تجمع کردند. مسئولان این واحد هنوز به درخواست آنان پاسخ نداده‌اند و کارگران خواستار پرداخت دستمزد و بهبود شرایط کار شدند.'

class IsolatedTest(unittest.TestCase):
    def setUp(self):
        self.original_cwd = os.getcwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.network = patch('requests.sessions.Session.request', side_effect=AssertionError('Unexpected network in unit test'))
        self.network.start()

    def tearDown(self):
        self.network.stop()
        os.chdir(self.original_cwd)
        self.temp.cleanup()

class IdentityTests(IsolatedTest):
    def test_tracking_removed_but_article_query_preserved(self):
        self.assertEqual(canonical_url('http://www.example.org/x/?utm_source=rss#top'), 'https://example.org/x')
        self.assertNotEqual(canonical_url('https://example.org/?p=1'), canonical_url('https://example.org/?p=2'))

    def test_timezone_and_rss_dates(self):
        for value in ['Mon, 01 Jan 2001 00:00:00 +0000', '2001-01-01T00:00:00Z', '2001-01-01T03:30:00+03:30']:
            self.assertEqual(parse_datetime(value), datetime(2001, 1, 1, tzinfo=timezone.utc))
        self.assertIsNone(parse_datetime('not a date'))

    def test_persistent_identity_survives_title_changes(self):
        detector = DuplicateDetector()
        detector.mark_as_published('عنوان نخست خبر', 'https://example.org/story?utm_source=rss', BODY, '1')
        restored = DuplicateDetector()
        self.assertTrue(restored.is_duplicate('عنوان جدید همان خبر', 'https://example.org/story')[0])
        self.assertFalse(restored.is_duplicate('خبر دیگری', 'https://example.org/?p=2')[0])

    def test_similar_names_and_changed_numbers_are_not_duplicates(self):
        detector = DuplicateDetector()
        detector.mark_as_published('بازداشت ۳ شهروند در شهر تهران توسط نیروهای امنیتی', 'https://example.org/1')
        self.assertFalse(detector.is_duplicate('بازداشت ۴ شهروند در شهر تهران توسط نیروهای امنیتی', 'https://example.org/2')[0])
        detector.mark_as_published('بازداشت محمد احمدی در شهر تهران توسط نیروهای امنیتی', 'https://example.org/3')
        self.assertFalse(detector.is_duplicate('بازداشت علی رضایی در شهر تهران توسط نیروهای امنیتی', 'https://example.org/4')[0])

    def test_recovery_from_published_metadata(self):
        d = DuplicateDetector()
        d.seed_from_posts([{'id': 'x', 'title': 'عنوان بازنویسی شده', 'published': utc_now().isoformat(),
                           'content': '<article data-source-url="https://example.org/a" data-source-title="عنوان اصلی">خبر</article>'}])
        self.assertTrue(d.is_duplicate('عنوان اصلی تغییر کرد', 'https://example.org/a?utm_source=rss')[0])

    def test_distinct_paragraph_endings_are_preserved(self):
        prefix = ' '.join(str(i) for i in range(40))
        self.assertIn('پایان دوم', deduplicate_text(prefix + ' پایان اول\n' + prefix + ' پایان دوم'))

class FetcherTests(IsolatedTest):
    def test_hrana_current_article_selector(self):
        f = NewsFetcher()
        f._make_request = Mock(return_value=NS(status_code=200, content=(
            '<meta property="article:published_time" content="2026-09-22T12:00:00+00:00">'
            '<div class="single-post-content"><p>' + BODY + '</p></div>').encode()))
        article = f.fetch_full_article('https://www.hra-news.org/2026/hranews/test/')
        self.assertTrue(article['success'])
        self.assertEqual(article['full_content'], BODY)
        self.assertTrue(article['published'].endswith('+00:00'))

    def test_nested_article_is_only_collected_once(self):
        f = NewsFetcher()
        f._make_request = Mock(return_value=NS(status_code=200, content=b'<div class="post"><article><h4 class="entry-title"><a href="/story">A real article headline</a></h4></article></div>'))
        items = f.fetch_from_scrape({'name': 'test', 'url': 'https://example.org', 'selectors': {'articles': 'article,.post'}})
        self.assertEqual(len(items), 1)

    def test_quota_after_seen_filter(self):
        f = NewsFetcher()
        source = {'name': 'test', 'url': 'https://example.org', 'rss_url': 'https://example.org/feed', 'max_items': 1}
        f.seen_titles.add('Already seen article')
        xml = '<rss version="2.0"><channel><title>Test</title><item><title>Already seen article</title><link>https://example.org/1</link></item><item><title>Unseen second article</title><link>https://example.org/2</link><pubDate>Tue, 22 Sep 2026 12:00:00 GMT</pubDate></item></channel></rss>'
        f._make_request = Mock(return_value=NS(status_code=200, content=xml.encode()))
        self.assertEqual(f.fetch_from_rss(source)[0]['title'], 'Unseen second article')

    def test_legacy_cache_identity_preserved(self):
        f = NewsFetcher()
        title = 'عنوان خبر منتشرشده'
        f.seen_ids.add(f._generate_news_id(title, 'https://humanrightsinir.org/story/'))
        self.assertIsNone(f._item({'name': 'test', 'url': 'https://humanrightsinir.org/'}, title, 'https://humanrightsinir.org/story/?utm_source=rss'))

    def test_no_date_is_not_fabricated(self):
        f = NewsFetcher()
        item = f._item({'name': 'test', 'url': 'https://example.org'}, 'عنوان واقعی خبر', '/a')
        self.assertIsNone(item['published'])

    def test_non_200_logs_real_status_and_fails(self):
        f = NewsFetcher()
        f._make_request = Mock(return_value=NS(status_code=403))
        with self.assertRaisesRegex(RuntimeError, '403'):
            f.fetch_from_rss({'rss_url': 'https://example.org/feed'})

    def test_fallback_and_source_health(self):
        f = NewsFetcher()
        f.fetch_from_rss = Mock(side_effect=RuntimeError('blocked'))
        f.fetch_from_scrape = Mock(return_value=[])
        with patch('news_fetcher.NEWS_SOURCES', [{'name': 'test', 'url': 'https://example.org', 'rss_url': 'https://example.org/feed'}]):
            self.assertEqual(f.fetch_all_news(), [])
        self.assertTrue(f.source_health[0]['ok'])
        self.assertEqual(f.source_health[0]['errors'], ['blocked'])

class AITests(IsolatedTest):
    def processor(self, text):
        session = Mock()
        session.post.return_value = NS(status_code=200, json=lambda: {'candidates': [{
            'finishReason': 'STOP', 'content': {'parts': [{'text': text}]}}]})
        with patch('ai_processor.GEMINI_API_KEY', 'test-key'):
            return AIProcessor(session)

    def test_valid_rewrite_contract(self):
        ai = self.processor(json.dumps({'title': 'تجمع کارگران برای پیگیری دستمزد', 'english_slug': 'iran-workers-wages', 'content': BODY}))
        rewrite_response = ai.session.post.return_value
        verdict = NS(status_code=200, json=lambda: {'candidates': [{'finishReason': 'STOP',
                     'content': {'parts': [{'text': '{"supported":true,"issues":[]}'}]}}]})
        ai.session.post.side_effect = [rewrite_response, verdict]
        result = ai.process_news('تجمع کارگران', BODY)
        self.assertEqual(result[2], BODY)
        self.assertEqual(ai.session.post.call_count, 2)
        self.assertEqual(ai.session.post.call_args.kwargs['json']['generationConfig']['responseMimeType'], 'application/json')

    def test_unsupported_or_malformed_grounding_verdict_rejects(self):
        for verdict in [{'supported': False, 'issues': ['invented attribution']},
                        {'supported': True, 'issues': ['changed name']},
                        {'supported': 'true', 'issues': []}, {'supported': True}]:
            ai = self.processor(json.dumps(verdict))
            with self.subTest(verdict=verdict), self.assertRaises(AIProcessingError):
                ai._verify_grounding('تجمع کارگران', BODY, {'title': 'تجمع کارگران', 'content': BODY})

    def test_failed_grounding_never_returns_rewrite(self):
        ai = self.processor(json.dumps({'title': 'تجمع کارگران برای پیگیری دستمزد',
                                        'english_slug': 'workers-wages', 'content': BODY}))
        with patch.object(ai, '_verify_grounding', side_effect=AIProcessingError('unsupported')) as verify:
            with patch('ai_processor.time.sleep'), self.assertRaises(AIProcessingError):
                ai.process_news('تجمع کارگران', BODY)
            self.assertEqual(verify.call_count, 3)

    def test_hunger_strike_is_not_automatically_a_labor_story(self):
        self.assertEqual(labels_for('اعتصاب غذا در زندان', 'یک زندانی اعتصاب غذا کرده است.', 'حقوق بشر'), ['وضعیت زندانیان'])
        self.assertIn('کارگران', labels_for('اعتصاب کارگران', BODY, 'حقوق بشر'))

    def test_bad_json_and_types_rejected(self):
        ai = self.processor('')
        for bad in ['not JSON', '[]', '{"title":null}', json.dumps({'title': 'عنوان کافی خبر', 'english_slug': 'good-slug', 'content': []})]:
            with self.subTest(bad=bad), self.assertRaises(AIProcessingError):
                ai._parse_ai_response(bad)

    def test_unused_slug_cannot_block_a_valid_story(self):
        ai = self.processor('')
        for value in [None, 'نامک فارسی', 'too many words without hyphens']:
            data = ai._parse_ai_response(json.dumps({'title': 'تجمع کارگران برای پیگیری دستمزد',
                                                     'english_slug': value, 'content': BODY}))
            self.assertRegex(data['english_slug'], r'^news-[0-9a-f]{12}$')

    def test_no_model_call_for_headline_only(self):
        ai = self.processor('')
        with self.assertRaises(AIProcessingError):
            ai.process_news('تیتر خبر', '')
        ai.session.post.assert_not_called()

    def test_new_numeric_claim_rejected(self):
        ai = self.processor(json.dumps({'title': 'بازداشت ۹۹ نفر در تهران', 'english_slug': 'arrest-news', 'content': BODY}))
        with patch('ai_processor.time.sleep'), self.assertRaises(AIProcessingError):
            ai.process_news('تجمع کارگران', BODY)

    def test_html_output_escaped(self):
        item = {'title': '" onerror="evil', 'link': 'https://example.org/a', 'source': '<b>source</b>'}
        html = build_post_html(item, '" onerror="evil', '<script>alert(1)</script>', 'https://example.org/img.jpg', ['خبر'])
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('&quot; onerror=&quot;', html)

class StatsTests(IsolatedTest):
    now = datetime(2026, 9, 22, 12, tzinfo=timezone.utc)

    def post(self, title, body, id='1', published=None):
        return {'id': id, 'title': title, 'content': '<article><p>' + body + '</p></article>',
                'url': 'https://example.org/' + id, 'published': published or self.now.isoformat()}

    def test_empty_input_is_zero_reports_without_baseline(self):
        stats = calculate_stats([], self.now)
        self.assertEqual((stats['executions'], stats['arrests']), ('0', '0'))
        self.assertEqual(stats['count_kind'], 'blog_occurrence_reports')

    def test_counts_reports_not_people(self):
        stats = calculate_stats([self.post('اجرای اعدام در یک زندان', 'سه زندانی در این زندان اعدام شدند.')], self.now)
        self.assertEqual(stats['executions'], '1')
        self.assertEqual(len(stats['evidence']['executions']), 1)

    def test_sentences_releases_and_negations_not_occurrences(self):
        cases = [('صدور حکم اعدام', 'برای سه زندانی حکم اعدام صادر شد.', 'executions'),
                 ('آزادی یک زندانی', 'او بازداشت شده بود و امروز آزاد شد.', 'arrests'),
                 ('تکذیب خبر اعدام', 'خبر اعدام این زندانی تکذیب شد.', 'executions'),
                 ('درخواست توقف اعدام', 'این زندانی قرار است فردا اعدام شود.', 'executions'),
                 ('محکومیت یک فعال به حبس', 'این فعال بازداشت و به زندان منتقل شد.', 'arrests')]
        for title, body, kind in cases:
            with self.subTest(title=title):
                self.assertNotEqual(classify(title, body, kind)[0], 'reported')

    def test_mixed_denial_is_uncertain(self):
        self.assertEqual(classify('گزارش اعدام', 'یک زندانی اعدام شد. این خبر تکذیب شد.', 'executions')[0], 'uncertain')

    def test_month_boundary_and_duplicates(self):
        start, end, _ = month_window(self.now)
        p = self.post('بازداشت یک شهروند', 'این شهروند توسط نیروهای امنیتی بازداشت شد.')
        same = dict(p, id='2')
        old = dict(p, id='3', published=(start - timedelta(seconds=1)).isoformat())
        result = calculate_stats([p, same, old], self.now)
        self.assertEqual(result['arrests'], '1')
        self.assertEqual(result['duplicates_removed'], 1)
        self.assertLess(start, self.now)
        self.assertGreater(end, self.now)

    def test_only_dedicated_stats_record_can_be_patched(self):
        poster = Mock()
        poster.blog_id = 'blog'
        poster.list_posts.return_value = [{'id': 'stats-only', 'title': STATS_TITLE}]
        update_stats_post(poster, calculate_stats([], self.now))
        self.assertEqual(poster.service.posts.return_value.patch.call_args.kwargs['postId'], 'stats-only')
        poster.service.posts.return_value.update.assert_not_called()
        poster.list_posts.return_value = [{'id': 'old-news', 'title': 'An old news article'}]
        with self.assertRaises(RuntimeError):
            update_stats_post(poster, calculate_stats([], self.now))

class PipelineTests(IsolatedTest):
    def bot(self, published=None, source=BODY, fail=False):
        item = {'id': 'source-1', 'title': 'تجمع کارگران برای حقوق معوقه', 'description': source,
                'link': 'https://example.org/article', 'source': 'Example', 'published': published or utc_now().isoformat()}
        fetcher = Mock()
        fetcher.source_health = [{'source': 'Example', 'ok': True}]
        fetcher.fetch_all_news.return_value = [item]
        fetcher.fetch_full_article.return_value = {'success': bool(source), 'full_content': source}
        fetcher.resolve_article_image.return_value = ''
        poster = Mock()
        poster.list_posts.return_value = []
        poster.create_post.return_value = None if fail else {'id': 'new-post'}
        ai = Mock()
        ai.process_news.return_value = ('کارگران خواستار پرداخت دستمزد شدند', 'workers-wages', BODY)
        return BloggerNewsBot(fetcher=fetcher, blogger=poster, ai=ai), poster

    def run_bot(self, bot):
        with patch('main.time.sleep'), patch('main.fetch_and_calculate_stats', return_value={'ok': True}), patch('main.update_stats_post'):
            return bot.run_once()

    def test_old_aware_and_rss_articles_never_publish(self):
        for date in ['2001-01-01T00:00:00Z', 'Mon, 01 Jan 2001 00:00:00 GMT']:
            bot, poster = self.bot(published=date)
            self.assertEqual(self.run_bot(bot)['skipped_old'], 1)
            poster.create_post.assert_not_called()

    def test_no_source_text_never_publishes(self):
        bot, poster = self.bot(source='')
        self.assertEqual(self.run_bot(bot)['rejected'], 1)
        bot.ai.process_news.assert_not_called()
        poster.create_post.assert_not_called()

    def test_success_inserts_final_title_without_editing_old_posts(self):
        bot, poster = self.bot()
        result = self.run_bot(bot)
        self.assertEqual(result['published'], 1)
        self.assertEqual(poster.create_post.call_args.kwargs['title'], 'کارگران خواستار پرداخت دستمزد شدند')
        poster.update_post_title.assert_not_called()
        poster.service.posts.return_value.update.assert_not_called()
        poster.service.posts.return_value.patch.assert_not_called()
        self.assertTrue(DuplicateDetector().is_duplicate('changed title', 'https://example.org/article')[0])

    def test_publish_failure_is_visible_and_not_marked_seen(self):
        bot, poster = self.bot(fail=True)
        result = self.run_bot(bot)
        self.assertEqual(result['status'], 'degraded')
        self.assertEqual(result['failed'], 1)
        bot.fetcher.mark_as_seen.assert_not_called()

    def test_broken_image_defers_publication_without_marking_seen(self):
        from article_images import ImageUnavailable
        bot, poster = self.bot()
        bot.fetcher.resolve_article_image.side_effect = ImageUnavailable('broken source image')
        result = self.run_bot(bot)
        self.assertEqual(result['failed'], 1)
        poster.create_post.assert_not_called()
        bot.ai.process_news.assert_not_called()
        bot.fetcher.mark_as_seen.assert_not_called()

    def test_stats_update_even_when_no_new_news(self):
        bot, _ = self.bot()
        bot.fetcher.fetch_all_news.return_value = []
        with patch('main.fetch_and_calculate_stats', return_value={'ok': True}), patch('main.update_stats_post') as update:
            bot.run_once()
            update.assert_called_once()

class StateTests(IsolatedTest):
    def test_blogger_list_matches_installed_api_contract(self):
        from googleapiclient.discovery import build_from_document
        from googleapiclient.discovery_cache import get_static_doc
        from googleapiclient.http import HttpMockSequence
        poster = BloggerPoster.__new__(BloggerPoster)
        poster.blog_id = '12345'
        poster.service = build_from_document(get_static_doc('blogger', 'v3'),
            http=HttpMockSequence([({'status': '200'}, b'{"items": [{"id": "live-post"}]}')]))
        self.assertEqual(poster.list_posts('2026-09-01T00:00:00Z', labels='stats')[0]['id'], 'live-post')

    def test_large_snapshot_restores_through_raw_content(self):
        data = {'version': 1, 'files': {'news_cache.json': {'seen_ids': ['saved'], 'seen_titles': []},
                                     'duplicate_cache.json': {'seen_urls': [], 'published_entries': []}}}
        store = GitHubState.__new__(GitHubState)
        store.current = Mock(return_value=Mock(status_code=200, json=lambda: {'encoding': 'none'}))
        store.request = Mock(return_value=Mock(status_code=200, json=lambda: data))
        store.restore()
        self.assertEqual(json.loads(Path('news_cache.json').read_text())['seen_ids'], ['saved'])
        self.assertEqual(store.request.call_args.kwargs['headers']['Accept'], 'application/vnd.github.raw+json')

    def test_question_mark_is_not_a_reported_occurrence(self):
        self.assertNotEqual(classify('دو نفر بازداشت شدند؟', '', 'arrests')[0], 'reported')

    def test_atomic_state_and_validation(self):
        data = {'version': 1, 'files': {'news_cache.json': {'seen_ids': ['a'], 'seen_titles': []},
                                     'duplicate_cache.json': {'seen_urls': [], 'published_entries': []}}}
        atomic_json('state.json', data)
        self.assertEqual(validate_state(json.loads(Path('state.json').read_text()))['news_cache.json']['seen_ids'], ['a'])
        self.assertFalse(Path('state.json.tmp').exists())
        with self.assertRaises(ValueError):
            validate_state({'version': 1, 'files': {}})

    def test_restore_does_not_treat_server_failure_as_cache_miss(self):
        store = GitHubState.__new__(GitHubState)
        store.current = Mock(side_effect=RuntimeError('HTTP 500'))
        with self.assertRaises(RuntimeError):
            store.restore()

    def test_blogger_pagination_failure_not_partial_success(self):
        poster = BloggerPoster.__new__(BloggerPoster)
        poster.blog_id = 'test'
        poster.service = Mock()
        poster.service.posts.return_value.list.return_value.execute.side_effect = [
            {'items': [{'id': 'one'}], 'nextPageToken': 'next'}, RuntimeError('temporary failure')]
        with self.assertRaises(RuntimeError):
            poster.list_posts()

if __name__ == '__main__':
    unittest.main()
