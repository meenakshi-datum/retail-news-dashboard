import feedparser
from datetime import datetime, timezone, timedelta
import re
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
# IST TIME
# -----------------------------
ist = timezone(timedelta(hours=5, minutes=30))
last_updated = datetime.now(ist).strftime("%Y-%m-%d %H:%M IST")

# -----------------------------
# COLLECT NEWS
# -----------------------------
all_news = []

for url in feeds:
    feed = feedparser.parse(url)

    for entry in feed.entries[:8]:

        summary = re.sub("<.*?>", "", entry.get("summary", ""))

        raw_date = entry.get("published") or entry.get("updated") or ""
        try:
            clean_date = time.strftime("%Y-%m-%d", time.strptime(raw_date[:25], "%a, %d %b %Y"))
        except:
            clean_date = datetime.now(ist).strftime("%Y-%m-%d")

        all_news.append({
            "title": entry.title,
            "link": entry.link,
            "summary": summary[:180],
            "date": clean_date,
            "category": get_category(entry.title)
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
grouped = defaultdict(list)
date_summary = {}

for n in unique_news:
    grouped[n["date"]].append(n)
    date_summary[n["date"]] = date_summary.get(n["date"], 0) + 1

# -----------------------------
# BUILD LIST VIEW CARDS
# -----------------------------
news_cards = ""

for date in sorted(grouped.keys(), reverse=True):

    news_cards += f"""
    <h2 class="date-header">{date} ({date_summary[date]} news)</h2>
    """

    for n in grouped[date]:

        news_cards += f"""
        <div class="card"
             data-title="{n['title']}"
             data-category="{n['category']}"
             data-date="{n['date']}">

            <div class="tag">{n['category']}</div>
            <h3>{n['title']}</h3>
            <p>{n['summary']}</p>
            <a href="{n['link']}" target="_blank">Read more →</a>
        </div>
        """

# -----------------------------
# FINAL HTML (UI + SEARCH + FILTER + DATE)
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
}}

.sub {{
    color: #94a3b8;
    margin-bottom: 10px;
}}

.topbar {{
    display: flex;
    gap: 10px;
    margin: 15px 0;
    flex-wrap: wrap;
}}

input, select {{
    padding: 8px;
    border-radius: 6px;
    border: none;
}}

.list {{
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

.card {{
    background: #111c33;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #1f2a44;
    display: flex;
    flex-direction: column;
}}

.card:hover {{
    transform: translateY(-3px);
}}

.tag {{
    font-size: 12px;
    color: #60a5fa;
    margin-bottom: 6px;
}}

.date-header {{
    margin-top: 25px;
    border-left: 4px solid #60a5fa;
    padding-left: 10px;
}}

h3 {{
    margin: 6px 0;
}}

p {{
    font-size: 13px;
    color: #cbd5e1;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}

a {{
    color: #60a5fa;
    margin-top: auto;
}}
</style>
</head>

<body>

<div class="header">Retail Intelligence Dashboard</div>
<div class="sub">Last updated: {last_updated}</div>

<!-- ================= TOP BAR (SEARCH + FILTER) ================= -->
<div class="topbar">
    <input type="text" id="search" placeholder="Search news...">
    
    <select id="category">
        <option value="all">All Categories</option>
        <option value="Retail">Retail</option>
        <option value="Ecommerce">Ecommerce</option>
        <option value="FMCG">FMCG</option>
        <option value="Quick Commerce">Quick Commerce</option>
        <option value="Startups / Funding">Startups</option>
        <option value="Business / Tech">Business</option>
    </select>

    <input type="date" id="start">
    <input type="date" id="end">
</div>

<!-- ================= LIST VIEW ================= -->
<div class="list">
{news_cards}
</div>

<!-- ================= JS FILTER SYSTEM ================= -->
<script>
const search = document.getElementById("search");
const category = document.getElementById("category");
const start = document.getElementById("start");
const end = document.getElementById("end");

function filterNews() {{
    const s = search.value.toLowerCase();
    const c = category.value;
    const sd = start.value;
    const ed = end.value;

    document.querySelectorAll(".card").forEach(card => {{
        const title = card.dataset.title.toLowerCase();
        const cat = card.dataset.category;
        const date = card.dataset.date;

        let show = true;

        if (s && !title.includes(s)) show = false;
        if (c !== "all" && cat !== c) show = false;
        if (sd && date < sd) show = false;
        if (ed && date > ed) show = false;

        card.style.display = show ? "block" : "none";
    }});
}}

search.addEventListener("input", filterNews);
category.addEventListener("change", filterNews);
start.addEventListener("change", filterNews);
end.addEventListener("change", filterNews);
</script>

</body>
</html>
"""

# -----------------------------
# WRITE FILE
# -----------------------------
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
