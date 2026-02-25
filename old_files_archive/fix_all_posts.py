"""
Fix Amjadi post - Add complete biography text
And update ALL posts to have proper source box
"""
import os
import sys
import pickle
import re
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")

def get_blogger_service():
    if not os.path.exists('token_auth_fixed.pickle'):
        return None
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    return build('blogger', 'v3', credentials=creds)

# Complete Amjadi content with FULL biography
AMJADI_FULL_CONTENT = """
<style>
@keyframes kenburns {
    0% { transform: scale(1) translate(0, 0); }
    50% { transform: scale(1.1) translate(-1%, -1%); }
    100% { transform: scale(1) translate(0, 0); }
}
.featured-img-container {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.featured-img-container img {
    width: 100%;
    display: block;
    animation: kenburns 20s ease-in-out infinite;
}
</style>
<div class="separator" style="clear: both; text-align: center; margin-bottom: 30px;">
    <div class="featured-img-container">
        <img border="0" src="https://eutoday.net/wp-content/uploads/2026/01/ChatGPT-Image-Jan-29-2026-at-11_09_24-PM.jpg" />
    </div>
</div><br/>

<div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
<p>برای سال‌ها، اتحادیه اروپا آنچه را که مقامات اغلب «صبر استراتژیک» در قبال جمهوری اسلامی ایران توصیف می‌کردند، دنبال می‌کرد. این رویکرد بر یک محاسبه استوار بود: دیپلماسی، تعامل و مذاکرات هسته‌ای می‌تواند بی‌ثباتی منطقه‌ای را کاهش دهد و با گذشت زمان، رفتار تهران را تعدیل کند.</p>

<p>آن محاسبه اکنون توسط رویدادها مورد آزمایش قرار گرفته است. در ۲۹ ژانویه ۲۰۲۶، وزرای خارجه اتحادیه اروپا توافق کردند که سپاه پاسداران انقلاب اسلامی (IRGC) را به عنوان یک سازمان تروریستی تعیین کنند؛ اقدامی که مدت‌ها در مؤسسات اروپایی مورد بحث بود.</p>

<p>به عنوان یک فعال ایرانی که در تبعید در اروپا زندگی می‌کند و به عنوان کسی که با نحوه عملکرد دولت ایران در داخل و خارج آشنا است، من مشاهده کرده‌ام که «صبر استراتژیک» به دوره‌های طولانی احتیاط اروپایی ترجمه شده است. تعامل ادامه یافت، اما سرکوب و عملیات‌های منطقه‌ای نیز ادامه یافت. بنابراین، تعیین جدید اتحادیه اروپا دارای اهمیت است. این نشان می‌دهد که دوره طولانی تردید به پایان رسیده است.</p>

<p>اما این تعیین، آغاز است، نه پایان. سپاه پاسداران صرفاً یک تشکیلات نظامی نیست. یک مرکز قدرت با گستره اقتصادی، نفوذ سیاسی و کنترل بر بخش‌هایی از زیرساخت‌های امنیتی و فناوری ایران است. همچنین از طریق شبکه‌ها و گروه‌های شریک در خارج از ایران قدرت‌نمایی می‌کند. این ویژگی‌ها دقیقاً همان چیزی است که مهار سپاه را تنها با بیانیه‌ها دشوار می‌کند.</p>

<p>موقعیت قانونی جدید اتحادیه اروپا اکنون باید با اجرای عملیاتی همراه شود. بدون آن، تأثیر عملی ممکن است کمتر از تیترهای سیاسی باشد.</p>
<!--more-->
<p>دو حوزه بلافاصله اهمیت دارند. اول، جداسازی دیجیتال و فنی. ایران سرمایه‌گذاری سنگینی در ابزارهای کنترل دیجیتال انجام داده است. در جریان اعتراضات مرتبط با جنبش «زن، زندگی، آزادی»، مقامات بر قطع اینترنت، نظارت و هدف قرار دادن فعالان تکیه کردند. شاخه‌های فنی سپاه نقش مرکزی در معماری‌ای ایفا می‌کنند که این امر را ممکن می‌سازد. همین قابلیت‌ها از فشار فراملی حمایت می‌کنند: آزار و اذیت، نظارت و ارعاب مخالفان در خارج از کشور، از جمله در اروپا.</p>

<p>این نه تنها یک موضوع حقوق بشری است، بلکه یک نگرانی امنیتی برای کشورهای اروپایی نیز می‌باشد. سپاه پاسداران و بازیگران مرتبط با آن با تهدیداتی علیه فعالان و روزنامه‌نگاران در اروپا مرتبط بوده‌اند و دولت‌های اروپایی به طور فزاینده‌ای عملیات‌های خارجی تهران را به عنوان بخشی از یک چالش امنیتی گسترده‌تر تلقی می‌کنند.</p>

<p>اگر قرار است تعیین اتحادیه اروپا تأثیرگذار باشد، مقامات اروپایی باید اطمینان حاصل کنند که فناوری اروپایی و کالاهای با کاربرد دوگانه به اکوسیستم فنی سپاه، چه به طور مستقیم و چه از طریق واسطه‌ها، نرسد.</p>

<p>دوم، اختلال مالی. پایداری سپاه به پول بستگی دارد و بخش بزرگی از قدرت اقتصادی آن از طریق کنسرسیوم‌ها، پیمانکاران و «شرکت‌های صوری» ساختاریافته است که می‌توانند سرمایه را جابجا کنند، کالاها را خریداری کنند و نفوذ ایجاد کنند.</p>

<p>تعیین سپاه، پایه قانونی قوی‌تری برای اقدام به اتحادیه اروپا می‌دهد. گام بعدی استفاده از آن است: نقشه‌برداری از ساختارهای شرکتی مرتبط با سپاه، شناسایی تسهیل‌کنندگان و پیگیری مسدود کردن دارایی‌ها و اعمال محدودیت‌ها به روش‌هایی که دور زدن آن‌ها دشوار باشد.</p>

<p>اروپا دیگر در عصر «صبر استراتژیک» نیست. ماه‌های آینده نشان خواهد داد که آیا موقعیت جدید اتحادیه اروپا به یک سیاست عمل‌گرا تبدیل می‌شود یا تصمیمی که تا حد زیادی در حد بیانیه باقی می‌ماند.</p>
</div>

<!-- Author Bio Box - COMPLETE with photo and FULL text -->
<div style="background:#fff; padding:25px; border-top:4px solid #ce0000; border-radius:8px; margin-top:40px; box-shadow:0 5px 20px rgba(0,0,0,0.1);">
    <table style="width:100%; border-collapse:collapse;">
        <tr>
            <td style="width:130px; vertical-align:top; padding-left:20px;">
                <img src="https://eutoday.net/wp-content/uploads/2026/02/cropped-OB_Hossein_Amjadi_Portrait-x.jpg" alt="Hossein Amjadi" style="width:120px; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">
            </td>
            <td style="vertical-align:top; direction:rtl; text-align:right; padding-right:20px;">
                <h3 style="margin:0 0 15px 0; color:#ce0000; font-size:1.3em; font-weight:bold; border-bottom:1px dashed #ddd; padding-bottom:10px; font-family:Tahoma,sans-serif;">درباره نویسنده: حسین امجدی</h3>
                <p style="margin:0; color:#333; line-height:2; text-align:justify; font-size:14px; font-family:Tahoma,sans-serif;">
                    <strong>حسین امجدی</strong>، فعال حقوق بشر ایرانی ساکن اوبرهاوزن آلمان و عضو انجمن <strong>VVMIran e.V.</strong> (انجمن دفاع از حقوق بشر در ایران) است. او پس از آنچه «تهدید جدی جانی» توصیف می‌کند، مجبور به ترک ایران شد. نوشته‌های او بر سرکوب دولتی، هدف قرار دادن بازداشت‌شدگان و معترضان، و وضعیت زنان در ایران تمرکز دارد. امجدی همچنین مهندس نرم‌افزار با تجربه در زیرساخت‌های حیاتی است و پژوهش‌های او بر شناسایی شبکه‌های فنی و مالی که امکان سرکوب فراملی را فراهم می‌کنند، متمرکز می‌باشد.
                </p>
            </td>
        </tr>
    </table>
</div>

<!-- Premium Source Box -->
<div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
    <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
        <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
        <a href="https://eutoday.net/iran-irgc-and-the-end-of-europes-strategic-patience/" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در EU Today</a>
    </p>
</div>
"""

# Standard source box template for all posts
SOURCE_BOX_TEMPLATE = """
<!-- Premium Source Box -->
<div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
    <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
        <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
        <a href="{url}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در {source}</a>
    </p>
</div>
"""

def fix_source_box(content):
    """Ensure post has proper 'منبع اصلی مقاله' source box"""
    
    # Extract existing URL and source name
    url_match = re.search(r'href="([^"]+)"[^>]*>مشاهده', content)
    source_match = re.search(r'مشاهده در ([^<]+)', content)
    
    url = url_match.group(1) if url_match else "#"
    source = source_match.group(1) if source_match else "منبع"
    
    # Check if already has the correct format with "منبع اصلی مقاله"
    if 'منبع اصلی مقاله' in content and 'background:#ce0000' in content:
        return content, False
    
    # Remove old source boxes (various patterns)
    patterns_to_remove = [
        r'<!-- Premium Source Box.*?</div>\s*</div>',
        r'<div[^>]*margin-top:40px[^>]*>.*?منبع.*?</div>\s*</div>',
        r'<div[^>]*>.*?<p[^>]*>.*?منبع خبر:.*?</p>.*?</div>',
    ]
    
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Add the new source box at the end
    new_source_box = SOURCE_BOX_TEMPLATE.format(url=url, source=source)
    content = content.strip() + new_source_box
    
    return content, True

def update_all_posts():
    service = get_blogger_service()
    if not service:
        print("❌ No credentials.")
        return
    
    print("📝 Step 1: Updating Amjadi post with FULL biography...")
    
    try:
        # First update Amjadi post
        posts = service.posts().list(blogId=BLOG_ID, maxResults=50).execute().get('items', [])
        
        amjadi_updated = False
        for post in posts:
            if 'حسین امجدی' in post.get('title', ''):
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=post['id'],
                    body={"content": AMJADI_FULL_CONTENT, "labels": ["گزارش ویژه", "بین‌الملل", "حسین امجدی"]}
                ).execute()
                print(f"  ✅ Amjadi post updated with full biography")
                amjadi_updated = True
                break
        
        if not amjadi_updated:
            print("  ⚠️ Amjadi post not found")
        
        print("\n📝 Step 2: Updating ALL posts with 'منبع اصلی مقاله' box...")
        
        updated_count = 0
        for post in posts:
            title = post.get('title', '')[:50]
            content = post.get('content', '')
            
            # Skip Amjadi (already updated)
            if 'حسین امجدی' in post.get('title', ''):
                continue
            
            new_content, was_changed = fix_source_box(content)
            
            # Also fix text colors
            new_content = new_content.replace('color:#eee', 'color:#fff')
            new_content = new_content.replace('color:#ddd', 'color:#fff')
            new_content = new_content.replace('color:#ccc', 'color:#fff')
            
            if was_changed or 'color:#fff' not in content:
                print(f"  🔄 Updating: {title}...")
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=post['id'],
                    body={"content": new_content}
                ).execute()
                updated_count += 1
            else:
                print(f"  ✓ OK: {title}")
        
        print(f"\n✅ Updated {updated_count} posts with proper source box and white text.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_all_posts()
