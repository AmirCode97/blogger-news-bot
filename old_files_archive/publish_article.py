"""
اسکریپت انتشار مقاله دستی در وبلاگ با تصویر اصلی و پروفایل نویسنده
"""
import base64
import sys
import os

# اضافه کردن مسیر پروژه به پایتون
sys.path.append(r"C:\Users\amirs\.gemini\antigravity\scratch\blogger-news-bot")

try:
    from blogger_poster import BloggerPoster
except ImportError:
    print("❌ خطا: ابتدا وارد پوشه C:\\Users\\amirs\\.gemini\\antigravity\\scratch\\blogger-news-bot شوید!")
    sys.exit(1)

# ==================== تنظیمات مقاله ====================
TITLE = "جنگی که از آسمان شروع شد، اما بر دوش مردم افتاد"

ARTICLE_TEXT = """من این جنگ را فقط یک درگیری نظامی میان ایران، اسرائیل و آمریکا نمی‌بینم. تا اواخر مارس ۲۰۲۶، این بحران از مرحله حملات محدود عبور کرده و به یک رویارویی فرسایشی با پیامدهای انسانی، اقتصادی و امنیتی گسترده تبدیل شده است.

برای فهمیدن ریشه این فاجعه نباید فقط به موشک‌ها، پایگاه‌ها و حملات متقابل نگاه کرد. مسئله اصلی، ساختاری است که سال‌ها بقای خود را در بحران‌سازی، دشمن‌تراشی و نظامی کردن سیاست داخلی و خارجی جست‌وجو کرده است.

وقتی یک حکومت، به جای ساختن کشور، انرژی خود را صرف گسترش تنش، تولید نفرت و تبدیل کردن تقابل به ابزار بقا می‌کند، نتیجه دیر یا زود همین می‌شود — جنگ از مرزها عبور می‌کند و وارد زندگی روزمره مردم می‌شود.

ریشه بخش بزرگی از این وضعیت در ماهیت جمهوری اسلامی است؛ در نوعی ایدئولوژی حکومتی که به جای عقلانیت سیاسی، بر تقابل دائمی، خشونت سازمان‌یافته و نگاه مأموریتی به منطقه تکیه دارد. من عامدانه از حکومت حرف می‌زنم، نه از مردم ایران و نه از باور دینی افراد. نقد من متوجه سیستمی است که سال‌ها کشور را از مسیر توسعه، رفاه و ثبات دور کرد و آن را به میدان پروژه‌های پرهزینه امنیتی و منطقه‌ای کشاند.

امروز تاوان این سیاست را مردم عادی می‌دهند. نهادهای بین‌المللی از افزایش تلفات غیرنظامیان و آسیب به زیرساخت‌های غیرنظامی در جریان این جنگ خبر داده‌اند، و همین نشان می‌دهد که در هر درگیری طولانی، نخستین قربانیان نه تصمیم‌گیران، بلکه شهروندان بی‌دفاع هستند.

خانواده‌ای که خانه‌اش را از دست می‌دهد، کودکی که مدرسه‌اش ناامن می‌شود، بیماری که در میانه اختلال خدمات درمانی گرفتار می‌ماند، هیچ سهمی در محاسبات سیاسی و نظامی حاکمان نداشته، اما سنگین‌ترین هزینه را او می‌پردازد.

این واقعیت فقط به داخل ایران محدود نمی‌ماند. گزارش‌ها نشان می‌دهد که در اسرائیل نیز مدارس تعطیل شده، محدودیت‌های امنیتی گسترش یافته و زندگی روزمره مردم تحت تأثیر حملات و تهدیدهای متقابل قرار گرفته است.

همین نکته برای من مهم است: جنگ، هرچند با زبان دولت‌ها آغاز می‌شود، در نهایت با اضطراب مردم عادی ادامه پیدا می‌کند. کسانی که پشت میزهای قدرت تصمیم می‌گیرند، معمولاً آخرین کسانی هستند که طعم واقعی ناامنی را می‌چشند.

ادامه این بحران، فقط شهرها را ناامن نمی‌کند؛ اقتصاد را هم از درون می‌فرساید. این جنگ به بازارهای جهانی شوک وارد کرده، نگرانی درباره تنگه هرمز را بالا برده و فشار بر قیمت انرژی و تجارت را افزایش داده است. این یعنی اثر جنگ فقط در صدای انفجار خلاصه نمی‌شود؛ جنگ در قیمت کالا، در هزینه حمل‌ونقل، در آینده شغلی مردم و در کوچک‌تر شدن سفره خانواده‌ها هم خودش را نشان می‌دهد.

به همین دلیل من معتقدم آدرس درست این بحران را باید با صراحت نشان داد. اگر کشوری دهه‌ها با سیاست صدور تنش، شعارهای افراطی و ترجیح میدان بر زندگی مردم اداره شود، نتیجه‌اش نه عزت ملی است و نه امنیت پایدار؛ نتیجه‌اش انزوای بیشتر، آسیب‌پذیری بیشتر و باز شدن راه جنگ به داخل خانه‌های مردم است.

این همان نقطه‌ای است که جمهوری اسلامی باید بابت آن پاسخ‌گو شناخته شود — نه فقط به خاطر تصمیم‌های امروز، بلکه به خاطر بنیانی که سال‌ها بر دشمنی، بحران و ترس بنا کرد.

اندوه از اینکه باز هم مردم باید هزینه ایدئولوژی و ماجراجویی را بدهند، و مسئولیت برای اینکه واقعیت را پنهان نکنیم.

تا وقتی ریشه بحران را فقط در آخرین حمله و آخرین پاسخ نظامی جست‌وجو کنیم، مسئله را ناقص دیده‌ایم. ریشه عمیق‌تر است: در حکومتی که بقا را در تنش می‌بیند و در ذهنیتی که جان انسان را پس از ایدئولوژی قرار می‌دهد.

اگر قرار باشد از دل این ویرانی یک درس روشن بیرون بیاید، آن درس برای ما این است: هیچ کشوری با سیاست بحران دائمی به امنیت نمی‌رسد. حکومتی که از ترس، دشمن و التهاب تغذیه می‌کند، سرانجام همان ترس و ویرانی را به جامعه خودش برمی‌گرداند.

و امروز، آنچه بیش از همه زیر آوار این جنگ مانده، نه فقط ساختمان‌ها و زیرساخت‌ها، بلکه زندگی مردمی است که سال‌هاست هزینه تصمیم‌هایی را می‌دهند که هرگز در آن سهمی نداشته‌اند."""

LABELS = ["مقاله", "بین‌الملل"]

# مسیر مستقیم عکس‌هایی که همین الان آپلود کردید
# عکس اول: تصویر اصلی خبر (خرابه‌ها و مردم)
MAIN_IMAGE_PATH = r"C:\Users\amirs\.gemini\antigravity\brain\fba99f12-72d1-4b24-bf7e-84200abd026d\.tempmediaStorage\media_fba99f12-72d1-4b24-bf7e-84200abd026d_1777922472624.png"

# عکس دوم: تصویر پروفایل نویسنده
AUTHOR_IMAGE_PATH = r"C:\Users\amirs\.gemini\antigravity\brain\fba99f12-72d1-4b24-bf7e-84200abd026d\.tempmediaStorage\media_fba99f12-72d1-4b24-bf7e-84200abd026d_1777922478367.png"


def image_to_base64_compressed(filepath, max_width=800, quality=70):
    try:
        import io
        from PIL import Image
        
        with Image.open(filepath) as img:
            # Convert to RGB (in case it's PNG with alpha)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
                
            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
            # Compress to JPEG
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except ImportError:
        print("❌ کتابخانه Pillow نصب نیست! لطفاً دستور زیر را اجرا کنید:")
        print("pip install Pillow")
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطا در پردازش عکس {filepath}: {e}")
        return None

def main():
    print("📝 آماده‌سازی مقاله برای انتشار...")
    
    # پردازش عکس اصلی
    main_img_b64 = image_to_base64_compressed(MAIN_IMAGE_PATH, max_width=850, quality=75)
    if main_img_b64:
        image_html = f'<div style="margin-bottom:30px;text-align:center;"><img src="data:image/jpeg;base64,{main_img_b64}" style="width:100%;max-width:850px;border-radius:14px;box-shadow:0 8px 30px rgba(0,0,0,0.5);"></div>'
        print("✅ عکس اصلی (بالای خبر) بهینه و بارگذاری شد.")
    else:
        image_html = ""
        print("⚠️ عکس اصلی پیدا نشد!")

    # پردازش عکس نویسنده
    author_img_b64 = image_to_base64_compressed(AUTHOR_IMAGE_PATH, max_width=200, quality=80)
    if author_img_b64:
        author_html = f"""
        <div style="background:linear-gradient(135deg, #161616, #242424); border-radius:14px; padding:20px; margin-top:50px; display:flex; align-items:center; direction:rtl; border-right:5px solid #c0392b; box-shadow:0 6px 25px rgba(0,0,0,0.4);">
            <img src="data:image/jpeg;base64,{author_img_b64}" style="width:90px; height:90px; border-radius:50%; object-fit:cover; margin-left:25px; border:3px solid #c0392b; box-shadow:0 4px 15px rgba(0,0,0,0.5);">
            <div>
                <h3 style="color:#fff; margin:0 0 10px 0; font-family:'Vazir',sans-serif; font-size:20px;">امیرسام</h3>
                <p style="color:#aaa; margin:0; font-size:15px; line-height:1.7; font-family:'Vazir',sans-serif;">نویسنده و تحلیل‌گر مسائل سیاسی و اجتماعی. علاقه‌مند به بررسی ریشه‌های بحران‌های خاورمیانه و تاثیر سیاست‌های کلان بر زندگی روزمره مردم.</p>
            </div>
        </div>
        """
        print("✅ عکس نویسنده (پایین خبر) بهینه و بارگذاری شد.")
    else:
        author_html = ""
        print("⚠️ عکس نویسنده پیدا نشد!")

    
    # تبدیل متن به پاراگراف‌های HTML
    paragraphs = [p.strip() for p in ARTICLE_TEXT.strip().split('\n\n') if p.strip()]
    formatted_paragraphs = ""
    for i, p in enumerate(paragraphs):
        if i == 0:
            formatted_paragraphs += f'<p style="font-size:19px;line-height:2.4;color:#e0e0e0;margin-bottom:22px;border-right:4px solid #c0392b;padding-right:18px;">{p}</p>\n'
        else:
            formatted_paragraphs += f'<p style="font-size:17px;line-height:2.3;color:#ddd;margin-bottom:18px;">{p}</p>\n'
    
    # ساخت HTML نهایی
    html_content = f"""
    <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
    {image_html}
    
    <!-- Article Content -->
    <div style="direction:rtl;text-align:justify;font-family:'Vazir',sans-serif;padding:10px 5px;">
        {formatted_paragraphs}
    </div>
    
    <!-- Author Box -->
    {author_html}
    """
    
    print("📡 اتصال به وبلاگ...")
    blogger = BloggerPoster()
    print("✅ اتصال برقرار شد.")
    
    print("🚀 در حال انتشار مقاله...")
    result = blogger.create_post(
        title=TITLE,
        content=html_content,
        labels=LABELS,
        is_draft=False
    )
    
    if result:
        print(f"✅ مقاله با موفقیت منتشر شد!")
        print(f"🔗 لینک: {result.get('url', 'N/A')}")
    else:
        print("❌ خطا در انتشار مقاله")

if __name__ == "__main__":
    main()
