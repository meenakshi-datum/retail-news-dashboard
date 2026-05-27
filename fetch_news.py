import feedparser
from datetime import datetime

feeds = [
    "https://retail.economictimes.indiatimes.com/rss/topstories",
    "https://www.moneycontrol.com/rss/business.xml"
]

news = []

for url in feeds:
    feed = feedparser.parse(url)

    for entry in feed.entries[:10]:
        news.append(f"""
TITLE: {entry.title}
LINK: {entry.link}
SUMMARY: {entry.summary}
DATE: {datetime.now().strftime('%d-%m-%Y')}
--------------------------
""")

with open("daily_news.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(news))
