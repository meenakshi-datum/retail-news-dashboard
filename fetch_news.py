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
# FETCH NEWS
# =============================
news = []

for url in feeds:
    feed = feedparser.parse(url)

    for e in feed.entries[:8]:

        summary = re.sub("<.*?>", "", e.get("summary", ""))

        news.append({
            "title": e.title,
            "link": e.link,
            "summary": summary[:160],
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
# LEVEL 2 AI ANALYST ENGINE
# =============================
def generate_ai_insight(day_news):

    cat_count = {}
    keyword_count = {}

    for n in day_news:

        cat_count[n["category"]] = cat_count.get(n["category"], 0) + 1

        for w in n["title"].lower().split():
            if len(w) > 4:
                keyword_count[w] = keyword_count.get(w, 0) + 1

    top_categories = sorted(cat_count.items(), key=lambda x: x[1], reverse=True)[:3]
    top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:6]

    dominant = top_categories[0][0] if top_categories else "Mixed Market"

    trend_words = ", ".join([k[0] for k in top_keywords[:5]])

    narrative = ""

    if cat_count.get("Quick Commerce", 0) >= 2:
        narrative += "Quick commerce is showing strong expansion + delivery + funding activity. "

    if cat_count.get("Ecommerce", 0) >= 2:
        narrative += "E-commerce platforms show steady marketplace movement. "

    if cat_count.get("Startups", 0) >= 2:
        narrative += "Startup ecosystem shows funding/acquisition momentum. "

    if cat_count.get("FMCG", 0) >= 1:
        narrative += "FMCG remains stable with brand-level updates. "

    return f"""
📊 Market Overview:
{narrative}

🧠 Dominant Sector: {dominant}

🔥 Emerging Themes: {trend_words}

⚠️ Interpretation:
Market attention is concentrated around {dominant.lower()}-driven activity,
with repeated signals indicating short-term momentum formation.

💡 So What:
This suggests shifting retail intelligence focus toward {dominant.lower()} ecosystem developments.
"""

# =============================
# BUILD HTML CONTENT
# =============================
content = ""

for date in sorted(grouped.keys(), reverse=True):

    day_news = grouped[date]

    insight = generate_ai_insight(day_news)

    content += f"""
    <div class="day-section">

        <div class="date-header">📅 {date}</div>

        <div class="insight-box">
            🧠 <b>AI Analyst Insight</b><br>
            {insight}
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
# FINAL HTML
# =============================
html = f"""
<!DOCTYPE html>
<html>
<head>
<title>Retail Intelligence Dashboard - Level 2</title>

<style>

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
    font-size: 12px;
    color: #666;
}}

.controls {{
    display: flex;
    gap: 10px;
    margin: 15px 0;
    flex-wrap: wrap;
}}

input, select {{
    padding: 8px;
    font-size: 12px;
}}

.day-section {{
    margin-bottom: 25px;
}}

.date-header {{
    font-size: 18px;
    font-weight: bold;
    margin: 10px 0;
}}

.insight-box {{
    background: #eef2ff;
    border-left: 4px solid #4f46e5;
    padding: 10px;
    font-size: 12px;
    margin-bottom: 10px;
    white-space: pre-line;
}}

.item {{
    background: white;
    border: 1px solid #ddd;
    padding: 12px;
    margin-bottom: 8px;
}}

.meta {{
    font-size: 10px;
    color: #666;
}}

.title {{
    font-size: 14px;
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

<div class="header">Retail Intelligence Dashboard - Level 2</div>
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
