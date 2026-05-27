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
    "https://entrackr.com/feed/",
]

# =============================
# CATEGORY FUNCTION
# =============================
def get_category(title):
    title = title.lower()

    if any(x in title for x in ["blinkit", "zepto", "swiggy", "quick commerce"]):
        return "Quick Commerce"

    if any(x in title for x in ["amazon", "flipkart", "ecommerce"]):
        return "Ecommerce"

    if any(x in title for x in ["fmcg", "nestle", "dabur"]):
        return "FMCG"

    if any(x in title for x in ["startup", "funding", "raise", "acquire"]):
        return "Startups"

    return "Retail / Business"

# =============================
# IST TIME
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
# COLLECT NEWS
# =============================
news = []

for feed_url in feeds:
    feed = feedparser.parse(feed_url)

    for e in feed.entries[:8]:

        summary = re.sub("<.*?>", "", e.get("summary", ""))

        news.append({
            "title": e.title,
            "link": e.link,
            "summary": summary[:150],
            "date": clean_date(e.get("published", "")),
            "category": get_category(e.title)
        })

# =============================
# REMOVE DUPLICATES
# =============================
seen = set()
unique = []

for n in news:
    if n["title"] not in seen:
        unique.append(n)
        seen.add(n["title"])

# =============================
# GROUP BY DATE
# =============================
grouped = defaultdict(list)

for n in unique:
    grouped[n["date"]].append(n)

# =============================
# DAILY SUMMARY ENGINE
# =============================
def summary(day_news):
    cats = {}
    words = {}

    for n in day_news:
        cats[n["category"]] = cats.get(n["category"], 0) + 1
        for w in n["title"].split():
            if len(w) > 4:
                words[w.lower()] = words.get(w.lower(), 0) + 1

    top_cat = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:3]
    top_words = sorted(words.items(), key=lambda x: x[1], reverse=True)[:5]

    return "Top sectors: " + ", ".join([c[0] for c in top_cat]) + " | Trending: " + ", ".join([w[0] for w in top_words])

# =============================
# BUILD HTML ITEMS (LIST VIEW ONLY)
# =============================
items = ""

for date in sorted(grouped.keys(), reverse=True):

    day_news = grouped[date]
    day_summary = summary(day_news)

    for n in day_news:

        items += f"""
        <div class="item"
             data-date="{date}"
             data-category="{n['category']}">

            <div class="meta">{date} · {n['category']}</div>

            <div class="title">{n['title']}</div>

            <div class="desc">{n['summary']}</div>

            <a href="{n['link']}" target="_blank">Read →</a>
        </div>
        """

# =============================
# FINAL HTML
# =============================
html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Retail Intelligence</title>

<style>

/* ================= UI ================= */

body {{
    font-family: Arial;
    background: #fafaf7;
    margin: 0;
    padding: 20px;
}}

.header {{
    font-size: 26px;
    font-weight: bold;
}}

.sub {{
    color: #666;
    font-size: 12px;
}}

.controls {{
    display: flex;
    gap: 10px;
    margin: 15px 0;
}}

input, select {{
    padding: 8px;
    font-size: 12px;
}}

.item {{
    background: white;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
}}

.meta {{
    font-size: 10px;
    color: #666;
}}

.title {{
    font-size: 15px;
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

<!-- CONTROLS -->
<div class="controls">

<input id="search" placeholder="Search news...">

<select id="category">
    <option value="">All Categories</option>
    <option>Retail / Business</option>
    <option>Quick Commerce</option>
    <option>Ecommerce</option>
    <option>FMCG</option>
    <option>Startups</option>
</select>

<input type="date" id="fromDate">
<input type="date" id="toDate">

</div>

<!-- LIST -->
<div id="list">
{items}
</div>

<script>

// ================= SEARCH =================
document.getElementById("search").addEventListener("input", filter);
document.getElementById("category").addEventListener("change", filter);
document.getElementById("fromDate").addEventListener("change", filter);
document.getElementById("toDate").addEventListener("change", filter);

function filter() {{

    let search = document.getElementById("search").value.toLowerCase();
    let cat = document.getElementById("category").value;
    let from = document.getElementById("fromDate").value;
    let to = document.getElementById("toDate").value;

    let items = document.querySelectorAll(".item");

    items.forEach(i => {{

        let text = i.innerText.toLowerCase();
        let category = i.dataset.category;
        let date = i.dataset.date;

        let ok =
            (text.includes(search)) &&
            (cat === "" || category === cat) &&
            (!from || date >= from) &&
            (!to || date <= to);

        i.style.display = ok ? "block" : "none";
    }});
}}

</script>

</body>
</html>
"""

# =============================
# SAVE
# =============================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
