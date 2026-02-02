import re

# نمونه واقعی از سایت (از تست قبلی)
sample_text = r'"className\":\"CustomPortableTextComponents-module-scss-module__MwAzyW__paragraph\",\"children\":[\"او ۱۳ بهمن گفت: «برای ازسرگیری گفت‌وگوها نباید پیش‌شرطی وجود داشته باشد.\"]'

# تست Regex
pattern = r'\\"children\\":\[\\"([^\\"]{10,})\\"]'
matches = re.findall(pattern, sample_text)

print(f"Original text: {sample_text[:100]}...")
print(f"Matches found: {len(matches)}")
for m in matches:
    print(f"Match: {m}")

# تست روی فایل بزرگ debug_page.html
try:
    with open('debug_page.html', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"\nScanning debug_page.html ({len(content)} chars)...")
        
        matches = re.findall(pattern, content)
        print(f"Found {len(matches)} matches in file")
        for i, m in enumerate(matches[:5]):
            print(f"{i}: {m[:100]}...")
except:
    pass
