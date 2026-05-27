import feedparser
from datetime import datetime

feeds = [
    "https://retail.economictimes.indiatimes.com/rss/topstories",
    "https://www.livemint.com/rss/companies",
    "https://www.business-standard.com/rss/latest.rss"
]

news_cards = ""

for url in feeds:
    feed = feedparser.parse(url)

    for entry in feed.entries[:8]:
        news_cards += f"""
        <div class="card">
            <h3>{entry.title}</h3>
            <p>{entry.summary[:200]}...</p>
            <a href="{entry.link}" target="_blank">Read more</a>
        </div>
        """

html = f"""
<html>
<head>
<title>Retail Intelligence Dashboard</title>
<style>
body {{
    font-family: Arial;
    background: #0f172a;
    color: white;
    padding: 30px;
}}

.card {{
    background: #1e293b;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 12px;
}}

a {{
    color: #60a5fa;
}}
</style>
</head>

<body>

<h1>Retail Intelligence Dashboard</h1>
<p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>

{news_cards}

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
