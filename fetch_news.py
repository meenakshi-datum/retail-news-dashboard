import feedparser
from datetime import datetime, timezone, timedelta
import re
import time
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
    "https://entrackr.com/feed/",
    "https://www.retaildive.com/feeds/news/",
    "https://techcrunch.com/feed/"
]

# =============================
# CATEGORY SYSTEM
# =============================
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

# =============================
# IST TIME
# =============================
ist = timezone(timedelta(hours=5, minutes=30))
last_updated = datetime.now(ist).strftime("%Y-%m-%d %H:%M IST")

# =============================
# DATE CLEANER
# =============================
def clean_date(date_str):
    if not date_str:
        return datetime.now(ist).strftime("%Y-%m-%d")

    try:
        return time.strftime("%Y-%m-%d", time.strptime(date_str[:25], "%a, %d %b %Y"))
    except:
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            return datetime.now(ist).strftime("%Y-%m-%d")

# =============================
# COLLECT NEWS
# =============================
all_news = []

for url in feeds:
    feed = feedparser.parse(url)

    for entry in feed.entries[:8]:

        summary = re.sub("<.*?>", "", entry.get("summary", ""))

        raw_date = entry.get("published") or entry.get("updated") or ""

        all_news.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary[:160],
            "date": clean_date(raw_date),
            "category": get_category(entry.title)
        })

# =============================
# REMOVE DUPLICATES
# =============================
seen = set()
unique_news = []

for n in all_news:
    if n["title"] not in seen:
        unique_news.append(n)
        seen.add(n["title"])

# =============================
# GROUP BY DATE
# =============================
grouped = defaultdict(list)

for n in unique_news:
    grouped[n["date"]].append(n)

# =============================
# DAILY INTELLIGENCE SUMMARY
# =============================
def generate_day_summary(news_list):
    cats = {}
    words = {}

    for n in news_list:
        cats[n["category"]] = cats.get(n["category"], 0) + 1

        for w in n["title"].lower().split():
            if len(w) > 4:
                words[w] = words.get(w, 0) + 1

    top_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:3]
    top_words = sorted(words.items(), key=lambda x: x[1], reverse=True)[:5]

    return (
        "📊 Key Intelligence: "
        + " | Top sectors: "
        + ", ".join([f"{c[0]} ({c[1]})" for c in top_cats])
        + " | Trending: "
        + ", ".join([w[0] for w in top_words])
    )

# =============================
# BUILD DATUM STYLE HTML
# =============================
content = ""

for date in sorted(grouped.keys(), reverse=True):

    day_news = grouped[date]
    summary = generate_day_summary(day_news)

    content += f"""

    <!-- SECTION -->
    <div class="section-head">
        <div class="section-num">{date}</div>
        <div>
            <div class="section-title">Retail Intelligence Report</div>
            <div class="section-lede">{summary}</div>
        </div>
    </div>

    <!-- EXHIBIT -->
    <div class="ex">

        <div class="ex-head">
            <div class="ex-num">EXHIBIT · {date}</div>
            <div class="ex-cap">Daily News Intelligence Feed</div>
        </div>

        <div class="ex-body">
    """

    for n in day_news:

        content += f"""
        <div style="padding:10px 0; border-bottom:1px solid #e7e5dd;">

            <div style="font-size:10px; letter-spacing:1.2px; text-transform:uppercase; color:#7c3aed;">
                {n['category']}
            </div>

            <div style="font-family: DM Serif Display, serif; font-size:16px; color:#1e1b4b;">
                {n['title']}
            </div>

            <div style="font-size:13px; color:#475569;">
                {n['summary']}
            </div>

            <a href="{n['link']}" target="_blank"
               style="font-size:11px; color:#4F46E5;">
               Read more →
            </a>

        </div>
        """

    content += """
        </div>
    </div>
    """

# =============================
# FINAL HTML
# =============================
html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Datum Wiki · Retail Intelligence</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- GOOGLE FONTS -->
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Questrial&display=swap" rel="stylesheet">

<style>

/* =============================
   YOUR DATUM STYLE (SIMPLIFIED CORE)
   ============================= */

body {{
    background: #fafaf7;
    font-family: Questrial, sans-serif;
    margin: 0;
    padding: 32px 40px;
    color: #0f172a;
}}

.masthead {{
    background: #1e1b4b;
    color: white;
    padding: 14px 20px;
    border-bottom: 4px solid #fbbf24;
    font-family: DM Serif Display, serif;
}}

.byline {{
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #64748b;
    margin: 12px 0;
}}

.kpis {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: #e7e5dd;
    margin-bottom: 20px;
}}

.kpi {{
    background: white;
    padding: 14px;
}}

.kpi .val {{
    font-family: DM Serif Display;
    font-size: 24px;
    color: #1e1b4b;
}}

.section-head {{
    margin-top: 30px;
    border-top: 2px solid #1e1b4b;
    padding-top: 10px;
}}

.section-num {{
    font-family: DM Serif Display;
    font-size: 20px;
    color: #7c3aed;
}}

.section-title {{
    font-family: DM Serif Display;
    font-size: 22px;
    color: #1e1b4b;
}}

.section-lede {{
    font-size: 13px;
    color: #475569;
}}

.ex {{
    background: white;
    border: 1px solid #e7e5dd;
    margin-top: 10px;
}}

.ex-head {{
    padding: 10px;
    border-bottom: 1px solid #e7e5dd;
}}

.ex-body {{
    padding: 14px;
}}

.ex-num {{
    font-size: 10px;
    text-transform: uppercase;
    color: #7c3aed;
}}

.ex-cap {{
    font-family: DM Serif Display;
    font-size: 14px;
    color: #1e1b4b;
}}

a {{
    color: #4F46E5;
    text-decoration: none;
}}

</style>

</head>

<body>

<div class="masthead">
    DATUM WIKI · Retail Intelligence Dashboard
</div>

<div class="byline">
    Last updated: {last_updated}
</div>

<div class="kpis">
    <div class="kpi"><div>Total News</div><div class="val">{len(unique_news)}</div></div>
    <div class="kpi"><div>Days Covered</div><div class="val">{len(grouped)}</div></div>
    <div class="kpi"><div>System</div><div class="val">Live RSS</div></div>
</div>

{content}

</body>
</html>
"""

# =============================
# WRITE OUTPUT
# =============================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
