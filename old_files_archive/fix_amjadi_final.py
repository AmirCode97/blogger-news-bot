"""
Fix Amjadi Post - FINAL VERSION with complete visible biography
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

def get_blogger_service():
    if not os.path.exists('token_auth_fixed.pickle'):
        return None
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    return build('blogger', 'v3', credentials=creds)

# Complete Amjadi post with VISIBLE biography
AMJADI_COMPLETE = """
<style>
@keyframes kenburns {
    0% { transform: scale(1) translate(0, 0); }
    50% { transform: scale(1.1) translate(-1%, -1%); }
    100% { transform: scale(1) translate(0, 0); }
}
</style>

<!-- Featured Image -->
<div style="text-align:center; margin-bottom:30px;">
    <img src="https://eutoday.net/wp-content/uploads/2026/01/ChatGPT-Image-Jan-29-2026-at-11_09_24-PM.jpg" style="width:100%; max-width:800px; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.3); animation: kenburns 20s ease-in-out infinite;">
</div>

<!-- Article Content - WHITE TEXT -->
<div style="font-size:17px; line-height:2.2; color:#fff; text-align:justify; direction:rtl; font-family:'Vazir',Tahoma,sans-serif;">

<p>برای سال‌ها، اتحادیه اروپا آنچه را که مقامات اغلب «صبر استراتژیک» در قبال جمهوری اسلامی ایران توصیف می‌کردند، دنبال می‌کرد. این رویکرد بر یک محاسبه استوار بود: دیپلماسی، تعامل و مذاکرات هسته‌ای می‌تواند بی‌ثباتی منطقه‌ای را کاهش دهد و با گذشت زمان، رفتار تهران را تعدیل کند.</p>

<p>آن محاسبه اکنون توسط رویدادها مورد آزمایش قرار گرفته است. در ۲۹ ژانویه ۲۰۲۶، وزرای خارجه اتحادیه اروپا توافق کردند که سپاه پاسداران انقلاب اسلامی (IRGC) را به عنوان یک سازمان تروریستی تعیین کنند؛ اقدامی که مدت‌ها در مؤسسات اروپایی مورد بحث بود.</p>

<p>به عنوان یک فعال ایرانی که در تبعید در اروپا زندگی می‌کند و به عنوان کسی که با نحوه عملکرد دولت ایران در داخل و خارج آشنا است، من مشاهده کرده‌ام که «صبر استراتژیک» به دوره‌های طولانی احتیاط اروپایی ترجمه شده است. تعامل ادامه یافت، اما سرکوب و عملیات‌های منطقه‌ای نیز ادامه یافت. بنابراین، تعیین جدید اتحادیه اروپا دارای اهمیت است. این نشان می‌دهد که دوره طولانی تردید به پایان رسیده است.</p>

<p>اما این تعیین، آغاز است، نه پایان. سپاه پاسداران صرفاً یک تشکیلات نظامی نیست. یک مرکز قدرت با گستره اقتصادی، نفوذ سیاسی و کنترل بر بخش‌هایی از زیرساخت‌های امنیتی و فناوری ایران است. همچنین از طریق شبکه‌ها و گروه‌های شریک در خارج از ایران قدرت‌نمایی می‌کند.</p>

<p>موقعیت قانونی جدید اتحادیه اروپا اکنون باید با اجرای عملیاتی همراه شود. بدون آن، تأثیر عملی ممکن است کمتر از تیترهای سیاسی باشد.</p>

<!--more-->

<p>دو حوزه بلافاصله اهمیت دارند. اول، جداسازی دیجیتال و فنی. ایران سرمایه‌گذاری سنگینی در ابزارهای کنترل دیجیتال انجام داده است. در جریان اعتراضات مرتبط با جنبش «زن، زندگی، آزادی»، مقامات بر قطع اینترنت، نظارت و هدف قرار دادن فعالان تکیه کردند.</p>

<p>این نه تنها یک موضوع حقوق بشری است، بلکه یک نگرانی امنیتی برای کشورهای اروپایی نیز می‌باشد. سپاه پاسداران و بازیگران مرتبط با آن با تهدیداتی علیه فعالان و روزنامه‌نگاران در اروپا مرتبط بوده‌اند.</p>

<p>اگر قرار است تعیین اتحادیه اروپا تأثیرگذار باشد، مقامات اروپایی باید اطمینان حاصل کنند که فناوری اروپایی و کالاهای با کاربرد دوگانه به اکوسیستم فنی سپاه نرسد.</p>

<p>دوم، اختلال مالی. پایداری سپاه به پول بستگی دارد و بخش بزرگی از قدرت اقتصادی آن از طریق کنسرسیوم‌ها، پیمانکاران و «شرکت‌های صوری» ساختاریافته است.</p>

<p>تعیین سپاه، پایه قانونی قوی‌تری برای اقدام به اتحادیه اروپا می‌دهد. گام بعدی استفاده از آن است: نقشه‌برداری از ساختارهای شرکتی مرتبط با سپاه و پیگیری مسدود کردن دارایی‌ها.</p>

<p>اروپا دیگر در عصر «صبر استراتژیک» نیست. ماه‌های آینده نشان خواهد داد که آیا موقعیت جدید اتحادیه اروپا به یک سیاست عمل‌گرا تبدیل می‌شود یا تصمیمی در حد بیانیه باقی می‌ماند.</p>

</div>

<!-- AUTHOR BIO BOX - With Photo and FULL Text -->
<div style="background:#fff; margin-top:40px; padding:0; border-radius:8px; overflow:hidden; box-shadow:0 5px 20px rgba(0,0,0,0.15); border-top:4px solid #ce0000;">
    
    <!-- Header -->
    <div style="background:#ce0000; color:#fff; padding:15px 20px; font-family:Tahoma,sans-serif;">
        <strong style="font-size:16px;">درباره نویسنده: حسین امجدی</strong>
    </div>
    
    <!-- Content with Photo -->
    <div style="padding:20px; display:flex; gap:20px; align-items:flex-start;">
        
        <!-- Photo -->
        <div style="flex-shrink:0;">
            <img src="https://eutoday.net/wp-content/uploads/2026/02/cropped-OB_Hossein_Amjadi_Portrait-x.jpg" 
                 style="width:120px; height:150px; object-fit:cover; border-radius:8px; box-shadow:0 4px 10px rgba(0,0,0,0.2);">
        </div>
        
        <!-- Biography Text -->
        <div style="flex-grow:1; direction:rtl; text-align:justify; line-height:1.9; font-size:14px; color:#333; font-family:Tahoma,sans-serif;">
            <strong>حسین امجدی</strong>، فعال حقوق بشر ایرانی ساکن اوبرهاوزن آلمان و عضو انجمن <strong style="color:#ce0000;">VVMIran e.V.</strong> (انجمن دفاع از حقوق بشر در ایران) است.
            <br><br>
            او پس از آنچه «تهدید جدی جانی» توصیف می‌کند، مجبور به ترک ایران شد. نوشته‌های او بر سرکوب دولتی، هدف قرار دادن بازداشت‌شدگان و معترضان، و وضعیت زنان در ایران تمرکز دارد.
            <br><br>
            امجدی همچنین <strong>مهندس نرم‌افزار</strong> با تجربه در زیرساخت‌های حیاتی است و پژوهش‌های او بر شناسایی شبکه‌های فنی و مالی که امکان سرکوب فراملی را فراهم می‌کنند، متمرکز می‌باشد.
        </div>
        
    </div>
</div>

<!-- Source Box -->
<div style="margin-top:40px; padding:25px; background:#fff; border-right:5px solid #ce0000; border-radius:8px; text-align:right; direction:rtl; box-shadow:0 5px 15px rgba(0,0,0,0.05);">
    <p style="margin:0; font-size:14px; color:#555; font-family:Tahoma,sans-serif;">
        <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
        <a href="https://eutoday.net/iran-irgc-and-the-end-of-europes-strategic-patience/" target="_blank" style="background:#ce0000; color:#fff; padding:10px 20px; border-radius:6px; text-decoration:none; font-weight:bold; font-size:13px; box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در EU Today</a>
    </p>
</div>
"""

def fix_amjadi():
    service = get_blogger_service()
    if not service:
        print("❌ No credentials")
        return
    
    print("🔍 Finding Amjadi post...")
    
    try:
        posts = service.posts().list(blogId=BLOG_ID, maxResults=50).execute().get('items', [])
        
        for post in posts:
            if 'حسین امجدی' in post.get('title', ''):
                print(f"📝 Found: {post['title'][:50]}...")
                
                service.posts().patch(
                    blogId=BLOG_ID,
                    postId=post['id'],
                    body={
                        "content": AMJADI_COMPLETE,
                        "labels": ["گزارش ویژه", "بین‌الملل", "حسین امجدی", "سپاه پاسداران"]
                    }
                ).execute()
                
                print(f"✅ Updated successfully!")
                return
        
        print("⚠️ Post not found, creating new...")
        result = service.posts().insert(
            blogId=BLOG_ID,
            body={
                "title": "ایران، سپاه پاسداران و پایان صبر استراتژیک اروپا؛ یادداشتی از حسین امجدی",
                "content": AMJADI_COMPLETE,
                "labels": ["گزارش ویژه", "بین‌الملل", "حسین امجدی", "سپاه پاسداران"]
            }
        ).execute()
        print(f"✅ Created: {result.get('url')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_amjadi()
