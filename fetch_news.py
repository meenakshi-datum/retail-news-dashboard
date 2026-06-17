import feedparser
from datetime import datetime, timezone, timedelta
import re
from collections import defaultdict
import os
import json

# =========================================================
# RSS SOURCES
# =========================================================

feeds = [

    # Indian Retail
    "https://retail.economictimes.indiatimes.com/rss/topstories",
    "https://indiaretailing.com/feed",

    # Business
    "https://www.livemint.com/rss/companies",
    "https://www.business-standard.com/rss/latest.rss",
    "https://www.moneycontrol.com/rss/business.xml",

    # Startup
    "https://inc42.com/feed/",
    "https://entrackr.com/feed/",
    "https://yourstory.com/feed",

    # Global Retail
    "https://www.retaildive.com/feeds/news/",
    "https://www.retailbrew.com/feed/",

    # Retail Tech
    "https://www.retailtouchpoints.com/rss.xml",

    # Grocery
    "https://progressivegrocer.com/rss.xml",

    # Commerce
    "https://www.pymnts.com/feed/",

    # Indian Retailer
    "https://www.indianretailer.com/rss/retail-business",
    "https://www.indianretailer.com/rss/technology-ecommerce",
    "https://www.indianretailer.com/rss/ir-just-in",

    # Technology
    "https://techcrunch.com/feed/"
]

# =========================================================
# CATEGORY ENGINE
# =========================================================
def get_category(title):

    t = title.lower()

    if any(x in t for x in ["blinkit", "zepto", "swiggy", "quick commerce"]):
        return "Quick Commerce"

    if any(x in t for x in ["amazon", "flipkart", "ecommerce", "e-commerce"]):
        return "Ecommerce"

    if any(x in t for x in ["fmcg", "nestle", "dabur", "hul"]):
        return "FMCG"

    if any(x in t for x in ["startup", "funding", "raises", "acquire", "merger"]):
        return "Startups"

    return "Retail / Business"

# =========================================================
# NORMALIZE TITLES
# =========================================================
def normalize_key(title):

    title = title.lower()
    title = re.sub(r"[^a-z0-9 ]", "", title)
    title = " ".join(title.split()[:10])

    return title

# =========================================================
# IST TIME
# =========================================================
ist = timezone(timedelta(hours=5, minutes=30))

now_ist = datetime.now(ist)

last_updated = now_ist.strftime("%Y-%m-%d %H:%M IST")

today = now_ist.strftime("%Y-%m-%d")

# =========================================================
# CLEAN DATE
# =========================================================
def clean_date(date_str):

    try:

        return datetime.strptime(
            date_str[:25],
            "%a, %d %b %Y %H:%M:%S"
        ).strftime("%Y-%m-%d")

    except:

        try:

            return datetime.strptime(
                date_str[:16],
                "%a, %d %b %Y"
            ).strftime("%Y-%m-%d")

        except:
            return today

# =========================================================
# FETCH NEWS
# =========================================================
all_news = []

for url in feeds:

    print("=" * 80)
    print("Checking Feed:")
    print(url)

    feed = feedparser.parse(url)

    print(f"Articles Found: {len(feed.entries)}")

    if len(feed.entries) == 0:
        print("❌ Feed returned 0 articles")
        continue

    print("✅ Feed Working")

    for e in feed.entries[:50]:

        summary = re.sub("<.*?>", "", e.get("summary", ""))

        all_news.append({

            "title": e.title,
            "link": e.link,
            "summary": summary[:220],
            "date": clean_date(e.get("published", "")),
            "category": get_category(e.title)

        })
# =========================================================
# DEDUP
# =========================================================
seen = set()
unique = []

for n in all_news:

    key = normalize_key(n["title"])

    # SOFT DEDUP
    if key not in seen or len(unique) < 120:

        seen.add(key)
        unique.append(n)

# =========================================================
# SAVE DAILY SNAPSHOT
# =========================================================
os.makedirs("data", exist_ok=True)

snapshot_file = f"data/{today}.json"

existing_news = []

if os.path.exists(snapshot_file):

    with open(snapshot_file, "r", encoding="utf-8") as f:

        existing_news = json.load(f)

combined = existing_news + unique

final_seen = set()
final_news = []

for n in combined:

    k = normalize_key(n["title"])

    if k not in final_seen:

        final_seen.add(k)
        final_news.append(n)

# SAVE PERMANENT ARCHIVE
with open(snapshot_file, "w", encoding="utf-8") as f:

    json.dump(final_news, f, ensure_ascii=False, indent=2)

# =========================================================
# LOAD ALL HISTORICAL FILES
# =========================================================
all_archived_news = []

for file in os.listdir("data"):

    if file.endswith(".json"):

        with open(f"data/{file}", "r", encoding="utf-8") as f:

            data = json.load(f)

            all_archived_news.extend(data)

# =========================================================
# GROUP BY DATE
# =========================================================
grouped = defaultdict(list)

for n in all_archived_news:

    grouped[n["date"]].append(n)

# =========================================================
# DAILY SUMMARY ENGINE
# =========================================================
def daily_summary(day_news):

    total = len(day_news)

    categories = {}
    keywords = {}

    for n in day_news:

        categories[n["category"]] = categories.get(n["category"], 0) + 1

        for w in n["title"].lower().split():

            if len(w) > 4:

                keywords[w] = keywords.get(w, 0) + 1

    top_cat = sorted(
        categories.items(),
        key=lambda x: x[1],
        reverse=True
    )

    dominant = top_cat[0][0] if top_cat else "Retail"

    top_keywords = sorted(
        keywords.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    kw_text = ", ".join([k[0] for k in top_keywords])

    return f"""
Total news captured today: {total}. Major developments were concentrated around {dominant.lower()} related activity.
Key themes observed across the retail ecosystem included {kw_text}.
Multiple companies across retail, ecommerce, and startup sectors remained active through expansion, funding, and operational developments.
Consumer commerce and digital retail continued to dominate overall news flow across platforms.
The broader market environment reflected continued movement in organized retail and commerce ecosystems.
"""

# =========================================================
# BUILD CONTENT
# =========================================================
content = ""

for date in sorted(grouped.keys(), reverse=True):

    day_news = grouped[date]

    summary = daily_summary(day_news)

    content += f"""

    <div class="day-section">

        <div class="date-header">
            📅 {date}
        </div>

        <div class="summary-box">
            <b>Daily Summary</b><br><br>
            {summary}
        </div>

    """

    for n in day_news:

        content += f"""

        <div class="item"
             data-category="{n['category']}"
             data-date="{date}">

            <div class="meta">
                {n['category']}
            </div>

            <div class="title">
                {n['title']}
            </div>

            <div class="desc">
                {n['summary']}
            </div>

            <a href="{n['link']}" target="_blank">
                Read Full Article →
            </a>

        </div>

        """

    content += "</div>"

# =========================================================
# FINAL HTML
# =========================================================
html = f"""

<!DOCTYPE html>

<html>

<head>

<title>Retail Intelligence Dashboard</title>

<style>

body {{

    font-family: Arial;
    background: #fafaf7;
    margin: 0;
    padding: 20px;
}}

.header {{

    font-size: 32px;
    font-weight: bold;
}}

.sub {{

    color: #666;
    font-size: 12px;
    margin-bottom: 20px;
}}

.controls {{

    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}}

input, select {{

    padding: 10px;
    border: 1px solid #ccc;
    font-size: 12px;
}}

.day-section {{

    margin-bottom: 40px;
}}

.date-header {{

    font-size: 22px;
    font-weight: bold;
    margin-bottom: 10px;
}}

.summary-box {{

    background: #eef2ff;
    border-left: 4px solid #4f46e5;
    padding: 14px;
    margin-bottom: 14px;
    white-space: pre-line;
    line-height: 1.7;
    font-size: 13px;
}}

.item {{

    background: white;
    border: 1px solid #ddd;
    padding: 14px;
    margin-bottom: 10px;
}}

.meta {{

    font-size: 10px;
    color: #666;
    margin-bottom: 6px;
}}

.title {{

    font-size: 17px;
    font-weight: bold;
    margin-bottom: 8px;
}}

.desc {{

    font-size: 13px;
    line-height: 1.6;
    color: #444;
    margin-bottom: 8px;
}}

a {{

    color: #2563eb;
    text-decoration: none;
    font-size: 13px;
}}

a:hover {{

    text-decoration: underline;
}}

</style>

</head>

<body>

<div class="header">
Retail Intelligence Dashboard
</div>

<div class="sub">
Last Updated: {last_updated}
</div>

<div class="controls">

<input
    type="text"
    id="search"
    placeholder="Search news..."
>

<select id="category">

    <option value="">
        All Categories
    </option>

    <option value="Quick Commerce">
        Quick Commerce
    </option>

    <option value="Ecommerce">
        Ecommerce
    </option>

    <option value="FMCG">
        FMCG
    </option>

    <option value="Startups">
        Startups
    </option>

    <option value="Retail / Business">
        Retail / Business
    </option>

</select>

<input type="date" id="fromDate">
<input type="date" id="toDate">

</div>

{content}

<script>

document.getElementById("search").addEventListener("input", filterNews);

document.getElementById("category").addEventListener("change", filterNews);

document.getElementById("fromDate").addEventListener("change", filterNews);

document.getElementById("toDate").addEventListener("change", filterNews);

function filterNews() {{

    let search =
        document.getElementById("search")
        .value
        .toLowerCase();

    let category =
        document.getElementById("category")
        .value;

    let fromDate =
        document.getElementById("fromDate")
        .value;

    let toDate =
        document.getElementById("toDate")
        .value;

    let items =
        document.querySelectorAll(".item");

    items.forEach(item => {{

        let text =
            item.innerText.toLowerCase();

        let cat =
            item.dataset.category;

        let date =
            item.dataset.date;

        let visible = true;

        if (!text.includes(search))
            visible = false;

        if (category && cat !== category)
            visible = false;

        if (fromDate && date < fromDate)
            visible = false;

        if (toDate && date > toDate)
            visible = false;

        item.style.display =
            visible ? "block" : "none";

    }});
}}

</script>

</body>
</html>

"""

# =========================================================
# SAVE HTML
# =========================================================
with open("index.html", "w", encoding="utf-8") as f:

    f.write(html)

print("Dashboard generated successfully.")
