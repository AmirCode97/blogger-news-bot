
import os
import sys
from blogger_poster import BloggerPoster
from dotenv import load_dotenv

load_dotenv()

# Force text encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

FA_TITLE = "ایران، سپاه پاسداران و پایان صبر استراتژیک اروپا؛ یادداشتی از حسین امجدی"
TARGET_URL = "https://eutoday.net/iran-irgc-and-the-end-of-europes-strategic-patience/"

# تصویر اصلی مقاله با افکت سینمایی (Ken Burns)
FEATURED_IMG_HTML = """
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
"""

FA_BODY = """
<div style="font-size:17px;line-height:2.2;color:#eee;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;">
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
"""

# کادر بیوگرافی با عکس - دقیقا مشابه عکس ارسالی کاربر (عکس در سمت چپ، متن در سمت راست)
# Updated text color for Dark Mode compatibility (#111 title on White bg is fine, p #444 on White is fine)
AUTHOR_BIO_FA_HTML = """
<div style="background-color: #ffffff; padding: 25px; border-top: 4px solid #ce0000; border-radius: 8px; margin-top: 40px; font-family: 'Tahoma', sans-serif; display: flex; flex-direction: row; gap: 20px; align-items: flex-start; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
    <div style="flex-shrink: 0; width: 130px;">
        <img src="https://eutoday.net/wp-content/uploads/2026/02/cropped-OB_Hossein_Amjadi_Portrait-x.jpg" alt="Hossein Amjadi" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
    </div>
    <div style="flex-grow: 1; direction: rtl;">
        <h3 style="margin: 0 0 10px 0; color: #ce0000; font-size: 1.3em; font-weight: bold; text-align: right; text-transform: uppercase; border-bottom: 1px dashed #ddd; padding-bottom: 8px;">درباره نویسنده: حسین امجدی</h3>
        <p style="margin: 0; color: #444; line-height: 1.9; text-align: justify; font-size: 0.95em;">
            <strong>حسین امجدی</strong>، فعال حقوق بشر ایرانی ساکن اوبرهاوزن آلمان و عضو انجمن <strong>VVMIran e.V.</strong> (انجمن دفاع از حقوق بشر در ایران) است. 
            او پس از آنچه «تهدید جدی جانی» توصیف می‌کند، مجبور به ترک ایران شد. نوشته‌های او بر سرکوب دولتی، هدف قرار دادن بازداشت‌شدگان و معترضان، و وضعیت زنان در ایران تمرکز دارد. 
            امجدی همچنین مهندس نرم‌افزار با تجربه در زیرساخت‌های حیاتی است و پژوهش‌های او بر شناسایی شبکه‌های فنی و مالی که امکان سرکوب فراملی را فراهم می‌کنند، متمرکز می‌باشد.
        </p>
    </div>
</div>
"""

# لینک منبع - Updated to Premium Button Style
SOURCE_HTML = f"""
<div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;display:flex;align-items:center;justify-content:flex-end;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
    <p style="margin:0;font-size:14px;color:#888;font-family:'Vazir',sans-serif;display:flex;align-items:center;">
        <span style="opacity:0.8;margin-left:15px;">منبع اصلی مقاله:</span> 
        <a href="{TARGET_URL}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);transition:0.3s;">مشاهده در EU Today</a>
    </p>
</div>
"""

def create_post():
    print(f"Creating Hossein Amjadi Post...")
    try:
        poster = BloggerPoster()
        if not poster.service: return
        
        final_content = FEATURED_IMG_HTML + FA_BODY + AUTHOR_BIO_FA_HTML + SOURCE_HTML
        
        # Insert new post
        result = poster.create_post(
            title=FA_TITLE,
            content=final_content,
            labels=["گزارش ویژه", "بین‌الملل", "حسین امجدی", "سپاه پاسداران"],
            is_draft=False
        )
        
        if result:
            print(f"✅ پست با موفقیت ایجاد شد: {result.get('url')}")
        else:
            print("❌ خطا در ایجاد پست.")
            
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    create_post()
