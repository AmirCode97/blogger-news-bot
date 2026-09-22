"""Evidence-linked monthly BLOG REPORT counts, never estimated people or national totals."""
import hashlib
import json
import re
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo
import jdatetime
from article_utils import normalize_text, parse_datetime, plain_article_text, utc_now

STATS_LABEL = 'آمار_زنده'
STATS_TITLE = 'Live Statistics Storage (Do not delete)'
TEHRAN = ZoneInfo('Asia/Tehran')

def month_window(now=None):
    now = (now or utc_now()).astimezone(TEHRAN)
    persian = jdatetime.date.fromgregorian(date=now.date())
    first = jdatetime.date(persian.year, persian.month, 1).togregorian()
    y, m = (persian.year + 1, 1) if persian.month == 12 else (persian.year, persian.month + 1)
    following = jdatetime.date(y, m, 1).togregorian()
    start = datetime(first.year, first.month, first.day, tzinfo=TEHRAN)
    end = datetime(following.year, following.month, following.day, tzinfo=TEHRAN)
    return start, end, f'{persian.year:04}-{persian.month:02}'

END = r'(?=$|[\s،,:؛.!؟])'
COMPLETED = r'(?:شد(?:ند)?|گردید(?:ند)?|شده (?:است|اند))' + END
TOPICS = {'executions': re.compile(r'اعدام|قصاص|دار آویخته'),
          'arrests': re.compile(r'بازداشت|دستگیر')}
ASSERTIONS = {
    'executions': [
        re.compile(r'(?:اعدام|قصاص) ' + COMPLETED),
        re.compile(r'دار آویخته ' + COMPLETED),
        re.compile(r'(?:حکم|احکام) اعدام[^.!؟؛\n]{0,100}?(?:اجرا ' + COMPLETED + r'|به اجرا درآمد(?:ند)?' + END + ')'),
        re.compile(r'اجرای (?:حکم|احکام) اعدام[^.!؟؛\n]{0,80}?(?:انجام شد|صورت گرفت)' + END),
        re.compile(r'خبر اعدام[^.!؟؛\n]{0,70}?(?:تأیید|تایید) شد' + END)],
    'arrests': [
        re.compile(r'(?:بازداشت|دستگیر) ' + COMPLETED),
        re.compile(r'(?:بازداشت|دستگیر) و[^.!؟؛\n]{0,100}?منتقل ' + COMPLETED),
        re.compile(r'(?:بازداشت|دستگیری)[^.!؟؛\n]{0,70}?(?:صورت گرفت|انجام شد)' + END),
        re.compile(r'(?:خبر بازداشت|خبر دستگیری|وقوع بازداشت)[^.!؟؛\n]{0,70}?(?:تأیید|تایید) شد' + END)]}
DENIAL = re.compile(r'تکذیب|صحت ندارد|واقعیت ندارد|نادرست|شایعه|جعلی|ت[أا]یید نشده|ت[أا]یید نشد|ت[أا]یید نمی شود')
UNCERTAIN = re.compile(r'احتمالا|احتمال وقوع|احتمال اعدام|احتمال بازداشت|ممکن است|گویا|گفته می شود|شاید|ادعا|اگر |در صورت |آیا|[؟?]')
PREVENTION = re.compile(r'جلوگیری|متوقف|توقف|لغو|تعلیق|قرار است|خواهد|خواهند|باید |نباید |در آستانه|در خطر|تهدید|درخواست')
BACKGROUND = re.compile(r'پیشتر|پیش از این|قبلا|سال گذشته|سال قبل|سال ها پیش|سالها پیش|شده بود|شده بودند')
ARREST_CONTEXT = re.compile(r'محاکمه|صدور حکم|حکم اعدام|احکام|حبس|پرونده|آزادی|آزاد شد|وثیقه|سالگرد|بی خبری|وضعیت زندانی|ادامه بازداشت|تمدید بازداشت|بلاتکلیفی')

def sentences(text):
    # Keep question marks so an interrogative sentence cannot become an assertion.
    return [normalize_text(s) for s in re.findall(r'[^.!؟?؛\n]+[.!؟?؛]?', text) if s.strip()]

def classify(title, body, kind):
    heading = normalize_text(title)
    heading_units, units = sentences(title), sentences(title) + sentences(body)
    if not any(TOPICS[kind].search(s) for s in units):
        return 'excluded', ''
    def occurrence(s):
        return any(pattern.search(s) for pattern in ASSERTIONS[kind])
    heading_action = any(occurrence(s) and not DENIAL.search(s) and not UNCERTAIN.search(s)
                         and not PREVENTION.search(s) for s in heading_units)
    background_headline = (kind == 'arrests' and ARREST_CONTEXT.search(heading) and not heading_action
                           and not re.match(r'^(بازداشت|دستگیری) ', heading))
    candidate, ambiguous = '', ''
    for unit in units:
        if not occurrence(unit) or BACKGROUND.search(unit):
            continue
        if DENIAL.search(unit) or UNCERTAIN.search(unit) or PREVENTION.search(unit) or background_headline:
            ambiguous = ambiguous or unit
        else:
            candidate = candidate or unit
    contradiction = next((u for u in units if (TOPICS[kind].search(u) and (DENIAL.search(u) or UNCERTAIN.search(u)))
                          or (re.search(r'این خبر|این گزارش|این ادعا', u) and DENIAL.search(u))), '')
    if candidate and contradiction:
        return 'uncertain', contradiction
    if candidate:
        return 'reported', candidate
    return ('uncertain', ambiguous) if ambiguous else ('excluded', '')

def calculate_stats(posts, now=None):
    now = now or utc_now()
    start, end, month = month_window(now)
    totals = {'executions': 0, 'arrests': 0}
    evidence = {'executions': [], 'arrests': []}
    uncertain = {'executions': [], 'arrests': []}
    fingerprints, ids = set(), set()
    scanned, duplicates = 0, 0
    for post in posts:
        if post.get('id') in ids or STATS_LABEL in post.get('labels', []):
            continue
        ids.add(post.get('id'))
        date = parse_datetime(post.get('published'))
        if not date or not start <= date < end or date > now:
            continue
        title, body = post.get('title', ''), plain_article_text(post.get('content', ''))
        scanned += 1
        digest = hashlib.sha256((normalize_text(title) + '\n' + normalize_text(body)).encode()).hexdigest()
        if digest in fingerprints:
            duplicates += 1
            continue
        fingerprints.add(digest)
        for kind in totals:
            state, quote = classify(title, body, kind)
            entry = {'post_id': post['id'], 'title': title, 'url': post.get('url', ''), 'evidence': quote[:300]}
            if state == 'reported':
                totals[kind] += 1
                evidence[kind].append(entry)
            elif state == 'uncertain':
                uncertain[kind].append(entry)
    return {**{k: str(v) for k, v in totals.items()}, 'version': 2, 'count_kind': 'blog_occurrence_reports',
            'period': month, 'period_start': start.isoformat(), 'period_end': end.isoformat(),
            'timezone': 'Asia/Tehran', 'last_updated': jdatetime.datetime.fromgregorian(datetime=now.astimezone(TEHRAN)).strftime('%Y/%m/%d %H:%M'),
            'updated_at': now.isoformat(), 'scanned_posts': scanned, 'duplicates_removed': duplicates,
            'evidence': evidence, 'uncertain': uncertain,
            'methodology': 'تعداد خبرهای وبلاگ با گزارش صریح وقوع در ماه شمسی جاری؛ نه تعداد افراد یا آمار کل کشور. خبر مبهم شمرده نمی‌شود. بازنشر کاملاً یکسان حذف می‌شود؛ بازنویسی متفاوت ممکن است خبر جدا محسوب شود.'}

def fetch_and_calculate_stats(poster, now=None):
    start, _, _ = month_window(now)
    # list_posts must finish ALL pages; any failure leaves the previous stats record untouched.
    return calculate_stats(poster.list_posts(start.isoformat()), now)

def update_stats_post(poster, stats_data):
    if stats_data.get('count_kind') != 'blog_occurrence_reports':
        raise ValueError('Refusing unqualified statistics')
    existing = poster.list_posts(labels=STATS_LABEL)
    if len(existing) > 1 or any(p.get('title') != STATS_TITLE for p in existing):
        raise RuntimeError('Ambiguous stats record; no existing post was changed')
    encoded = escape(json.dumps(stats_data, ensure_ascii=False))
    content = f"<pre id='stats-data' style='display:none;'>{encoded}</pre>"
    content += '<p dir="rtl">' + escape(stats_data['methodology']) + '</p>'
    for kind, label in [('executions', 'خبر اجرای اعدام'), ('arrests', 'خبر وقوع بازداشت')]:
        content += f'<p dir="rtl">{label}: {stats_data[kind]}</p><ul>'
        for entry in stats_data['evidence'][kind]:
            content += f'<li><a href="{escape(entry["url"], quote=True)}">{escape(entry["title"])}</a>: {escape(entry["evidence"])}</li>'
        content += '</ul>'
    if existing:
        # Only this explicitly identified storage record is mutable. News posts are never patched.
        poster.service.posts().patch(blogId=poster.blog_id, postId=existing[0]['id'],
                                     body={'content': content}).execute(num_retries=2)
    else:
        result = poster.create_post(STATS_TITLE, content, labels=[STATS_LABEL],
                                    published_date='2010-01-01T00:00:00Z')
        if not result:
            raise RuntimeError('Statistics record could not be created')

if __name__ == '__main__':
    from blogger_poster import BloggerPoster
    poster = BloggerPoster()
    update_stats_post(poster, fetch_and_calculate_stats(poster))
