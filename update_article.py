import os
from blogger_poster import BloggerPoster

def update_the_article():
    # Initialize Poster
    poster = BloggerPoster()
    
    # 1. Profile image URL (hosted externally to avoid large base64 in post)
    prof_img_url = "https://iili.io/qlSL0X4.jpg"

    # 2. Add proper line breaks to the article for HTML
    article_img_url = "https://iili.io/qledfMx.png"
    paragraphs = [
        "این روزها که صدای انفجارها لرزه بر تنِ پایگاه‌های سپاه و مراکز سرکوب می‌اندازد، خیلی‌ها از «جنگ» می‌گویند. اما بیایید با خودمان صادق باشیم؛ این جنگی نیست که امروز شروع شده باشد. جنگِ واقعی ٤٧ سال پیش شروع شد؛ همان روزی که ایران به اشغالِ یک تفکر ویرانگر درآمد. آنچه امروز در آسمان ایران می‌بینیم، نه یک تهدید خارجی، بلکه نتیجه‌ی حتمی و منطقیِ دهه‌ها باجخواهی، تروریسم و گروگان‌گیریِ یک رژیمِ ضدایرانی است.",
        "اگر امروز موشک‌ها مخازن سوخت و مراکز نظامی را نشانه گرفته‌اند، مقصر نه واشینگتن است و نه تل‌آویو. مقصر اصلی همان‌هایی هستند که نانِ سفره‌ی ما را بریدند تا به گروه‌های نیابتی‌شان در منطقه موشک و پهپاد برسانند. جمهوری اسلامی سال‌هاست که ایران را به سنگری برای نقشه‌های ایدئولوژیک خودش تبدیل کرده و مردم ایران را به عنوان «سپر انسانی» گروگان گرفته است. این رژیم آخوندی بود که با شعارهای توخالی و دشمن‌تراشی‌های بی‌پایان، کشور ما را به لبه‌ی این پرتگاه کشاند.",
        "واقعیت این است که اسرائیل و آمریکا امروز در حال انجام کاری هستند که این رژیم هرگز اجازه نداد خودِ مردم در خیابان‌ها به سرانجام برسانند. ضربات دقیقی که به پیکره‌ی نظامی و امنیتی جمهوری اسلامی وارد می‌شود، در واقع هدف قرار دادنِ «ماشین سرکوب» است. هر پایگاهی که منهدم می‌شود، در واقع غل و زنجیری است که از دست و پای ملت ایران باز می‌شود.",
        "برخلاف تبلیغات رژیم که سعی می‌کند خودش را با «ایران» یکی نشان دهد، ما می‌دانیم که پیروزی این ائتلاف بر رژیم، به معنای شکستِ ایران نیست؛ بلکه به معنای بازگشتِ ایران به آغوشِ تمدن و صلح است. حمایت بین‌المللی از خواستِ مردم برای سرنگونی این اختاپوس، تنها راهی است که می‌تواند ما را از شر این «اشغالگرانِ داخلی» خلاص کند.",
        "رژیم آخوندی سال‌ها با ایجاد رعب و وحشت و اعدام و زندان، بقای خودش را تضمین کرد. اما حالا که ستون‌های قدرتش زیر ضربات سنگین ائتلافِ آزادی‌خواه سست شده، ما شاهدِ حقیقتِ ماجرا هستیم: این حکومت از درون پوک شده است.",
        "ما مردم ایران، نه خواهانِ تنش هستیم و نه به دنبال خونریزی؛ اما می‌دانیم که جراحیِ این تومور سرطانی، درد دارد. این جنگ، در واقع «عملیاتِ نجاتِ ایران» است. ما می‌خواهیم بعد از دهه‌ها، دوباره کشوری داشته باشیم که در آن پول ملی ارزش داشته باشد، پاسپورتش محترم باشد و جوانانش به جای سودای مهاجرت، به فکر ساختن وطنِ آزادشان باشند.",
        "سایه‌ی سیاه جمهوری اسلامی رو به زوال است. امروز بیش از هر زمان دیگری مشخص شده که متحدان واقعیِ مردم ایران، کسانی هستند که برای نابودیِ دشمنِ مشترک ما، یعنی این رژیمِ فاسد و تبهکار، وارد میدان شده‌اند. ما در آستانه‌ی یک تغییر بزرگ هستیم؛ تغییری که شاید با بوی باروت همراه باشد، اما نویدبخشِ طلوعی است که در آن دیگر خبری از گشت ارشاد، اعدام‌های سیاسی و غارتِ ثروت‌های ملی نخواهد بود."
    ]

    title = "پایانِ کابوس؛ وقتی آتش، راهِ رسیدن به آزادی میشود"

    content_html = "<div dir='rtl' style='text-align: right; font-family: tahoma, sans-serif; line-height: 2;'>\n"
    
    # 4. Insert the new generated article image at the top
    content_html += f"  <div style='margin-bottom: 30px; text-align: center;'>\n"
    content_html += f"    <img src='{article_img_url}' style='max-width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);' alt='Article Image'>\n"
    content_html += f"  </div>\n"

    for p in paragraphs:
        content_html += f"  <p style='font-size: 16px; margin-bottom: 20px; text-align: justify;'>{p}</p>\n"
    
    # Closing statement - bigger and bolder
    closing = "ایرانِ فردا، ایرانی است بدون جمهوری اسلامی. و این، ارزشِ هر هزینه‌ای را دارد."
    content_html += f"  <p style='font-size: 22px; font-weight: 900; margin-top: 30px; margin-bottom: 30px; text-align: center; color: #fff; line-height: 1.8; border-top: 1px solid #333; border-bottom: 1px solid #333; padding: 25px 0;'>{closing}</p>\n"
    
    # 5. Add Profile Image and Author info at the bottom
    content_html += f"""
    <div style='margin-top: 50px; border-top: 1px solid #333; padding-top: 25px; display: flex; align-items: center; gap: 20px;'>
      <img src='{prof_img_url}' style='width: 120px; height: 120px; object-fit: cover; border-radius: 50%; border: 3px solid #c0392b; flex-shrink: 0;' alt='Amirhossein Salehi Fashami'>
      <div style='text-align: right;'>
        <h3 style='margin: 0 0 8px 0; color: #c0392b; font-size: 22px; font-weight: bold;'>Amirhossein Salehi Fashami</h3>
        <h4 style='margin: 0; color: #95a5a6; font-size: 15px; font-weight: normal;'>فعال حقوق بشر و کارشناس سیاسی و منطقه</h4>
      </div>
    </div>
    """
    content_html += "</div>"

    print("Updating post by ID...")
    # Use known post ID directly
    post_id = "8013280011551779308"
    try:

        print(f"Updating post: {post_id}")
        post_body = {
            'id': post_id,
            'title': title,
            'content': content_html,
            'labels': ["مقاله"]
        }
        resp = poster.service.posts().update(
            blogId=poster.blog_id, postId=post_id, body=post_body
        ).execute()

        if resp:
            print(f"Article updated successfully: {resp.get('url')}")
        else:
            print("Failed to update.")

    except Exception as e:
        print(f"Error during update: {e}")

if __name__ == '__main__':
    update_the_article()
