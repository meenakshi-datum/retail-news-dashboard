import feedparser
from datetime import datetime
import re
import time
from collections import defaultdict

# -----------------------------
# RSS SOURCES
# -----------------------------
feeds = [
    "https://retail.economictimes.indiatimes.com/rss/topstories",
    "https://www.livemint.com/rss/companies",
    "https://www.business-standard.com/rss/latest.rss",
    "https://www.moneycontrol.com/rss/business.xml",
    "https://inc42.com/feed/",
    "https://entrackr.com/feed/",
    "https://www.retaildive.com/feeds/news/",
    "https://techcrunch.com/feed/"
]

# -----------------------------
# CATEGORY FUNCTION
# -----------------------------
def get_category(title):
    title = title.lower()

    if any(x in title for x in ["blinkit", "zepto", "swiggy", "quick commerce"]):
        return "Quick Commerce"

    elif any(x in title for x in ["amazon", "flipkart", "ecommerce", "e-commerce"]):
        return "Ecommerce"

    elif any(x in title for x in ["fmcg", "hindustan unilever", "nestle", "dabur"]):
        return "FMCG"

    elif any(x in title for x in ["startup", "funding", "raises", "acquire", "merger"]):
        return "Startups / Funding"

    elif any(x in title for x in ["retail", "store", "brand", "mall"]):
        return "Retail"

    else:
        return "Business / Tech"

# -----------------------------
# CLEAN DATE FUNCTION (IMPORTANT FIX)
# -----------------------------
def clean_date(date_str):
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")

    try:
        # RSS format: Wed, 27 May 2026 10:15:00 GMT
        return time.strftime("%Y-%m-%d", time.strptime(date_str[:25], "%a, %d %b %Y"))
    except:
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")

# -----------------------------
# COLLECT NEWS
# -----------------------------
all_news = []

for url in feeds:
    feed = feedparser.parse(url)

    for entry in feed.entries[:8]:

        summary = re.sub("<.*?>", "", entry.get("summary", ""))

        raw_date = entry.get("published") or entry.get("updated") or ""

        all_news.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary,
            "date": clean_date(raw_date)
        })

# -----------------------------
# REMOVE DUPLICATES
# -----------------------------
seen = set()
unique_news = []

for n in all_news:
    if n["title"] not in seen:
        unique_news.append(n)
        seen.add(n["title"])

# -----------------------------
# GROUP BY DATE
# -----------------------------
grouped_news = defaultdict(list)

for n in unique_news:
    grouped_news[n["date"]].append(n)

# -----------------------------
# BUILD HTML CARDS
# -----------------------------
news_cards = ""

for date in sorted(grouped_news.keys(), reverse=True):

    news_cards += f"""
    <h2 style="
        margin-top:30px;
        margin-bottom:10px;
        color:#ffffff;
        border-left:4px solid #60a5fa;
        padding-left:10px;
    ">
        {date}
    </h2>
    """

    for n in grouped_news[date]:

        category = get_category(n["title"])
        summary = n["summary"][:180]

        if not summary:
            summary = "No summary available."

        news_cards += f"""
        <div class="card">
            <div class="tag">{category}</div>
            <h3>{n["title"]}</h3>
            <p>{summary}</p>
            <a href="{n["link"]}" target="_blank">Read more →</a>
        </div>
        """

# -----------------------------
# LAST UPDATED
# -----------------------------
last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")

# -----------------------------
# FINAL HTML
# -----------------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Retail Intelligence Dashboard</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {{
    font-family: Arial;
    background: #0b1220;
    color: white;
    margin: 0;
    padding: 20px;
}}

.header {{
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 5px;
}}

.sub {{
    color: #94a3b8;
    margin-bottom: 10px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    align-items: start;
}}

.card {{
    background: #111c33;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #1f2a44;
    display: flex;
    flex-direction: column;
    min-height: 180px;
}}

.card:hover {{
    transform: translateY(-4px);
    transition: 0.2s;
}}

.tag {{
    font-size: 12px;
    color: #60a5fa;
    margin-bottom: 8px;
}}

h3 {{
    font-size: 15px;
    margin: 8px 0;
}}

p {{
    font-size: 13px;
    color: #cbd5e1;
    line-height: 1.4;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
}}

a {{
    margin-top: auto;
    color: #60a5fa;
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}
</style>

</head>

<body>

<div class="header">Retail Intelligence Dashboard</div>
<div class="sub">Date-wise structured retail & ecommerce feed</div>
<div class="sub">Last updated: {last_updated}</div>

<div class="grid">
{news_cards}
</div>

</body>
</html>
"""

# -----------------------------
# WRITE OUTPUT
# -----------------------------
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
