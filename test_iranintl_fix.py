"""
Quick test to verify Iran International content cleaning works.
Tests the _clean_iranintl_content regex patterns.
"""
import re

# Simulate the cleanup function
def clean_iranintl_content(text):
    if not text:
        return text
    
    junk_patterns = [
        r'پخش\s*نسخه\s*شنیداری',
        r'اشتراک[‌\u200c]?گذاری',
        r'[۰-۹\d]+\s*دقیقه\s*پیش',
        r'[۰-۹\d]+\s*ساعت\s*پیش',
        r'[۰-۹\d]+\s*روز\s*پیش',
        r'لحظاتی\s*پیش',
        r'►\s*پخش',
        r'▶\s*پخش',
        r'نسخه\s*شنیداری',
        r'بازپخش',
        r'ذخیره\s*کردن',
        r'نشان‌گذاری',
        r'کپی\s*لینک',
        r'رونوشت\s*لینک',
    ]
    
    cleaned = text
    for pattern in junk_patterns:
        cleaned = re.sub(pattern, '', cleaned)
    
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = cleaned.strip()
    return cleaned


# Test cases
test_cases = [
    # Case 1: Content with audio player junk
    "۲۴ دقیقه پیش پخش نسخه شنیداری اشتراکگذاری\nحسین شریعتمداری مدیرمسئول روزنامه کیهان در مقاله‌ای خطاب به مردم آمریکا نوشت.",
    # Case 2: Content with Persian numeral timestamps
    "۳ ساعت پیش پخش نسخه شنیداری\nمتن اصلی خبر اینجاست.",
    # Case 3: Clean content (should not change)
    "این یک خبر عادی است که هیچ متن اضافی ندارد.\n\nپاراگراف دوم خبر.",
    # Case 4: Mixed junk at different positions
    "متن اول خبر.\n۱۲ دقیقه پیش\nمتن دوم خبر.\nاشتراک‌گذاری\nمتن سوم خبر.",
]

for i, test in enumerate(test_cases, 1):
    result = clean_iranintl_content(test)
    print(f"\n{'='*60}")
    print(f"Test {i}:")
    print(f"  INPUT:  {test[:80]}...")
    print(f"  OUTPUT: {result[:80]}...")
    print(f"  Removed {len(test) - len(result)} chars")
