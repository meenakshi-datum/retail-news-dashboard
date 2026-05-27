import feedparser
from datetime import datetime, timezone, timedelta
import re
from collections import defaultdict

# =============================
# RSS SOURCES
# =============================
feeds = [
    "https://retail.economictimes.indiatimes.com/rss/topstories",
    "https://www.livemint.com/rss/companies",
    "https://www.business-standard.com/rss/latest.rss",
    "https://www.moneycontrol.com/rss/business.xml",
    "https://inc42.com/feed/",
    "https://entrackr.com/feed/"
]

# =============================
# CATEGORY ENGINE
# =============================
def get_category(title):
    t = title.lower()

    if any(x in t for x in ["blinkit", "zepto", "swiggy", "quick commerce"]):
        return "Quick Commerce"

    if any(x in t for x in ["amazon", "flipkart", "ecommerce"]):
        return "Ecommerce"

    if any(x in t for x in ["fmcg", "nestle", "dabur"]):
        return "FMCG"

    if any(x in t for x in ["startup", "funding", "acquire", "merge"]):
        return "Startups"

    return "Retail / Business"

# =============================
# TIME (IST)
# =============================
ist = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M IST")

# =============================
# CLEAN DATE
# =============================
def clean_date(date_str):
    try:
        return datetime.strptime(date_str[:16], "%a, %d %b %Y").strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

# =============================
# NORMALIZE TITLE
# =============================
def norm(t):
    return " ".join(t.lower().split())

# =============================
# FETCH NEWS
# =============================
news = []

for url in feeds:
    feed = feedparser.parse(url)

    for e in feed.entries[:20]:

        summary = re.sub("<.*?>", "", e.get("summary", ""))

        news.append({
            "title": e.title,
            "link": e.link,
            "summary": summary[:180],
            "date": clean_date(e.get("published", "")),
            "category": get_category(e.title)
        })

# =============================
# DEDUP
# =============================
seen = set()
unique = []

for n in news:
    key = norm(n["title"])
    if key not in seen:
        seen.add(key)
        unique.append(n)

# =============================
# GROUP BY DATE
# =============================
grouped = defaultdict(list)

for n in unique:
    grouped[n["date"]].append(n)

# =============================
# BUILD HTML (NO ANALYST INSIGHT)
# =============================
html_content = ""

for date in sorted(grouped.keys(), reverse=True):

    day_news = grouped[date]

    html_content += f"""
    <div class="day">

        <div class="date">📅 {date}</div>

        <div class="summary-box">
            📰 <b>Daily Summary</b><br>
            Total News: {len(day_news)}<br>
            Categories: {len(set([n['category'] for n in day_news]))}
        </div>
    """

    for n in day_news:

        html_content += f"""
        <div class="item">

            <div class="cat">{n['category']}</div>

            <div class="title">{n['title']}</div>

            <div class="desc">{n['summary']}</div>

            <a href="{n['link']}" target="_blank">Read →</a>

        </div>
        """

    html_content += "</div>"

# =============================
# FINAL HTML
# =============================
html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Retail Intelligence Dashboard</title>

<style>

body {{
    font-family: Arial;
    background: #fafaf7;
    padding: 20px;
}}

.header {{
    font-size: 26px;
    font-weight: bold;
}}

.sub {{
    font-size: 12px;
    color: #666;
}}

.day {{
    margin-bottom: 30px;
}}

.date {{
    font-size: 18px;
    font-weight: bold;
}}

.summary-box {{
    background: #f1f5f9;
    border-left: 4px solid #334155;
    padding: 10px;
    font-size: 12px;
    margin: 10px 0;
}}

.item {{
    background: white;
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 8px;
}}

.cat {{
    font-size: 10px;
    color: #666;
}}

.title {{
    font-weight: bold;
}}

.desc {{
    font-size: 12px;
    color: #444;
}}

a {{
    font-size: 12px;
    color: blue;
}}

</style>

</head>

<body>

<div class="header">Retail Intelligence Dashboard</div>
<div class="sub">Last Updated: {now_ist}</div>

{html_content}

</body>
</html>
"""

# =============================
# SAVE FILE
# =============================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
