import feedparser
from datetime import datetime, timezone, timedelta
import re
from collections import defaultdict

# =============================
# RSS SOURCES (HIGH QUALITY)
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
# NORMALIZE
# =============================
def norm(t):
    return " ".join(t.lower().split())

# =============================
# FETCH NEWS (FIXED - HIGH VOLUME)
# =============================
news = []

for url in feeds:
    feed = feedparser.parse(url)

    # IMPORTANT FIX: keep volume high
    for e in feed.entries[:25]:

        summary = re.sub("<.*?>", "", e.get("summary", ""))

        news.append({
            "title": e.title,
            "link": e.link,
            "summary": summary[:180],
            "date": clean_date(e.get("published", "")),
            "category": get_category(e.title)
        })

# =============================
# DEDUP (SAFE, NOT AGGRESSIVE)
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
# DAILY 4–5 LINE SUMMARY ENGINE (NEW REQUIREMENT)
# =============================
def daily_summary(day_news):

    total = len(day_news)

    categories = {}
    keywords = {}

    for n in day_news:
        categories[n["category"]] = categories.get(n["category"], 0) + 1

        for w in n["title"].lower().split():
            if len(w) > 4:
                keywords[w] = keywords.get(w, 0) + 1

    top_cat = sorted(categories.items(), key=lambda x: x[1], reverse=True)

    dominant = top_cat[0][0] if top_cat else "Mixed Market"

    top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
    kw_text = ", ".join([k[0] for k in top_keywords])

    return f"""
Total news today: {total}. The day was primarily driven by {dominant} related developments.
Key themes observed across the ecosystem include {kw_text}.
Retail and digital commerce segments continued to show active movement across multiple platforms.
Overall sentiment reflects ongoing structural activity in the {dominant} space.
Market attention remains concentrated on consolidated retail and startup ecosystem updates.
"""

# =============================
# BUILD HTML CONTENT (LIST VIEW + FILTER READY)
# =============================
content = ""

for date in sorted(grouped.keys(), reverse=True):

    day_news = grouped[date]

    summary = daily_summary(day_news)

    content += f"""
    <div class="day-section">

        <div class="date-header">📅 {date}</div>

        <div class="summary-box">
            📰 <b>Daily Summary</b><br>
            {summary}
        </div>
    """

    for n in day_news:

        content += f"""
        <div class="item"
             data-date="{date}"
             data-category="{n['category']}">

            <div class="meta">{n['category']}</div>

            <div class="title">{n['title']}</div>

            <div class="desc">{n['summary']}</div>

            <a href="{n['link']}" target="_blank">Read →</a>
        </div>
        """

    content += "</div>"

# =============================
# FINAL HTML (SEARCH + FILTER + DATE RANGE)
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

.controls {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 15px 0;
}}

input, select {{
    padding: 8px;
    font-size: 12px;
}}

.day-section {{
    margin-bottom: 30px;
}}

.date-header {{
    font-size: 18px;
    font-weight: bold;
}}

.summary-box {{
    background: #f1f5f9;
    border-left: 4px solid #334155;
    padding: 10px;
    font-size: 12px;
    margin: 10px 0;
    white-space: pre-line;
}}

.item {{
    background: white;
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 8px;
}}

.meta {{
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

<!-- CONTROLS -->
<div class="controls">

<input id="search" placeholder="Search news...">

<select id="category">
    <option value="">All Categories</option>
    <option>Quick Commerce</option>
    <option>Ecommerce</option>
    <option>FMCG</option>
    <option>Startups</option>
    <option>Retail / Business</option>
</select>

<input type="date" id="fromDate">
<input type="date" id="toDate">

</div>

<div id="list">
{content}
</div>

<script>

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
# SAVE FILE
# =============================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
