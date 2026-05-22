import os
import json
import re

search_titles = [
    "بحران هوای خوزستان: غبار سمی نفس مردم را بند آورد",
    "موج جدید پلمب واحدهای صنفی در کاشان: کشف حجاب عامل تعطیلی یک کافه",
    "مرگ در زندان؛ پرونده سیاه اعدام دو فعال سیاسی در ایران",
    "سازمان عفو بین‌الملل پرده از ابعاد هولناک اعدام‌ها در ایران برداشت: هشداری جدی برای جامعه جهانی",
    "پایان تلخ زندگی؛ اجرای حکم اعدام در سکوت خبری"
]

search_ids = [
    "4566076101771367375",
    "7937031076052603044",
    "8656571386204910865",
    "42661393950526048",
    "950771976670731036"
]

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".json") or file.endswith(".xml") or file.endswith(".txt") or file.endswith(".html"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Check for titles
                for t in search_titles:
                    # Let's clean title search to be fuzzy in case of spacing/paraphrasing
                    t_words = t.split()[:4]
                    t_pattern = ".*".join(t_words)
                    if re.search(t_pattern, content):
                        print(f"Match for title '{t[:20]}...' in file: {file_path}")
                
                # Check for IDs
                for pid in search_ids:
                    if pid in content:
                        print(f"Match for ID '{pid}' in file: {file_path}")
            except Exception as e:
                pass
