"""Scheduled source -> Gemini rewrite -> Blogger publication; old news posts are read-only."""
import argparse
import json
import sys
import time
from datetime import timedelta
from html import escape
from urllib.parse import quote

import schedule
from bs4 import BeautifulSoup
from ai_processor import AIProcessor, AIProcessingError, sufficient_source
from article_utils import atomic_json, canonical_url, normalize_text, parse_datetime, utc_now
from blogger_poster import BloggerPoster
from config import BLOG_ID, BLOG_URL, CHECK_INTERVAL_HOURS, MAX_NEWS_PER_CHECK, MAX_NEWS_AGE_HOURS
from duplicate_detector import DuplicateDetector
from news_fetcher import NewsFetcher
from stats_updater import fetch_and_calculate_stats, update_stats_post

def deduplicate_text(text):
    """Remove only identical full paragraphs, never just a common opening."""
    seen, paragraphs = set(), []
    for paragraph in text.split('\n'):
        key = normalize_text(paragraph)
        if key and key not in seen:
            paragraphs.append(paragraph.strip())
            seen.add(key)
    return '\n\n'.join(paragraphs)

def download_and_optimize_image(url):
    # Already checked by the fetcher. Keep the source CDN URL and its exact query.
    from article_images import image_url
    return image_url(url)

def labels_for(title, body, category):
    text = title + ' ' + body
    labels = []
    if any(w in text for w in ['کارگر', 'حقوق معوقه', 'سندیکا', 'بازنشستگان', 'پرستار']) or (
            'اعتصاب' in text and 'اعتصاب غذا' not in normalize_text(text)):
        labels.append('کارگران')
    if any(w in text for w in ['زندان', 'بازداشت', 'اوین', 'اعدام', 'حبس', 'وثیقه', 'شکنجه']):
        labels.append('وضعیت زندانیان')
    return labels or [category or 'حقوق بشر']

def build_post_html(item, title, body, image, labels, related_posts=(), english_slug=''):
    """Keep the dark article styling; escape all externally supplied text/attributes."""
    published = utc_now().isoformat()
    schema = {'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': title,
              'datePublished': published, 'dateModified': published, 'description': body[:160],
              'author': {'@type': 'Organization', 'name': 'iranpolnews', 'url': BLOG_URL}}
    if image:
        schema['image'] = [image]
    schema_json = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    source_url = canonical_url(item['link'])
    figure = ''
    image_url = download_and_optimize_image(image)
    if image_url:
        figure = f'<figure style="margin:0 0 25px"><img src="{escape(image_url, quote=True)}" alt="{escape(title, quote=True)}" loading="lazy" decoding="async" style="width:100%;max-width:800px;border-radius:12px" /></figure>'
    paragraphs = '\n'.join(f'<p style="margin-bottom:18px">{escape(p)}</p>'
                           for p in deduplicate_text(body).split('\n\n') if p)
    tags = ' '.join(f'<a href="/search/label/{quote(label)}" style="color:#c0392b;margin-left:12px">#{escape(label)}</a>' for label in labels)
    # Use the existing renderer for related links, without running its update_posts routine.
    related = ''
    if len(related_posts) >= 3:
        from update_all_posts import build_related_posts_widget, extract_first_image, get_persian_date
        candidates = sorted(related_posts, key=lambda p: (len(set(labels).intersection(p.get('labels', []))), p.get('published', '')), reverse=True)[:3]
        cards = [{'title': escape(p.get('title', ''), quote=True),
                  'url': escape(canonical_url(p.get('url', '')), quote=True),
                  'image': escape(extract_first_image(p.get('content', ''), '', {}), quote=True),
                  'label': escape((p.get('labels') or ['حقوق بشر'])[0]),
                  'date': get_persian_date(p.get('published', ''))} for p in candidates]
        related = build_related_posts_widget(cards, escape(labels[0]))
    return f'''<style>.post-featured-image,.post-thumbnail{{display:none!important}}</style>
<script type="application/ld+json">{schema_json}</script>
{figure}
<article data-source-url="{escape(source_url, quote=True)}" data-source-title="{escape(item['title'], quote=True)}" data-source-published="{escape(item.get('published') or '', quote=True)}" data-pending-slug="{escape(english_slug, quote=True)}" data-final-title="{escape(title, quote=True)}" style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:Vazir,sans-serif">
{paragraphs}
</article>
<footer class="news-source-footer" style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:18px;margin-top:35px;border-top:1px solid #d9dee7;padding:24px 0;direction:rtl">
<div class="news-related-labels" style="direction:rtl;text-align:right;margin-left:auto"><strong>برچسب‌های مرتبط:</strong> {tags}</div>
<div class="news-source-credit" style="direction:rtl;text-align:right;margin-right:auto;background:#f3f4f6;padding:12px 20px;border-right:3px solid #d9dee7;border-radius:10px;color:#53627a">
منبع خبر: {escape(item['source'])}
</div></footer>
{related}'''

class BloggerNewsBot:
    def __init__(self, fetcher=None, ai=None, blogger=None, detector=None):
        self.fetcher = fetcher or NewsFetcher()
        self.duplicate_detector = detector or DuplicateDetector()
        self.ai, self.blogger = ai, blogger

    def repair_new_post_titles(self, recent):
        """Retry only titles of posts created by this slug-first workflow."""
        failures = 0
        for post in recent:
            article = BeautifulSoup(post.get('content', ''), 'html.parser').select_one(
                'article[data-pending-slug][data-final-title]')
            if not article or post.get('title') != article.get('data-pending-slug'):
                continue
            title = article.get('data-final-title', '')
            if not title or not post.get('id'):
                continue
            updated = self.blogger.update_post_title(post['id'], title)
            if updated and updated.get('title') == title:
                post['title'] = title
                print(f"[REPAIRED TITLE] {post['id']}")
            else:
                failures += 1
                print(f"[TITLE REPAIR FAILED] {post['id']}")
        return failures

    def fetch_and_process_news(self):
        report = {'started_at': utc_now().isoformat(), 'published': 0, 'duplicates': 0,
                  'skipped_old': 0, 'rejected': 0, 'failed': 0, 'stats_updated': False}
        try:
            items = self.fetcher.fetch_all_news(max_items=MAX_NEWS_PER_CHECK)
            report['sources'] = self.fetcher.source_health
            report['candidates'] = len(items)
            if not BLOG_ID and self.blogger is None:
                raise RuntimeError('BLOG_ID is missing')
            self.blogger = self.blogger or BloggerPoster()
            # Read, never edit, recent existing posts to recover from missing state/ambiguous insert.
            recent = self.blogger.list_posts((utc_now() - timedelta(days=max(7, MAX_NEWS_AGE_HOURS / 24))).isoformat())
            report['failed'] += self.repair_new_post_titles(recent)
            self.duplicate_detector.seed_from_posts(recent)
            recent = [p for p in recent if 'آمار_زنده' not in p.get('labels', [])]
            for item in items:
                try:
                    if self.duplicate_detector.is_duplicate(item['title'], item['link'], published=item.get('published'))[0]:
                        report['duplicates'] += 1
                        continue
                    date = parse_datetime(item.get('published'))
                    if date and utc_now() - date > timedelta(hours=MAX_NEWS_AGE_HOURS):
                        report['skipped_old'] += 1
                        continue
                    full = ({'success': True, 'full_content': item['description'],
                             'main_image': item.get('image_url'), 'published': item.get('published')}
                            if item.get('has_full_content') and sufficient_source(item['description'])
                            else self.fetcher.fetch_full_article(item['link'], item['source']))
                    source_text = full.get('full_content', '') if full.get('success') else ''
                    # A substantial source summary is allowed, but never expand a title into a story.
                    if not sufficient_source(source_text):
                        source_text = item.get('description', '')
                    date = parse_datetime(full.get('published') or item.get('published'))
                    if not date or date > utc_now() + timedelta(hours=1):
                        report['rejected'] += 1
                        print(f"[REJECT] Unknown/future source date: {item['link']}")
                        continue
                    if utc_now() - date > timedelta(hours=MAX_NEWS_AGE_HOURS):
                        report['skipped_old'] += 1
                        continue
                    item['published'] = date.isoformat()
                    if not sufficient_source(source_text):
                        report['rejected'] += 1
                        print(f"[REJECT] Insufficient source text: {item['link']}")
                        continue
                    if self.duplicate_detector.is_duplicate(item['title'], item['link'], source_text, item['published'])[0]:
                        report['duplicates'] += 1
                        continue
                    image = self.fetcher.resolve_article_image(item, full)
                    self.ai = self.ai or AIProcessor()
                    title, slug, body = self.ai.process_news(item['title'], source_text, item.get('language', 'fa'))
                    labels = labels_for(title, body, item.get('source_category'))
                    html = build_post_html(item, title, body, image, labels, recent, english_slug=slug)
                    result = self.blogger.create_post_with_slug(slug, title, html, labels)
                    report['published'] += 1
                    self.duplicate_detector.mark_as_published(title, item['link'], source_text, result['id'],
                                                              item['title'], item['published'])
                    self.fetcher.mark_as_seen(item['title'], item['id'])
                    print(f"[PUBLISHED] {result['id']}: {title}")
                    time.sleep(20)
                except AIProcessingError as exc:
                    report['failed'] += 1
                    print(f"[AI FAILED] {item['link']}: {exc}")
                except Exception as exc:
                    report['failed'] += 1
                    print(f"[ITEM FAILED] {item['link']}: {type(exc).__name__}: {exc}")
            # Update only the dedicated statistics record, including runs with no new news.
            stats = fetch_and_calculate_stats(self.blogger)
            update_stats_post(self.blogger, stats)
            report['stats_updated'] = True
        except Exception as exc:
            report['failed'] += 1
            print(f'[RUN FAILED] {type(exc).__name__}: {exc}')
        report['finished_at'] = utc_now().isoformat()
        unhealthy = [s for s in report.get('sources', []) if not s['ok']]
        report['status'] = 'degraded' if unhealthy or report['failed'] or report['rejected'] else 'success'
        atomic_json('run_report.json', report)
        print('[SUMMARY] ' + json.dumps(report, ensure_ascii=False))
        return report

    def run_once(self):
        return self.fetch_and_process_news()

    def run_scheduler(self):
        self.run_once()
        schedule.every(CHECK_INTERVAL_HOURS).hours.do(self.run_once)
        while True:
            schedule.run_pending()
            time.sleep(30)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--check-sources', action='store_true', help='Read sources only; no Gemini/Blogger writes')
    args = parser.parse_args()
    if args.check_sources:
        fetcher = NewsFetcher()
        items = fetcher.fetch_all_news()
        samples = []
        for source in fetcher.source_health:
            item = next((x for x in items if x['source'] == source['source']), None)
            if item:
                full = fetcher.fetch_full_article(item['link'], item['source'])
                samples.append({'source': item['source'], 'url': item['link'],
                                'source_date': full.get('published') or item.get('published'),
                                'full_text_chars': len(full.get('full_content', '')), 'ok': full.get('success', False)})
                try:
                    samples[-1]['image_url'] = fetcher.resolve_article_image(item, full)
                    samples[-1]['image_ok'] = bool(samples[-1]['image_url'])
                except RuntimeError as exc:
                    samples[-1].update(image_ok=False, image_error=str(exc), ok=False)
        report = {'sources': fetcher.source_health, 'samples': samples, 'candidates': len(items)}
        atomic_json('source_report.json', report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return int(any(not s['ok'] for s in fetcher.source_health) or any(not s['ok'] for s in samples))
    bot = BloggerNewsBot()
    if args.once:
        return int(bot.run_once()['status'] != 'success')
    bot.run_scheduler()
    return 0

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
