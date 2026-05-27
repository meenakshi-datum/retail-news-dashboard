import feedparser
from datetime import datetime

feeds = [
    "https://retail.economictimes.indiatimes.com/rss/topstories",
    "https://www.livemint.com/rss/companies",
    "https://www.business-standard.com/rss/latest.rss"
]

def get_category(title):
    title = title.lower()

    if "blinkit" in title or "zepto" in title or "swiggy" in title:
        return "Quick Commerce"
    elif "amazon" in title or "flipkart" in title:
        return "Ecommerce"
    elif "fmcg" in title or "hindustan unilever" in title:
        return "FMCG"
    elif "funding" in title or "acquire" in title or "merger" in title:
        return "Funding / M&A"
    else:
        return "Retail"

news_cards = ""

for url in feeds:
    feed = feedparser.parse(url)

    for entry in feed.entries[:8]:

        category = get_category(entry.title)

        news_cards += f"""
        <div class="card">
            <small style="color:#60a5fa;">{category}</small>
            <h3>{entry.title}</h3>
            <p>{entry.summary[:180]}...</p>
            <a href="{entry.link}" target="_blank">Read more</a>
        </div>
        """

last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")

html = f"""
<html>
<head>
<title>Retail Intelligence Dashboard</title>

<style>
body {{
    font-family: Arial;
    background: #0f172a;
    color: white;
    margin: 0;
    padding: 20px;
}}

.header {{
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 5px;
}}

.sub {{
    color: #94a3b8;
    margin-bottom: 20px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 15px;
}}

.card {{
    background: #1e293b;
    padding: 15px;
    border-radius: 12px;
    transition: 0.2s;
}}

.card:hover {{
    transform: scale(1.02);
}}

a {{
    color: #60a5fa;
    text-decoration: none;
}}
</style>
</head>

<body>

<div class="header">Retail Intelligence Dashboard</div>
<div class="sub">Auto-generated daily insights</div>
<div class="sub">Last updated: {last_updated}</div>

<div class="grid">
{news_cards}
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
