"""Fix the last 2 posts with long duplicated content"""
import sys, pickle, os, re, time
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from googleapiclient.discovery import build
load_dotenv()
BLOG_ID = os.getenv("BLOG_ID", "1276802394255833723")
with open("token_auth_fixed.pickle", "rb") as f:
    creds = pickle.load(f)
service = build("blogger", "v3", credentials=creds)

post_ids = ["872555773162872336", "4045108482536399704"]

for pid in post_ids:
    post = service.posts().get(blogId=BLOG_ID, postId=pid).execute()
    content = post['content']
    
    # The pattern: Line 7 has the entire text as one blob, 
    # then line 8 has <!--more-->, then lines 10+ repeat the same text with line breaks.
    # We need to KEEP the formatted version (lines 10+) and REMOVE the blob (line 7).
    
    # Find the Persian div
    pattern = r'(<div style="font-size:17px;line-height:2\.2;color:#fff;text-align:justify;direction:rtl;font-family:\'Vazir\',sans-serif;">\s*)(.*?)(\s*</div>)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"⚠️ No match: {post['title'][:50]}")
        continue
    
    inner = match.group(2)
    
    # Get pure text (no HTML tags) to find first 100 chars
    pure = re.sub(r'<[^>]+>', '', inner).strip()
    pure = re.sub(r'\s+', ' ', pure)
    first_100 = pure[:100]
    
    # Find second occurrence in inner text
    # The blob is first, then <!--more-->, then formatted text repeat
    # Find the <!--more--> tag position
    more_pos = inner.find("<a name='more'></a>")
    if more_pos < 0:
        more_pos = inner.find("<!--more-->")
    
    if more_pos > 0:
        # Everything before <!--more--> is the blob, after is formatted + repeated
        before_more = inner[:more_pos].strip()
        after_more = inner[more_pos:].strip()
        
        # The after_more contains the <!--more--> tag plus the repeated text
        # Remove the first blob, keep <!--more--> + formatted text
        # But we also need to add <!--more--> after first paragraph of the formatted text
        
        # Get the formatted text (after <!--more--> tag)
        more_tag = "<a name='more'></a>" if "<a name='more'></a>" in after_more else "<!--more-->"
        formatted = after_more.replace(more_tag, "", 1).strip()
        
        # Add <!--more--> after first paragraph
        lines = formatted.split('\n')
        new_lines = []
        added_more = False
        for line in lines:
            new_lines.append(line)
            if not added_more and line.strip() and len(line.strip()) > 50:
                new_lines.append(more_tag)
                added_more = True
        
        new_inner = '\n'.join(new_lines)
        new_content = content[:match.start(2)] + '\n                    ' + new_inner + '\n                ' + content[match.end(2):]
        
        try:
            service.posts().patch(
                blogId=BLOG_ID, postId=pid,
                body={"content": new_content}
            ).execute()
            print(f"✅ Fixed: {post['title'][:55]}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"⚠️ No <!--more--> found: {post['title'][:50]}")
