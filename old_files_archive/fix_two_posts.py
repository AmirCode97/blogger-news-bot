"""
Fix 2 posts:
1. EU Today (English→Persian) + Author bio
2. LokalKlick (German→Persian) + Author bio
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

import os, pickle, time
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

# ============================================================
# AUTHOR BIO SECTION (same for both posts)
# ============================================================
AUTHOR_BIO_EUTODAY = """
<div style="margin-top:50px;padding:30px;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:12px;border-right:4px solid #ce0000;direction:rtl;text-align:right;box-shadow:0 8px 25px rgba(0,0,0,0.3);">
    <div style="display:flex;align-items:center;gap:20px;flex-direction:row-reverse;">
        <img src="https://eutoday.net/wp-content/uploads/2026/02/cropped-OB_Hossein_Amjadi_Portrait-x.jpg" 
             alt="حسین امجدی" 
             style="width:100px;height:100px;border-radius:50%;border:3px solid #ce0000;object-fit:cover;box-shadow:0 4px 15px rgba(206,0,0,0.3);">
        <div>
            <h3 style="margin:0 0 10px 0;color:#fff;font-size:20px;font-family:'Vazir',Tahoma,sans-serif;">حسین امجدی</h3>
            <p style="margin:0;color:#ccc;font-size:14px;line-height:2;font-family:'Vazir',Tahoma,sans-serif;">
                فعال حقوق بشر ایرانی مقیم اوبرهاوزن، آلمان و عضو انجمن دفاع از حقوق بشر در ایران 
                (<span style="direction:ltr;unicode-bidi:embed;">VVMIran e.V.</span>). 
                او پس از تهدید جدی به جانش ایران را ترک کرد و اکنون درباره سرکوب دولتی، وضعیت بازداشت‌شدگان و معترضان، و جایگاه زنان در ایران می‌نویسد. 
                امجدی همچنین مهندس نرم‌افزار با تجربه در زیرساخت‌های حیاتی است و بر شبکه‌های فنی و مالی‌ای تمرکز دارد که سرکوب فرامرزی را ممکن می‌سازند.
            </p>
        </div>
    </div>
</div>
"""

AUTHOR_BIO_LOKALKLICK = """
<div style="margin-top:50px;padding:30px;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:12px;border-right:4px solid #ce0000;direction:rtl;text-align:right;box-shadow:0 8px 25px rgba(0,0,0,0.3);">
    <div style="display:flex;align-items:center;gap:20px;flex-direction:row-reverse;">
        <img src="https://lokalklick.eu/wp-content/uploads/2026/01/OB_Hossein_Amjadi_Portrait.jpg" 
             alt="حسین امجدی" 
             style="width:100px;height:100px;border-radius:50%;border:3px solid #ce0000;object-fit:cover;box-shadow:0 4px 15px rgba(206,0,0,0.3);">
        <div>
            <h3 style="margin:0 0 10px 0;color:#fff;font-size:20px;font-family:'Vazir',Tahoma,sans-serif;">حسین امجدی</h3>
            <p style="margin:0;color:#ccc;font-size:14px;line-height:2;font-family:'Vazir',Tahoma,sans-serif;">
                فعال حقوق بشر ایرانی مقیم اوبرهاوزن، آلمان و عضو انجمن دفاع از حقوق بشر در ایران 
                (<span style="direction:ltr;unicode-bidi:embed;">VVMIran e.V.</span>). 
                او پس از تهدید جدی به جانش ایران را ترک کرد و اکنون درباره سرکوب دولتی، وضعیت بازداشت‌شدگان و معترضان، و جایگاه زنان در ایران می‌نویسد. 
                امجدی همچنین مهندس نرم‌افزار با تجربه در زیرساخت‌های حیاتی است و بر شبکه‌های فنی و مالی‌ای تمرکز دارد که سرکوب فرامرزی را ممکن می‌سازند.
            </p>
        </div>
    </div>
</div>
"""

# ============================================================
# POST 1: EU Today - Persian Translation
# ============================================================
EU_TODAY_PERSIAN = """این محاسبه اکنون در بوته آزمایش رویدادها قرار گرفته است. در ۲۹ ژانویه ۲۰۲۶، وزیران خارجه اتحادیه اروپا توافق کردند که سپاه پاسداران انقلاب اسلامی (سپاه) را به عنوان یک سازمان تروریستی تعیین کنند؛ گامی که مدت‌ها در نهادهای اروپایی مورد بحث بود.

<p style="margin-bottom:15px;">به عنوان یک فعال ایرانی در تبعید در اروپا و به عنوان کسی که با نحوه عملکرد دولت ایران در داخل و خارج آشناست، شاهد بوده‌ام که «صبر استراتژیک» به دوره‌های طولانی احتیاط اروپایی ترجمه شده است. تعامل ادامه یافت، اما سرکوب و عملیات منطقه‌ای نیز ادامه پیدا کرد. بنابراین تعیین جدید اتحادیه اروپا مهم است. این نشان می‌دهد که دوره طولانی تردید به پایان رسیده است.</p>

<p style="margin-bottom:15px;">اما تعیین، آغاز است نه پایان.</p>

<p style="margin-bottom:15px;">سپاه صرفاً یک تشکیلات نظامی نیست. بلکه یک مرکز قدرت با دسترسی اقتصادی، نفوذ سیاسی و کنترل بر بخش‌هایی از زیرساخت‌های امنیتی و فناوری ایران است. همچنین از طریق شبکه‌ها و گروه‌های شریک در خارج از ایران نیرو عرضه می‌کند. این ویژگی‌ها دقیقاً همان چیزی است که مهار سپاه را تنها با بیانیه دشوار می‌سازد.</p>

<p style="margin-bottom:15px;">موضع حقوقی جدید اتحادیه اروپا اکنون باید با اجرای عملیاتی همراه شود. بدون آن، تأثیر عملی ممکن است از تیتر سیاسی کمتر باشد.</p>

<p style="margin-bottom:15px;"><strong>اول، جداسازی دیجیتال و فنی.</strong> ایران سرمایه‌گذاری سنگینی در ابزارهای کنترل دیجیتال کرده است. در جریان اعتراضات مرتبط با جنبش «زن، زندگی، آزادی»، مقامات به قطع اینترنت، نظارت و هدف قرار دادن فعالان تکیه کردند. بال‌های فنی سپاه نقش محوری در معماری‌ای ایفا می‌کنند که این امر را ممکن می‌سازد. همان توانایی‌ها از فشار فرامرزی پشتیبانی می‌کنند: آزار و اذیت، نظارت و ارعاب مخالفان در خارج از کشور، از جمله در اروپا.</p>

<p style="margin-bottom:15px;">این فقط یک مسئله حقوق بشری نیست. بلکه یک نگرانی امنیتی برای کشورهای اروپایی نیز هست. سپاه و بازیگران مرتبط با تهدید علیه فعالان و روزنامه‌نگاران در اروپا مرتبط بوده‌اند و دولت‌های اروپایی به طور فزاینده‌ای عملیات خارجی تهران را بخشی از یک چالش امنیتی گسترده‌تر تلقی می‌کنند.</p>

<p style="margin-bottom:15px;">اگر تعیین اتحادیه اروپا قرار است تأثیر داشته باشد، مقامات اروپایی باید اطمینان حاصل کنند که فناوری و کالاهای دومنظوره اروپایی به اکوسیستم فنی سپاه نمی‌رسد، چه مستقیم و چه از طریق واسطه‌ها.</p>

<p style="margin-bottom:15px;"><strong>دوم، اختلال مالی.</strong> دوام سپاه به پول بستگی دارد و بخش زیادی از قدرت اقتصادی آن از طریق کنسرسیوم‌ها، پیمانکاران و «شرکت‌های پوششی» ساختار یافته است که می‌توانند سرمایه جابجا کنند، کالا تهیه کنند و نفوذ بسازند.</p>

<p style="margin-bottom:15px;">تعیین، پایه حقوقی قوی‌تری برای اقدام به اتحادیه اروپا می‌دهد. گام بعدی استفاده از آن است: نقشه‌برداری ساختارهای شرکتی مرتبط با سپاه، شناسایی تسهیل‌کنندگان، و پیگیری مسدودسازی دارایی‌ها و محدودیت‌هایی که دشوار باشد از آنها فرار کرد.</p>

<p style="margin-bottom:15px;">اگر اروپا پاسخ خود را به عمل تعیین محدود کند، شبکه‌های سپاه می‌توانند سازگار شوند. چالش، کاهش توانایی سازمان برای عملیات فرامرزی، جذب بودجه، تهیه تجهیزات و ارعاب مخالفان در خارج از کشور است.</p>

<p style="margin-bottom:15px;">ایران قبلاً از نظر سیاسی واکنش نشان داده است. در روزهای پس از اقدام اتحادیه اروپا، مقامات ایرانی سیگنال تلافی‌جویی دادند، از جمله بیانیه‌هایی مبنی بر اینکه تهران نیروهای مسلح کشورهای عضو اتحادیه اروپا را به عنوان «گروه‌های تروریستی» تلقی خواهد کرد.</p>

<p style="margin-bottom:15px;">برای اتحادیه اروپا، سؤال سیاسی اکنون عملی می‌شود. مهار پس از تعیین حقوقی، به صورت قابل اندازه‌گیری چگونه به نظر می‌رسد؟</p>

<p style="margin-bottom:15px;">می‌تواند شامل موارد زیر باشد: اجرای سخت‌گیرانه‌تر کنترل صادرات در برابر انحراف کالاهای دومنظوره؛ تحقیقات هماهنگ در مورد مسیرهای تدارک؛ شناسایی سیستماتیک کسب‌وکارها و واسطه‌های وابسته به سپاه؛ و فشار مداوم بر کانال‌های مالی.</p>

<p style="margin-bottom:15px;">هیچکدام از اینها مستلزم رها کردن دیپلماسی نیست. بلکه به وضوح درباره آنچه دیپلماسی می‌تواند و نمی‌تواند انجام دهد در زمانی که سازمانی در مرکز سرکوب داخلی و عملیات خارجی قرار دارد، نیاز است. اتحادیه اروپا یک گام رسمی برداشته که بسیاری معتقد بودند با تأخیر انجام شده است. اعتبار این گام بستگی به این دارد که آیا با مهار فعال دنبال می‌شود یا خیر.</p>"""

# ============================================================
# POST 2: LokalKlick - Persian Translation
# ============================================================
LOKALKLICK_PERSIAN = """اوبرهاوزن/راین–رور. در هفته‌ها و ماه‌های گذشته، خیابان‌های ایران بار دیگر به مکان‌هایی تبدیل شده‌اند که وجدان هر انسان آزادی‌خواهی را تکان می‌دهند. مردم بدون سلاح به خیابان‌ها می‌آیند، با صداهای لرزان اما با خواسته‌ای روشن: کرامت، آزادی و آینده‌ای قابل زیست. پاسخ به این خواسته‌ها، در بسیاری از موارد، مرگبار بوده است.

<p style="margin-bottom:15px;">زنان و دختران جوان در اعتراضات جایگاه ویژه‌ای دارند. آنها با شجاعت بی‌نظیری در صف اول مبارزه ایستاده‌اند. اما بهای این شجاعت سنگین بوده است: بازداشت‌های خودسرانه، شکنجه در بازداشتگاه‌ها و حتی خشونت جنسی از سوی نیروهای امنیتی. زنان زندانی از ابتدایی‌ترین حقوق انسانی محروم‌اند.</p>

<p style="margin-bottom:15px;"><strong>کشته‌شدگان:</strong> شمار قربانیان سرکوب روز به روز افزایش می‌یابد. نیروهای امنیتی بدون هیچ تردیدی به سوی معترضان غیرمسلح شلیک می‌کنند. گلوله‌های جنگی، ساچمه و گاز اشک‌آور به وفور استفاده می‌شود. خانواده‌های قربانیان تحت فشار قرار می‌گیرند تا سکوت کنند و اجازه برگزاری مراسم ترحیم داده نمی‌شود.</p>

<p style="margin-bottom:15px;"><strong>زندانیان:</strong> هزاران نفر در زندان‌ها، بازداشتگاه‌های موقت و مراکز نگهداری غیررسمی محبوس هستند. گزارش‌های متعددی از شکنجه سیستماتیک، اعترافات اجباری زیر فشار و محاکمات فرمایشی رسیده است. بسیاری از زندانیان از دسترسی به وکیل و خدمات پزشکی محروم‌اند.</p>

<p style="margin-bottom:15px;"><strong>زنان در ایران:</strong> وضعیت زنان در ایران همواره نگران‌کننده بوده، اما در ماه‌های اخیر به شکل بی‌سابقه‌ای وخیم شده است. زنان نه تنها به دلیل مشارکت در اعتراضات، بلکه صرفاً به خاطر حجاب، فعالیت در شبکه‌های اجتماعی یا دفاع از حقوق اولیه خود بازداشت و مجازات می‌شوند.</p>

<p style="margin-bottom:15px;">جامعه بین‌المللی در مقابل آنچه در ایران می‌گذرد، مسئولیت دارد. سکوت در برابر این جنایات، نه بی‌طرفی، بلکه همدستی با سرکوبگران است. هر دولت، هر نهاد و هر شهروندی که در برابر این واقعیت سکوت می‌کند، در عمل به تداوم این فاجعه انسانی کمک می‌کند.</p>

<p style="margin-bottom:15px;">ما از تمام دولت‌ها و نهادهای بین‌المللی می‌خواهیم که صدای مردم ایران باشند، از تحریم‌های هدفمند علیه عوامل سرکوب حمایت کنند و بر آزادی فوری زندانیان سیاسی اصرار ورزند. تاریخ از کسانی که سکوت کردند نخواهد گذشت.</p>"""


def build_post_html(persian_content, image_url, source_url, source_name, author_bio_html):
    """Build properly formatted post with Persian content + author bio"""
    
    image_html = ""
    if image_url:
        image_html = f'<div style="margin-bottom:25px;text-align:center;"><img src="{image_url}" style="width:100%;max-width:800px;border-radius:12px;box-shadow:0 5px 20px rgba(0,0,0,0.4);" alt=""></div>'
    
    html = f"""
<style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
{image_html}

<!-- Persian Content -->
<div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',Tahoma,sans-serif;">
    {persian_content}
</div>

<!-- Author Bio -->
{author_bio_html}

<!-- Premium Source Box -->
<div style="margin-top:30px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
    <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
        <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
        <a href="{source_url}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در {source_name}</a>
    </p>
</div>
"""
    return html


# ============================================
# MAIN: Update both posts
# ============================================
all_posts = []
page_token = None
while True:
    result = service.posts().list(blogId=BLOG_ID, maxResults=50, fetchBodies=True, pageToken=page_token).execute()
    all_posts.extend(result.get("items", []))
    page_token = result.get("nextPageToken")
    if not page_token:
        break

for p in all_posts:
    title = p.get("title","")
    post_id = p.get("id")
    
    # POST 1: EU Today
    if "سپاه پاسداران و پایان صبر" in title:
        print(f"\n🔧 Fixing POST 1: {title[:60]}...")
        
        new_html = build_post_html(
            persian_content=EU_TODAY_PERSIAN,
            image_url="https://eutoday.net/wp-content/uploads/2026/01/ChatGPT-Image-Jan-29-2026-at-11_09_24-PM.jpg",
            source_url="https://eutoday.net/iran-irgc-and-the-end-of-europes-strategic-patience/",
            source_name="EU Today",
            author_bio_html=AUTHOR_BIO_EUTODAY
        )
        
        try:
            service.posts().patch(
                blogId=BLOG_ID, postId=post_id,
                body={"content": new_html}
            ).execute()
            print(f"   ✅ Updated! Persian content + author bio + photo")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)
    
    # POST 2: LokalKlick  
    if "کشته‌شدگان، زندانیان و زنان در ایران" in title:
        print(f"\n🔧 Fixing POST 2: {title[:60]}...")
        
        new_html = build_post_html(
            persian_content=LOKALKLICK_PERSIAN,
            image_url="https://lokalklick.eu/wp-content/uploads/2026/01/ChatGPT-Image-Jan-26-2026-at-12_56_03-AM.jpg",
            source_url="https://lokalklick.eu/2026/01/26/klarklick-getoetete-inhaftierte-und-die-frauen-im-iran-wenn-schweigen-zur-mittaeterschaft-wird/",
            source_name="LokalKlick.eu",
            author_bio_html=AUTHOR_BIO_LOKALKLICK
        )
        
        try:
            service.posts().patch(
                blogId=BLOG_ID, postId=post_id,
                body={"content": new_html}
            ).execute()
            print(f"   ✅ Updated! Persian content + author bio + photo")
        except Exception as e:
            print(f"   ❌ Error: {e}")

print(f"\n{'='*60}")
print(f"✅ Done! Both posts updated.")
print(f"{'='*60}")
