"""
Advanced Duplicate Detection System for Blogger News Bot
سیستم پیشرفته جلوگیری از تکرار خبر

Features:
1. Title similarity check (fuzzy matching)
2. URL normalization and comparison
3. Content fingerprinting
4. Persistent database storage
5. Check against existing blog posts
6. Time-based duplicate window
"""

import os
import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Set, Dict, List, Optional
from difflib import SequenceMatcher

class DuplicateDetector:
    def __init__(self, cache_file: str = "duplicate_cache.json"):
        self.cache_file = cache_file
        self.title_hashes: Set[str] = set()
        self.url_hashes: Set[str] = set()
        self.content_hashes: Set[str] = set()
        self.full_titles: Set[str] = set()
        self.seen_urls: Set[str] = set()
        self.published_entries: List[Dict] = []  # Full history with timestamps
        self.similarity_threshold = 0.75  # 75% similarity = duplicate
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.title_hashes = set(data.get('title_hashes', []))
                    self.url_hashes = set(data.get('url_hashes', []))
                    self.content_hashes = set(data.get('content_hashes', []))
                    self.full_titles = set(data.get('full_titles', []))
                    self.seen_urls = set(data.get('seen_urls', []))
                    self.published_entries = data.get('published_entries', [])
            except Exception as e:
                print(f"[DuplicateDetector] Error loading cache: {e}")
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            data = {
                'title_hashes': list(self.title_hashes),
                'url_hashes': list(self.url_hashes),
                'content_hashes': list(self.content_hashes),
                'full_titles': list(self.full_titles)[-1000:],  # Keep last 1000
                'seen_urls': list(self.seen_urls)[-1000:],
                'published_entries': self.published_entries[-500:],  # Keep last 500
                'last_updated': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[DuplicateDetector] Error saving cache: {e}")
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        # Remove common prefixes/suffixes
        title = re.sub(r'^(خبر|گزارش|ویدیو|عکس|فوری)[:\s]+', '', title)
        # Remove punctuation and extra spaces
        title = re.sub(r'[^\w\s]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title.lower()
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        # Remove trailing slashes and query params
        url = re.sub(r'\?.*$', '', url)
        url = re.sub(r'#.*$', '', url)
        url = url.rstrip('/')
        # Remove www and protocol
        url = re.sub(r'^https?://(www\.)?', '', url)
        return url.lower()
    
    def _get_title_hash(self, title: str) -> str:
        """Get hash of normalized title"""
        normalized = self._normalize_title(title)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _get_url_hash(self, url: str) -> str:
        """Get hash of normalized URL"""
        normalized = self._normalize_url(url)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _get_content_hash(self, content: str) -> str:
        """Get hash of content fingerprint"""
        # Take first 500 chars, normalize
        snippet = content[:500] if content else ""
        snippet = re.sub(r'\s+', ' ', snippet).strip().lower()
        return hashlib.md5(snippet.encode()).hexdigest()
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles"""
        t1 = self._normalize_title(title1)
        t2 = self._normalize_title(title2)
        return SequenceMatcher(None, t1, t2).ratio()
    
    def is_duplicate(self, title: str, url: str, content: str = "") -> tuple:
        """
        Check if news item is duplicate
        Returns: (is_duplicate: bool, reason: str)
        """
        # 1. Check exact URL match
        url_hash = self._get_url_hash(url)
        if url_hash in self.url_hashes:
            return True, "URL already seen"
        
        if url in self.seen_urls or self._normalize_url(url) in [self._normalize_url(u) for u in self.seen_urls]:
            return True, "URL already published"
        
        # 2. Check exact title hash
        title_hash = self._get_title_hash(title)
        if title_hash in self.title_hashes:
            return True, "Exact title match"
        
        # 3. Check title in full titles set
        normalized_title = self._normalize_title(title)
        if normalized_title in [self._normalize_title(t) for t in self.full_titles]:
            return True, "Title already exists"
        
        # 4. Check title similarity (fuzzy matching)
        for existing_title in list(self.full_titles)[-200:]:  # Check last 200
            similarity = self._title_similarity(title, existing_title)
            if similarity >= self.similarity_threshold:
                return True, f"Similar title ({similarity:.0%}): {existing_title[:50]}..."
        
        # 5. Check content hash (if content provided)
        if content and len(content) > 100:
            content_hash = self._get_content_hash(content)
            if content_hash in self.content_hashes:
                return True, "Content fingerprint match"
        
        # 6. Check against recent entries (last 24 hours)
        now = datetime.now()
        for entry in self.published_entries[-100:]:
            try:
                entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                if now - entry_time > timedelta(hours=48):
                    continue  # Skip old entries
                
                # Check title similarity
                if self._title_similarity(title, entry.get('title', '')) >= 0.80:
                    return True, f"Recent similar: {entry.get('title', '')[:40]}..."
            except:
                pass
        
        return False, "OK - New content"
    
    def mark_as_published(self, title: str, url: str, content: str = "", post_id: str = ""):
        """Mark item as published"""
        # Add to all indexes
        self.title_hashes.add(self._get_title_hash(title))
        self.url_hashes.add(self._get_url_hash(url))
        self.full_titles.add(title)
        self.seen_urls.add(url)
        
        if content and len(content) > 100:
            self.content_hashes.add(self._get_content_hash(content))
        
        # Add to published entries with timestamp
        self.published_entries.append({
            'title': title,
            'url': url,
            'post_id': post_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # Save to disk
        self._save_cache()
    
    def get_stats(self) -> Dict:
        """Get duplicate detector statistics"""
        return {
            'total_titles': len(self.full_titles),
            'total_urls': len(self.seen_urls),
            'total_entries': len(self.published_entries),
            'title_hashes': len(self.title_hashes),
            'content_hashes': len(self.content_hashes)
        }
    
    def cleanup_old_entries(self, days: int = 30):
        """Remove entries older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        self.published_entries = [
            e for e in self.published_entries
            if datetime.fromisoformat(e.get('timestamp', datetime.now().isoformat())) > cutoff
        ]
        self._save_cache()


# Test
if __name__ == "__main__":
    detector = DuplicateDetector()
    
    # Test cases
    tests = [
        ("اعدام ۱۴ زندانی در ایران", "https://example.com/news1"),
        ("اعدام ۱۴ زندانی در ایران", "https://example.com/news2"),  # Duplicate title
        ("اعدام ۱۵ زندانی در ایران امروز", "https://example.com/news3"),  # Similar
        ("خبر کاملا متفاوت درباره اقتصاد", "https://example.com/news4"),  # Different
    ]
    
    print("Testing Duplicate Detector:")
    for title, url in tests:
        is_dup, reason = detector.is_duplicate(title, url)
        print(f"\n  Title: {title[:40]}...")
        print(f"  Is Duplicate: {is_dup}")
        print(f"  Reason: {reason}")
        
        if not is_dup:
            detector.mark_as_published(title, url)
    
    print(f"\nStats: {detector.get_stats()}")
