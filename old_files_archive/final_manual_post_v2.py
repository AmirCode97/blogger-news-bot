
import os
from blogger_poster import BloggerPoster
from dotenv import load_dotenv

load_dotenv()

FA_TITLE = "ایران، سپاه پاسداران و پایان صبر استراتژیک اروپا؛ یادداشتی از حسین امجدی"
TARGET_URL = "https://eutoday.net/iran-irgc-and-the-end-of-europes-strategic-patience/"

# هدر برندینگ وبلاگ (وسط‌چین و شیک)
BRAND_HEADER_HTML = """
<div style="text-align: center; margin-bottom: 40px; border-bottom: 2px solid #22d3ee; padding-bottom: 20px; font-family: 'Segoe UI', Tahoma, sans-serif;">
    <div style="font-size: 2.8em; font-weight: 900; letter-spacing: 4px; color: #05070a; text-transform: uppercase; margin: 0;">
        IRAN POL <span style="color: #22d3ee;">NEWS</span>
    </div>
    <div style="font-size: 0.85em; color: #64748b; text-transform: uppercase; letter-spacing: 6px; margin-top: 5px; font-weight: 600;">
        Investigative Journalism
    </div>
</div>
"""

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
<p style="text-align: justify; direction: rtl;">برای سال‌ها، اتحادیه اروپا آنچه را که مقامات اغلب «صبر استراتژیک» در قبال جمهوری اسلامی ایران توصیف می‌کردند، دنبال می‌کرد. این رویکرد بر یک محاسبه استوار بود: دیپلماسی، تعامل و مذاکرات هسته‌ای می‌تواند بی‌ثباتی منطقه‌ای را کاهش دهد و با گذشت زمان، رفتار تهران را تعدیل کند.</p>

<p style="text-align: justify; direction: rtl;">آن محاسبه اکنون توسط رویدادها مورد آزمایش قرار گرفته است. در ۲۹ ژانویه ۲۰۲۶، وزرای خارجه اتحادیه اروپا توافق کردند که سپاه پاسداران انقلاب اسلامی (IRGC) را به عنوان یک سازمان تروریستی تعیین کنند؛ اقدامی که مدت‌ها در مؤسسات اروپایی مورد بحث بود.</p>

<p style="text-align: justify; direction: rtl;">به عنوان یک فعال ایرانی که در تبعید در اروپا زندگی می‌کند و به عنوان کسی که با نحوه عملکرد دولت ایران در داخل و خارج آشنا است، من مشاهده کرده‌ام که «صبر استراتژیک» به دوره‌های طولانی احتیاط اروپایی ترجمه شده است. تعامل ادامه یافت، اما سرکوب و عملیات‌های منطقه‌ای نیز ادامه یافت. بنابراین، تعیین جدید اتحادیه اروپا دارای اهمیت است. این نشان می‌دهد که دوره طولانی تردید به پایان رسیده است.</p>

<p style="text-align: justify; direction: rtl;">اما این تعیین، آغاز است، نه پایان. سپاه پاسداران صرفاً یک تشکیلات نظامی نیست. یک مرکز قدرت با گستره اقتصادی، نفوذ سیاسی و کنترل بر بخش‌هایی از زیرساخت‌های امنیتی و فناوری ایران است. همچنین از طریق شبکه‌ها و گروه‌های شریک در خارج از ایران قدرت‌نمایی می‌کند. این ویژگی‌ها دقیقاً همان چیزی است که مهار سپاه را تنها با بیانیه‌ها دشوار می‌کند.</p>

<p style="text-align: justify; direction: rtl;">موقعیت قانونی جدید اتحادیه اروپا اکنون باید با اجرای عملیاتی همراه شود. بدون آن، تأثیر عملی ممکن است کمتر از تیترهای سیاسی باشد.</p>

<p style="text-align: justify; direction: rtl;">دو حوزه بلافاصله اهمیت دارند. اول، جداسازی دیجیتال و فنی. ایران سرمایه‌گذاری سنگینی در ابزارهای کنترل دیجیتال انجام داده است. در جریان اعتراضات مرتبط با جنبش «زن، زندگی، آزادی»، مقامات بر قطع اینترنت، نظارت و هدف قرار دادن فعالان تکیه کردند. شاخه‌های فنی سپاه نقش مرکزی در معماری‌ای ایفا می‌کنند که این امر را ممکن می‌سازد. همین قابلیت‌ها از فشار فراملی حمایت می‌کنند: آزار و اذیت، نظارت و ارعاب مخالفان در خارج از کشور، از جمله در اروپا.</p>

<p style="text-align: justify; direction: rtl;">این نه تنها یک موضوع حقوق بشری است، بلکه یک نگرانی امنیتی برای کشورهای اروپایی نیز می‌باشد. سپاه پاسداران و بازیگران مرتبط با آن با تهدیداتی علیه فعالان و روزنامه‌نگاران در اروپا مرتبط بوده‌اند و دولت‌های اروپایی به طور فزاینده‌ای عملیات‌های خارجی تهران را به عنوان بخشی از یک چالش امنیتی گسترده‌تر تلقی می‌کنند.</p>

<p style="text-align: justify; direction: rtl;">اگر قرار است تعیین اتحادیه اروپا تأثیرگذار باشد، مقامات اروپایی باید اطمینان حاصل کنند که فناوری اروپایی و کالاهای با کاربرد دوگانه به اکوسیستم فنی سپاه، چه به طور مستقیم و چه از طریق واسطه‌ها، نرسد.</p>

<p style="text-align: justify; direction: rtl;">دوم، اختلال مالی. پایداری سپاه به پول بستگی دارد و بخش بزرگی از قدرت اقتصادی آن از طریق کنسرسیوم‌ها، پیمانکاران و «شرکت‌های صوری» ساختاریافته است که می‌توانند سرمایه را جابجا کنند، کالاها را خریداری کنند و نفوذ ایجاد کنند.</p>

<p style="text-align: justify; direction: rtl;">تعیین سپاه، پایه قانونی قوی‌تری برای اقدام به اتحادیه اروپا می‌دهد. گام بعدی استفاده از آن است: نقشه‌برداری از ساختارهای شرکتی مرتبط با سپاه، شناسایی تسهیل‌کنندگان و پیگیری مسدود کردن دارایی‌ها و اعمال محدودیت‌ها به روش‌هایی که دور زدن آن‌ها دشوار باشد.</p>

<p style="text-align: justify; direction: rtl;">اروپا دیگر در عصر «صبر استراتژیک» نیست. ماه‌های آینده نشان خواهد داد که آیا موقعیت جدید اتحادیه اروپا به یک سیاست عمل‌گرا تبدیل می‌شود یا تصمیمی که تا حد زیادی در حد بیانیه باقی می‌ماند.</p>
"""

# کادر بیوگرافی با عکس - دقیقا مشابه عکس ارسالی کاربر (عکس در سمت چپ، متن در سمت راست)
AUTHOR_BIO_FA_HTML = """
<div style="background-color: #ffffff; padding: 20px; border-top: 2px solid #2c3e50; border-bottom: 1px solid #eee; margin-top: 40px; font-family: 'Tahoma', sans-serif; display: flex; flex-direction: row; gap: 20px; align-items: flex-start;">
    <div style="flex-shrink: 0; width: 130px;">
        <img src="https://eutoday.net/wp-content/uploads/2026/02/cropped-OB_Hossein_Amjadi_Portrait-x.jpg" alt="Hossein Amjadi" style="width: 100%; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    </div>
    <div style="flex-grow: 1; direction: rtl;">
        <h3 style="margin: 0 0 10px 0; color: #111; font-size: 1.2em; font-weight: bold; text-align: right; text-transform: uppercase;">HOSSEIN AMJADI</h3>
        <p style="margin: 0; color: #444; line-height: 1.8; text-align: justify; font-size: 0.95em;">
            حسین امجدی، فعال حقوق بشر ایرانی ساکن اوبرهاوزن آلمان و عضو انجمن <strong>VVMIran e.V.</strong> (انجمن دفاع از حقوق بشر در ایران) است. 
            او پس از آنچه «تهدید جدی جانی» توصیف می‌کند، مجبور به ترک ایران شد. نوشته‌های او بر سرکوب دولتی، هدف قرار دادن بازداشت‌شدگان و معترضان، و وضعیت زنان در ایران تمرکز دارد. 
            امجدی همچنین مهندس نرم‌افزار با تجربه در زیرساخت‌های حیاتی است و پژوهش‌های او بر شناسایی شبکه‌های فنی و مالی که امکان سرکوب فراملی را فراهم می‌کنند، متمرکز می‌باشد.
        </p>
    </div>
</div>
"""

# لینک منبع
SOURCE_HTML = f"""
<div style="margin-top: 20px; font-family: 'Tahoma', sans-serif; direction: rtl; font-size: 0.9em; color: #555; background-color: #fdfdfd; padding: 10px; border-radius: 4px;">
    <strong>منبع:</strong> <a href="{TARGET_URL}" target="_blank" style="color: #2c3e50; text-decoration: underline;">EU Today</a>
</div>
"""

def update_existing_post():
    POST_ID = "6198609712920970196" # شناسه پست فعلی
    print(f"� در حال آپدیت پست {POST_ID} با افکت سینمایی جدید...")
    try:
        poster = BloggerPoster()
        if not poster.service: return
        
        # ترکیب محتوا شامل عکس شاخص متحرک، متن، بیوگرافی و منبع
        final_content = FEATURED_IMG_HTML + FA_BODY + AUTHOR_BIO_FA_HTML + SOURCE_HTML
        
        body = {
            "id": POST_ID,
            "kind": "blogger#post",
            "blog": {"id": os.getenv("BLOG_ID")},
            "title": FA_TITLE,
            "content": final_content,
            "labels": ["گزارش ویژه", "بین‌الملل", "حسین امجدی", "سپاه پاسداران"]
        }
        
        # استفاده از متد update به جای insert
        result = poster.service.posts().update(
            blogId=os.getenv("BLOG_ID"),
            postId=POST_ID,
            body=body
        ).execute()
        
        print(f"✅ پست با موفقیت آپدیت شد: {result.get('url')}")
        
    except Exception as e:
        print(f"❌ خطا در آپدیت: {e}")

if __name__ == "__main__":
    update_existing_post()
