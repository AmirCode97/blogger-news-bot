# تحلیل محتوای خبر از سایت‌های جدید
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

def analyze_article(url, site_name):
    print(f"\n{'='*60}")
    print(f"📄 تحلیل خبر از: {site_name}")
    print(f"   URL: {url[:60]}...")
    print('='*60)
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # عنوان
        title = soup.find('h1')
        if title:
            print(f"\n📰 عنوان: {title.get_text(strip=True)[:80]}...")
        
        # محتوا - امتحان سلکتورهای مختلف
        content_selectors = [
            '.entry-content',
            '.post-content', 
            '.article-content',
            '.content',
            'article .content',
            '#content',
            '.single-content',
            '.main-content'
        ]
        
        for sel in content_selectors:
            content = soup.select_one(sel)
            if content:
                ps = content.find_all('p')
                if ps:
                    print(f"\n✅ سلکتور محتوا: {sel}")
                    print(f"   تعداد پاراگراف: {len(ps)}")
                    print(f"\n   [پاراگراف ۱]:")
                    print(f"   {ps[0].get_text(strip=True)[:150]}...")
                    if len(ps) > 1:
                        print(f"\n   [پاراگراف ۲]:")
                        print(f"   {ps[1].get_text(strip=True)[:150]}...")
                    break
        
        # همچنین همه پاراگراف‌ها
        all_ps = soup.find_all('p')
        persian_ps = [p for p in all_ps if sum(1 for c in p.get_text() if '\u0600' <= c <= '\u06FF') > 20]
        print(f"\n   کل پاراگراف‌های فارسی: {len(persian_ps)}")
        
    except Exception as e:
        print(f"❌ خطا: {e}")

# تست با یک خبر از هر سایت
# مرکز اسناد
analyze_article('https://persian.iranhumanrights.org/1404/11/unreported-deaths/', 'مرکز اسناد حقوق بشر')

# ناظران
analyze_article('https://fa.iran-hrm.com/%d8%ac%d8%b1%d9%85%d8%a7%d9%86%da%af%d8%a7%d8%b1%db%8c-%d8%b3%d9%88%da%af%d9%86%d8%af-%d9%be%d8%b2%d8%b4%da%a9%db%8c/', 'ناظران حقوق بشر')
