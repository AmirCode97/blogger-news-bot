"""
Post Hossein Amjadi Article from LokalKlick.eu
انتشار مقاله حسین امجدی از سایت آلمانی
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

# Article info from LokalKlick.eu
ARTICLE_URL = "https://lokalklick.eu/2026/01/26/klarklick-getoetete-inhaftierte-und-die-frauen-im-iran-wenn-schweigen-zur-mittaeterschaft-wird/"
AUTHOR_IMAGE = "https://lokalklick.eu/wp-content/uploads/2026/01/Hossein-Amjadi.jpg"

# Full article content
TITLE_DE = "Getötete, Inhaftierte und die Frauen im Iran – Wenn Schweigen zur Mittäterschaft wird"
TITLE_FA = "کشته‌شدگان، زندانیان و زنان در ایران - وقتی سکوت به همدستی تبدیل می‌شود"

CONTENT_DE = """
<p><strong>Oberhausen/Rhein-Ruhr.</strong> In den vergangenen Wochen und Monaten haben sich die Straßen des Iran erneut in Orte verwandelt, die das Gewissen jedes freien Menschen erschüttern. Menschen gehen unbewaffnet auf die Straße, mit zitternden Stimmen, aber mit einem klaren Wunsch: Würde, Freiheit und eine lebenswerte Zukunft. Die Antwort darauf ist vielerorts brutale Gewalt. Namen, die nie wieder nach Hause zurückkehren werden. Gesichter, die hinter Gefängnismauern im Schweigen verschwinden.</p>

<p>Die Getöteten der jüngsten Proteste sind keine bloßen Zahlen oder Statistiken. Es waren Töchter und Söhne, Schwestern und Brüder, Eltern – Menschen mit einem ganz normalen Leben. Ihr einziges „Vergehen" war es, grundlegende Rechte einzufordern: das Recht auf Leben, auf friedlichen Protest und darauf, gehört zu werden. Der Einsatz tödlicher Gewalt gegen unbewaffnete Demonstrierende stellt eine klare Verletzung des Rechts auf Leben dar – jenes Rechts, das bereits im ersten Artikel der Allgemeinen Erklärung der Menschenrechte garantiert wird.</p>

<p>Neben den Toten stehen Tausende Inhaftierte. Frauen und Männer, die ohne faire Verfahren, ohne wirksamen Zugang zu Rechtsbeistand und teils ohne Information ihrer Familien festgenommen wurden. Zahlreiche Berichte über Misshandlungen, psychischen Druck, Folter und erzwungene Geständnisse zeichnen ein erschreckendes Bild der Haftbedingungen. Für viele ist das Gefängnis kein Ort der Rechtsprechung, sondern ein Instrument, um Stimmen zum Schweigen zu bringen.</p>

<p>Im Zentrum dieser Repression stehen Frauen. Frauen, die nicht nur für politische oder soziale Rechte eintreten, sondern für das grundlegendste Recht überhaupt: die Selbstbestimmung über ihren eigenen Körper und ihr Leben. Sie werden auf den Straßen mit Gewalt konfrontiert, in Haft besonders unter Druck gesetzt und im Alltag systematisch diskriminiert. Der Protest der Frauen im Iran ist daher weit mehr als eine politische Forderung – er ist ein Ruf nach menschlicher Würde.</p>

<p>Ich schreibe diese Zeilen nicht aus einer parteipolitischen Perspektive, sondern aus einer menschlichen. Ich bin Menschenrechtsaktivist, lebe in Oberhausen und bin Mitglied der VVMIran e.V. – Vereinigung zur Verteidigung der Menschenrechte im Iran e.V. Nach jahrelangem Engagement für Freiheit und Menschenrechte im Iran war ich aufgrund einer ernsthaften Gefährdung meines Lebens gezwungen, mein Heimatland zu verlassen. Nicht, um zu schweigen, sondern um zu überleben und meine menschenrechtliche und humanitäre Unterstützung für meine Landsleute fortzusetzen.</p>

<p><strong>Die Opfer im Iran brauchen mehr als Mitgefühl. Sie brauchen Sichtbarkeit, Aufmerksamkeit und internationale Solidarität. In solchen Momenten ist Schweigen keine Neutralität. Schweigen ist Mittäterschaft.</strong></p>
"""

CONTENT_FA = """
<p>در هفته‌ها و ماه‌های گذشته، خیابان‌های ایران بار دیگر به مکان‌هایی تبدیل شده‌اند که وجدان هر انسان آزاده‌ای را به لرزه درمی‌آورند. مردم بدون سلاح به خیابان‌ها می‌آیند، با صداهای لرزان، اما با یک خواسته روشن: کرامت، آزادی و آینده‌ای قابل زندگی. پاسخ به این خواسته‌ها در بسیاری از نقاط، خشونت بی‌رحمانه است. نام‌هایی که دیگر هرگز به خانه بازنمی‌گردند. چهره‌هایی که پشت دیوارهای زندان در سکوت ناپدید می‌شوند.</p>

<p>کشته‌شدگان اعتراضات اخیر فقط اعداد یا آمار نیستند. آن‌ها دختران و پسران، خواهران و برادران، والدین بودند - انسان‌هایی با یک زندگی کاملاً عادی. تنها «جرم» آن‌ها این بود که حقوق اساسی را مطالبه کردند: حق زندگی، حق اعتراض مسالمت‌آمیز و حق شنیده شدن. استفاده از خشونت مرگبار علیه معترضان غیرمسلح، نقض آشکار حق حیات است - همان حقی که در ماده اول اعلامیه جهانی حقوق بشر تضمین شده است.</p>

<p>در کنار کشته‌شدگان، هزاران بازداشت‌شده وجود دارند. زنان و مردانی که بدون محاکمه عادلانه، بدون دسترسی مؤثر به وکیل و گاهی بدون اطلاع‌رسانی به خانواده‌هایشان دستگیر شده‌اند. گزارش‌های متعدد از بدرفتاری، فشار روانی، شکنجه و اعترافات اجباری، تصویری هولناک از شرایط بازداشت ترسیم می‌کنند. برای بسیاری، زندان نه مکان اجرای عدالت، بلکه ابزاری برای خاموش کردن صداها است.</p>

<p>در مرکز این سرکوب، زنان قرار دارند. زنانی که نه فقط برای حقوق سیاسی یا اجتماعی مبارزه می‌کنند، بلکه برای اساسی‌ترین حق: تعیین سرنوشت بدن و زندگی خودشان. آن‌ها در خیابان‌ها با خشونت مواجه می‌شوند، در بازداشت تحت فشار ویژه قرار می‌گیرند و در زندگی روزمره به طور سیستماتیک تبعیض می‌بینند. بنابراین اعتراض زنان در ایران بسیار فراتر از یک مطالبه سیاسی است - این فریادی برای کرامت انسانی است.</p>

<p><strong>قربانیان در ایران بیش از همدردی به چیزی نیاز دارند: دیده شدن، توجه و همبستگی بین‌المللی. در چنین لحظاتی، سکوت بی‌طرفی نیست. سکوت، همدستی است.</strong></p>
"""

def main():
    print("=" * 60)
    print("📰 POSTING HOSSEIN AMJADI ARTICLE FROM LOKALKLICK.EU")
    print("=" * 60)
    
    # Init Blogger API
    with open('token_auth_fixed.pickle', 'rb') as t:
        creds = pickle.load(t)
    service = build('blogger', 'v3', credentials=creds)
    
    # Build HTML content
    html_content = f"""
    <style>.post-featured-image, .post-thumbnail {{ display: none !important; }}</style>
    
    <!-- Author Box with Photo -->
    <div style="background:linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);border-radius:16px;padding:30px;margin-bottom:30px;border:1px solid #ce0000;box-shadow:0 10px 40px rgba(206,0,0,0.2);">
        <table style="width:100%;border-collapse:collapse;">
            <tr>
                <td style="width:140px;vertical-align:top;padding-left:20px;">
                    <img src="{AUTHOR_IMAGE}" style="width:120px;height:120px;border-radius:50%;border:4px solid #ce0000;object-fit:cover;box-shadow:0 5px 20px rgba(0,0,0,0.4);" alt="Hossein Amjadi">
                </td>
                <td style="vertical-align:top;text-align:right;direction:rtl;">
                    <h2 style="color:#fff;margin:0 0 10px 0;font-size:24px;font-weight:900;">حسین امجدی</h2>
                    <p style="color:#ce0000;margin:0 0 10px 0;font-size:14px;font-weight:bold;">Hossein Amjadi</p>
                    <p style="color:#aaa;margin:0;font-size:13px;line-height:1.8;">فعال حقوق بشر، ساکن اوبرهاوزن آلمان<br>عضو انجمن دفاع از حقوق بشر در ایران (VVMIran e.V.)</p>
                </td>
            </tr>
        </table>
    </div>
    
    <!-- Persian Content -->
    <div style="font-size:17px;line-height:2.2;color:#fff;text-align:justify;direction:rtl;font-family:'Vazir',sans-serif;margin-bottom:40px;">
        <h2 style="color:#ce0000;font-size:24px;margin-bottom:20px;border-right:5px solid #ce0000;padding-right:15px;">{TITLE_FA}</h2>
        {CONTENT_FA}
    </div>
    
    <!--more-->
    
    <!-- German Content -->
    <div style="margin-top:40px;padding-top:30px;border-top:2px dashed #333;direction:ltr;text-align:left;font-family:sans-serif;">
        <h3 style="color:#ce0000;margin-bottom:20px;font-size:20px;">🇩🇪 Original (Deutsch)</h3>
        <h4 style="color:#fff;font-size:18px;margin-bottom:15px;">{TITLE_DE}</h4>
        <div style="font-size:15px;line-height:1.9;color:#ddd;">
            {CONTENT_DE}
        </div>
        <p style="margin-top:20px;font-style:italic;color:#888;font-size:13px;">
            <strong>Ein KlarKlick von Hossein Amjadi</strong>, Menschenrechtsaktivist und Mitglied der VVMIran e.V. – Vereinigung zur Verteidigung der Menschenrechte im Iran e.V.
        </p>
    </div>
    
    <!-- Premium Source Box -->
    <div style="margin-top:40px;padding:25px;background:#fff;border-right:5px solid #ce0000;border-radius:8px;text-align:right;direction:rtl;box-shadow:0 5px 15px rgba(0,0,0,0.05);">
        <p style="margin:0;font-size:14px;color:#555;font-family:Tahoma,sans-serif;">
            <span style="margin-left:15px;">منبع اصلی مقاله:</span> 
            <a href="{ARTICLE_URL}" target="_blank" style="background:#ce0000;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:13px;box-shadow:0 4px 12px rgba(206,0,0,0.3);">مشاهده در LokalKlick.eu</a>
        </p>
    </div>
    """
    
    # Post title
    post_title = f"{TITLE_FA} | {TITLE_DE}"
    
    # Create post
    print(f"\n📝 Title: {post_title[:60]}...")
    print(f"🔗 Source: {ARTICLE_URL}")
    
    post_body = {
        'kind': 'blogger#post',
        'blog': {'id': BLOG_ID},
        'title': post_title,
        'content': html_content,
        'labels': ['خانه', 'گزارش ویژه', 'حقوق بشر', 'حسین امجدی', 'آلمان', 'Hossein Amjadi']
    }
    
    result = service.posts().insert(
        blogId=BLOG_ID,
        body=post_body,
        isDraft=False
    ).execute()
    
    print(f"\n✅ Published successfully!")
    print(f"🔗 URL: {result.get('url')}")

if __name__ == "__main__":
    main()
