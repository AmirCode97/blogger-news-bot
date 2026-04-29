import os

def delete_cache(filename):
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"✅ فایل {filename} پاک شد.")
        else:
            print(f"✅ فایل {filename} از قبل پاک شده بود.")
    except Exception as e:
        print(f"❌ خطا در پاک کردن {filename}: {e}")

delete_cache("duplicate_cache.json")
delete_cache("news_cache.json")
print("✅ حافظه ربات (کش) به طور کامل پاک شد.")
