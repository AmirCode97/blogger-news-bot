"""
Update Hossein Amjadi Article - Fix Image and Persian Only
"""

import os
import sys
import pickle
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

# Correct author image
AUTHOR_IMAGE = "https://lokalklick.eu/wp-content/uploads/2026/01/OB_Hossein_Amjadi_Portrait.jpg"
ARTICLE_URL = "https://lokalklick.eu/2026/01/26/klarklick-getoetete-inhaftierte-und-die-frauen-im-iran-wenn-schweigen-zur-mittaeterschaft-wird/"

TITLE = "کشته‌شدگان، زندانیان و زنان در ایران - وقتی سکوت به همدستی تبدیل می‌شود"

CONTENT_FA = """
<p>در هفته‌ها و ماه‌های گذشته، خیابان‌های ایران بار دیگر به مکان‌هایی تبدیل شده‌اند که وجدان هر انسان آزاده‌ای را به لرزه درمی‌آورند. مردم بدون سلاح به خیابان‌ها می‌آیند، با صداهای لرزان، اما با یک خواسته روشن: کرامت، آزادی و آینده‌ای قابل زندگی. پاسخ به این خواسته‌ها در بسیاری از نقاط، خشونت بی‌رحمانه است. نام‌هایی که دیگر هرگز به خانه بازنمی‌گردند. چهره‌هایی که پشت دیوارهای زندان در سکوت ناپدید می‌شوند.</p>

<p>کشته‌شدگان اعتراضات اخیر فقط اعداد یا آمار نیستند. آن‌ها دختران و پسران، خواهران و برادران، والدین بودند - انسان‌هایی با یک زندگی کاملاً عادی. تنها «جرم» آن‌ها این بود که حقوق اساسی را مطالبه کردند: حق زندگی، حق اعتراض مسالمت‌آمیز و حق شنیده شدن. استفاده از خشونت مرگبار علیه معترضان غیرمسلح، نقض آشکار حق حیات است - همان حقی که در ماده اول اعلامیه جهانی حقوق بشر تضمین شده است.</p>

<p>در کنار کشته‌شدگان، هزاران بازداشت‌شده وجود دارند. زنان و مردانی که بدون محاکمه عادلانه، بدون دسترسی مؤثر به وکیل و گاهی بدون اطلاع‌رسانی به خانواده‌هایشان دستگیر شده‌اند. گزارش‌های متعدد از بدرفتاری، فشار روانی، شکنجه و اعترافات اجباری، تصویری هولناک از شرایط بازداشت ترسیم می‌کنند. برای بسیاری، زندان نه مکان اجرای عدالت، بلکه ابزاری برای خاموش کردن صداها است.</p>

<p>در مرکز این سرکوب، زنان قرار دارند. زنانی که نه فقط برای حقوق سیاسی یا اجتماعی مبارزه می‌کنند، بلکه برای اساسی‌ترین حق: تعیین سرنوشت بدن و زندگی خودشان. آن‌ها در خیابان‌ها با خشونت مواجه می‌شوند، در بازداشت تحت فشار ویژه قرار می‌گیرند و در زندگی روزمره به طور سیستماتیک تبعیض می‌بینند. بنابراین اعتراض زنان در ایران بسیار فراتر از یک مطالبه سیاسی است - این فریادی برای کرامت انسانی است.</p>

<p>من این سطور را نه از منظر حزبی-سیاسی، بلکه از منظر انسانی می‌نویسم. من فعال حقوق بشر هستم، در اوبرهاوزن زندگی می‌کنم و عضو انجمن دفاع از حقوق بشر در ایران (VVMIran e.V.) هستم. پس از سال‌ها تلاش برای آزادی و حقوق بشر در ایران، به دلیل تهدید جدی جانم مجبور شدم کشورم را ترک کنم. نه برای سکوت، بلکه برای زنده ماندن و ادامه حمایت حقوق بشری و انسان‌دوستانه از هم‌وطنانم.</p>

<p style="font-size:20px;font-weight:bold;color:#ce0000;background:#1a1a2e;padding:20px;border-radius:10px;border-right:5px solid #ce0000;">قربانیان در ایران بیش از همدردی به چیزی نیاز دارند: دیده شدن، توجه و همبستگی بین‌المللی. در چنین لحظاتی، سکوت بی‌طرفی نیست. سکوت، همدستی است.</p>
"""

def main():
    print("=" * 60)
    print("📝 UPDATING ARTICLE WITH CORRECT IMAGE - PERSIAN ONLY")
    print("=" * 60)
    
    # Init Blogger API
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('blogger', 'v3', credentials=creds)
    
    # Find existing post
    posts = service.posts().list(blogId=BLOG_ID, maxResults=50).execute().get('items', [])
    target_post = None
    for post in posts:
        if 'کشته‌شدگان' in post.get('title', '') or 'Getötete' in post.get('title', ''):
            target_post = post
            break
    
    # Build HTML content - Persian Only with Author Photo
    html_content = f"""
    <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
    
    <!-- Main Author Image -->
    <div style="text-align:center;margin-bottom:30px;">
        <img src="{AUTHOR_IMAGE}" style="width:100%;max-width:800px;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.5);border:3px solid #ce0000;" alt="Hossein Amjadi - حسین امجدی">
    </div>
    
    <!-- Author Info Box -->
    <div style="background:linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);border-radius:12px;padding:25px;margin-bottom:30px;border-right:5px solid #ce0000;text-align:right;direction:rtl;">
        <h3 style="color:#fff;margin:0 0 10px 0;font-size:22px;">✍️ نویسنده: حسین امجدی</h3>
        <p style="color:#aaa;margin:0;font-size:14px;line-height:1.8;">فعال حقوق بشر | ساکن اوبرهاوزن، آلمان | عضو انجمن دفاع از حقوق بشر در ایران (VVMIran e.V.)</p>
    </div>
    
    <!-- Persian Article Content -->
    <div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
        {CONTENT_FA}
    </div>
    
    <!--more-->
    
    <!-- Premium Source Box -->
    <div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
        <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
            <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
            <a href="{ARTICLE_URL}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در LokalKlick.eu</a>
        </p>
    </div>
    """
    
    if target_post:
        # Update existing post
        print(f"🔄 Updating existing post: {target_post['id']}")
        service.posts().patch(
            blogId=BLOG_ID,
            postId=target_post['id'],
            body={
                'title': TITLE,
                'content': html_content,
                'labels': ['خانه', 'گزارش ویژه', 'حقوق بشر', 'حسین امجدی']
            }
        ).execute()
        print(f"✅ Updated: {target_post.get('url')}")
    else:
        # Create new post
        print("📝 Creating new post...")
        result = service.posts().insert(
            blogId=BLOG_ID,
            body={
                'title': TITLE,
                'content': html_content,
                'labels': ['خانه', 'گزارش ویژه', 'حقوق بشر', 'حسین امجدی']
            },
            isDraft=False
        ).execute()
        print(f"✅ Published: {result.get('url')}")

if __name__ == "__main__":
    main()
