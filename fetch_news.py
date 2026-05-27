import feedparser
from datetime import datetime

# -----------------------------
# 8 STRONG RSS SOURCES
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
# BUILD NEWS CARDS
# -----------------------------
news_cards = ""

for url in feeds:
    feed = feedparser.parse(url)

    for entry in feed.entries[:8]:

        category = get_category(entry.title)

        summary = entry.summary if hasattr(entry, "summary") else ""
        summary = summary[:180].replace("<p>", "").replace("</p>", "")

        news_cards += f"""
        <div class="card">
            <div class="tag">{category}</div>
            <h3>{entry.title}</h3>
            <p>{summary}...</p>
            <a href="{entry.link}" target="_blank">Read more →</a>
        </div>
        """

# -----------------------------
# LAST UPDATED TIME
# -----------------------------
last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")

# -----------------------------
# FINAL HTML DASHBOARD
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
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 5px;
}}

.sub {{
    color: #94a3b8;
    margin-bottom: 20px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px;
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
    display: inline-block;
    font-size: 12px;
    color: #60a5fa;
    margin-bottom: 8px;
}}

h3 {{
    font-size: 16px;
}}

a {{
    color: #60a5fa;
    text-decoration: none;
}}
</style>

</head>

<body>

<div class="header">Retail Intelligence Dashboard</div>
<div class="sub">Auto-generated daily retail & ecommerce insights</div>
<div class="sub">Last updated: {last_updated}</div>

<div class="grid">
{news_cards}
</div>

</body>
</html>
"""

# -----------------------------
# WRITE OUTPUT FILE
# -----------------------------
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
