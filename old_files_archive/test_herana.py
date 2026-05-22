import sys
import config
from main import BloggerNewsBot

# Overwrite config sources to ONLY include Herana
for source in config.NEWS_SOURCES:
    if "هرانا" in source["name"]:
        source["enabled"] = True
    else:
        source["enabled"] = False

print("Starting test for Herana ONLY...")
bot = BloggerNewsBot()
bot.run_once()
print("Test complete!")
