import inspect
from news_fetcher import NewsFetcher

print(f"File: {NewsFetcher.__module__}")
sig = inspect.signature(NewsFetcher.mark_as_seen)
print(f"Signature: {sig}")
