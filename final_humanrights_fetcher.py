# final_humanrights_fetcher.py
import requests, urllib3, re, time, random
from bs4 import BeautifulSoup
urllib3.disable_warnings()

LOGO_SKIP = ["cropped-----", "gravatar", "icons_the", "emoji",
             "ultimate-social-media", "plugins/"]

FEEDS = {
    "بازداشت_بلاتکلیفی": "https://humanrightsinir.org/category/%d8%a8%d8%a7%d8%b2%d8%af%d8%a7%d8%b4%d8%aa-%d8%a8%d9%84%d8%a7%d8%aa%da%a9%d9%84%db%8c%d9%81%db%8c/feed/",
    "محاکمه_صدور_حکم":   "https://humanrightsinir.org/category/%d9%85%d8%ad%d8%a7%da%a9%d9%85%d9%87-%d8%b5%d8%af%d9%88%d8%b1-%d8%ad%da%a9%d9%85/feed/",
}

# ─── ساخت session جدید ────────────────────────────────────────────────────
def make_session():
    s = requests.Session()
    s.verify = False
    s.headers.update({
        "User-Agent":                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language":           "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding":           "gzip, deflate, br",
        "Connection":                "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest":            "document",
        "Sec-Fetch-Mode":            "navigate",
        "Sec-Fetch-Site":            "none",
        "Sec-Fetch-User":            "?1",
    })
    try:
        s.get("https://humanrightsinir.org/", timeout=15)
        time.sleep(random.uniform(2, 4))
    except:
        pass
    return s

# ─── request با retry و session reset ────────────────────────────────────
def safe_get(url, max_retries=5):
    """در صورت 429، session رو reset می‌کنه و دوباره تلاش می‌کنه"""
    global session
    delays = [10, 20, 30, 45, 60]  # تاخیر تصاعدی

    for attempt in range(max_retries):
        try:
            r = session.get(url, timeout=15)
            if r.status_code == 200:
                return r
            elif r.status_code == 429:
                wait = delays[min(attempt, len(delays)-1)]
                print(f"  ⏳ 429 — reset session + صبر {wait}s (تلاش {attempt+1}/{max_retries})")
                time.sleep(wait)
                session = make_session()  # ← session جدید با cookie تازه
            else:
                print(f"  ⚠️ Status {r.status_code}")
                return None
        except Exception as e:
            print(f"  ⚠️ خطا: {e}")
            time.sleep(10)

    return None

# ─── بهترین URL از srcset ─────────────────────────────────────────────────
def best_from_srcset(srcset_str):
    best_url, best_w = None, 0
    for part in srcset_str.split(","):
        part = part.strip()
        if not part:
            continue
        tokens = part.split()
        if len(tokens) >= 2:
            url = tokens[0]
            try:
                w = int(tokens[1].replace("w",""))
                if w > best_w:
                    best_w, best_url = w, url
            except:
                pass
        elif len(tokens) == 1:
            best_url = tokens[0]
    if best_url:
        best_url = re.sub(r'\?.*$', '', best_url)
        best_url = re.sub(r'https://i\d\.wp\.com/', 'https://', best_url)
    return best_url

# ─── گرفتن تصویر اصلی خبر ────────────────────────────────────────────────
def get_article_image(url):
    time.sleep(random.uniform(5, 9))  # ← delay بیشتر بین خبرها

    r = safe_get(url)
    if not r:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # روش ۱: .wp-post-image
    featured = soup.select_one(".wp-post-image")
    if featured:
        srcset = featured.get("srcset", "")
        if srcset:
            u = best_from_srcset(srcset)
            if u:
                return u
        orig = featured.get("data-orig-file", "")
        if orig:
            return re.sub(r'\?.*$', '', orig)
        src = featured.get("src", "")
        if src:
            return re.sub(r'\?.*$', '', src)

    # روش ۲: اولین img داخل article
    article = soup.select_one("article, .entry-content, .post-content")
    if article:
        for img in article.find_all("img"):
            src_check = img.get("src","") + "".join(img.get("class",[]))
            if any(s in src_check for s in LOGO_SKIP):
                continue
            srcset = img.get("srcset","")
            if srcset:
                u = best_from_srcset(srcset)
                if u and any(e in u for e in [".jpg",".jpeg",".png",".webp"]):
                    return u
            src = img.get("src","") or img.get("data-src","")
            if src and any(e in src for e in [".jpg",".jpeg",".png",".webp"]):
                return re.sub(r'\?.*$', '', src)

    return None

# ─── خواندن Feed ──────────────────────────────────────────────────────────
def fetch_feed(feed_name, feed_url):
    print(f"\n{'='*50}")
    print(f"📰 دسته: {feed_name}")

    r = safe_get(feed_url)
    if not r:
        print("❌ feed ناموفق")
        return []

    print(f"✅ feed دریافت شد")
    soup = BeautifulSoup(r.text, "xml")
    items = soup.find_all("item")
    print(f"📋 {len(items)} خبر\n")

    results = []
    for item in items:
        title   = item.find("title").text.strip()
        link    = item.find("link").text.strip().split("?")[0]
        pubdate = item.find("pubDate").text[:22]

        print(f"  📰 {title[:60]}")
        print(f"  📅 {pubdate}")

        img_url = get_article_image(link)
        if not img_url:
            print(f"  ⏭️  بدون تصویر — رد شد\n")
            continue

        print(f"  🖼️  {img_url[:80]}\n")
        results.append({
            "title":    title,
            "link":     link,
            "date":     pubdate,
            "image":    img_url,
            "category": feed_name,
        })

    return results

# ─── اجرای اصلی ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔄 ساخت session اولیه...")
    session = make_session()
    print("✅ Session آماده\n")

    all_news = []
    for name, url in FEEDS.items():
        time.sleep(random.uniform(5, 8))
        news = fetch_feed(name, url)
        all_news.extend(news)

    print(f"\n{'='*50}")
    print(f"✅ جمع کل: {len(all_news)} خبر با تصویر آماده ارسال به بلاگر")
    for n in all_news:
        print(f"  • {n['title'][:55]}")
        print(f"    🖼️  {n['image'][:80]}")