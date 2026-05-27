import feedparser
from datetime import datetime

# -----------------------------
# RSS SOURCES (8 STRONG FEEDS)
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
# STEP 1: COLLECT ALL NEWS
# -----------------------------
all_news = []

for url in feeds:
    feed = feedparser.parse(url)

    for entry in feed.entries[:8]:

        all_news.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary if hasattr(entry, "summary") else ""
        })

# -----------------------------
# STEP 2: REMOVE DUPLICATES
# -----------------------------
seen = set()
unique_news = []

for n in all_news:
    if n["title"] not in seen:
        unique_news.append(n)
        seen.add(n["title"])

# -----------------------------
# STEP 3: BUILD NEWS CARDS
# -----------------------------
news_cards = ""

for n in unique_news:

    category = get_category(n["title"])
    summary = n["summary"]
    summary = summary.replace("<p>", "").replace("</p>", "")
    summary = summary[:180]

    news_cards += f"""
    <div class="card">
        <div class="tag">{category}</div>
        <h3>{n["title"]}</h3>
        <p>{summary}...</p>
        <a href="{n["link"]}" target="_blank">Read more →</a>
    </div>
    """

# -----------------------------
# STEP 4: LAST UPDATED TIME
# -----------------------------
last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")

# -----------------------------
# STEP 5: FINAL HTML DASHBOARD
# -----------------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Retail Intelligence Dashboard</title>

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
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 18px;
    align-items: stretch;
}}

.card {{
    background: #111c33;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #1f2a44;
    transition: 0.2s;
}}

.card:hover {{
    transform: translateY(-4px);
}}

.tag {{
    font-size: 12px;
    color: #60a5fa;
    margin-bottom: 8px;
    display: inline-block;
}}

h3 {{
    font-size: 16px;
    margin: 8px 0;
}}

p {{
    font-size: 13px;
    color: #cbd5e1;
}}

a {{
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
<div class="sub">Auto-generated retail & ecommerce insights</div>
<div class="sub">Last updated: {last_updated}</div>

<div class="grid">
{news_cards}
</div>

</body>
</html>
"""

# -----------------------------
# STEP 6: WRITE FILE
# -----------------------------
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
