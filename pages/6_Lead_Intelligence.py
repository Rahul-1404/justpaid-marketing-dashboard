"""
Lead Intelligence — Find warm leads from Reddit, HN, and YC communities.
People actively complaining about payroll, contractor payments, invoicing = JustPaid prospects.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="Lead Intelligence | JustPaid Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.google.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #0E1117; }
    header[data-testid="stHeader"] { background: transparent; }
    section[data-testid="stSidebar"] {
        background: #1A1D29;
        border-right: 1px solid rgba(255,255,255,0.04);
    }

    .page-hero {
        background: linear-gradient(135deg, rgba(108,92,231,0.15) 0%, rgba(0,206,201,0.08) 100%);
        border: 1px solid rgba(108,92,231,0.2);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
    }
    .page-hero h1 {
        font-size: 1.8rem;
        font-weight: 800;
        color: #E2E2EA;
        margin: 0 0 0.5rem;
    }
    .page-hero p {
        color: #8A8A9A;
        font-size: 0.95rem;
        margin: 0;
    }

    .signal-card {
        background: #1A1D29;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s;
        cursor: pointer;
    }
    .signal-card:hover {
        border-color: rgba(108,92,231,0.4);
        box-shadow: 0 4px 20px rgba(108,92,231,0.1);
    }
    .signal-source {
        display: inline-block;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-bottom: 0.6rem;
    }
    .signal-reddit { background: rgba(255,69,0,0.15); color: #FF4500; }
    .signal-hn { background: rgba(255,102,0,0.15); color: #FF6600; }
    .signal-yc { background: rgba(108,92,231,0.15); color: #A29BFE; }

    .signal-title {
        font-size: 0.92rem;
        font-weight: 600;
        color: #E2E2EA;
        margin-bottom: 0.4rem;
        line-height: 1.4;
    }
    .signal-meta {
        font-size: 0.72rem;
        color: #5A5A6A;
        display: flex;
        gap: 1rem;
    }
    .signal-pain {
        font-size: 0.8rem;
        color: #8A8A9A;
        margin-top: 0.5rem;
        line-height: 1.5;
        font-style: italic;
        border-left: 2px solid rgba(108,92,231,0.4);
        padding-left: 0.8rem;
    }
    .signal-tag {
        display: inline-block;
        font-size: 0.62rem;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        margin-right: 0.3rem;
        font-weight: 600;
    }
    .tag-hot { background: rgba(225,112,85,0.15); color: #E17055; }
    .tag-payroll { background: rgba(0,184,148,0.15); color: #00B894; }
    .tag-invoice { background: rgba(108,92,231,0.15); color: #A29BFE; }
    .tag-contractor { background: rgba(253,203,110,0.15); color: #FDCB6E; }

    .stat-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: rgba(255,255,255,0.04);
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        font-size: 0.75rem;
        color: #8A8A9A;
        font-weight: 500;
    }

    .section-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #E2E2EA;
        margin: 1.8rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .insight-box {
        background: linear-gradient(135deg, rgba(0,184,148,0.08), rgba(0,206,201,0.05));
        border: 1px solid rgba(0,184,148,0.2);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .insight-box h4 {
        color: #00B894;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 0 0 0.5rem;
    }
    .insight-box p {
        color: #E2E2EA;
        font-size: 0.88rem;
        margin: 0;
        line-height: 1.6;
    }

    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #5A5A6A;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-size: 1.1rem; font-weight: 700; color: #E2E2EA; padding: 0.5rem 0;">
        <span style="background: linear-gradient(135deg, #6C5CE7, #00CEC9);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        JustPaid</span> Analytics
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.caption("🎯 Lead Intelligence")
    signal_sources = st.multiselect(
        "Sources",
        ["Reddit", "Hacker News", "YC Community"],
        default=["Reddit", "Hacker News"],
    )
    max_results = st.slider("Results per source", 5, 25, 10)
    if st.button("🔄 Refresh Signals", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.caption("Auto-refreshes every 6 hours")

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
    <h1>🎯 Lead Intelligence</h1>
    <p>Real-time demand signals from Reddit, Hacker News, and YC communities.
    These are people actively asking about payroll, contractor payments, and invoicing —
    JustPaid's warmest prospects.</p>
</div>
""", unsafe_allow_html=True)


# ── Data Fetchers ─────────────────────────────────────────────────────────

REDDIT_QUERIES = [
    ("payroll software startup", "payroll"),
    ("contractor payment problems", "contractor"),
    ("invoice payment startup", "invoice"),
    ("paying international contractors", "contractor"),
    ("payroll for small business", "payroll"),
    ("1099 contractor payment", "contractor"),
    ("accounts payable automation", "invoice"),
]

SUBREDDITS = [
    "r/startups",
    "r/Entrepreneur",
    "r/smallbusiness",
    "r/freelance",
    "r/accounting",
]

HN_QUERIES = [
    "payroll startup",
    "contractor payments",
    "invoice automation",
    "international payroll",
]


def time_ago(timestamp: int) -> str:
    dt = datetime.utcfromtimestamp(timestamp)
    diff = datetime.utcnow() - dt
    if diff.days > 0:
        return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    mins = diff.seconds // 60
    return f"{mins}m ago"


def tag_for_query(query: str) -> str:
    q = query.lower()
    if "payroll" in q:
        return '<span class="signal-tag tag-payroll">Payroll</span>'
    if "contractor" in q or "1099" in q:
        return '<span class="signal-tag tag-contractor">Contractor</span>'
    if "invoice" in q or "accounts" in q:
        return '<span class="signal-tag tag-invoice">Invoice</span>'
    return ""


def score_badge(score: int) -> str:
    if score >= 100:
        return '<span class="signal-tag tag-hot">🔥 Hot</span>'
    if score >= 20:
        return '<span class="signal-tag tag-payroll">↑ Rising</span>'
    return ""


@st.cache_data(ttl=21600)
def fetch_reddit_signals(max_items: int = 10) -> list[dict]:
    headers = {"User-Agent": "JustPaid-Analytics/1.0"}
    results = []
    seen_ids = set()

    for query, category in REDDIT_QUERIES:
        for subreddit in SUBREDDITS[:3]:
            try:
                url = (
                    f"https://www.reddit.com/{subreddit}/search.json"
                    f"?q={requests.utils.quote(query)}&sort=new&limit=5&restrict_sr=1&t=month"
                )
                r = requests.get(url, headers=headers, timeout=8)
                if r.status_code != 200:
                    continue
                data = r.json()
                for post in data.get("data", {}).get("children", []):
                    p = post["data"]
                    if p["id"] in seen_ids:
                        continue
                    if p.get("score", 0) < 3:
                        continue
                    seen_ids.add(p["id"])
                    results.append({
                        "source": "Reddit",
                        "subreddit": p.get("subreddit_name_prefixed", subreddit),
                        "title": p.get("title", ""),
                        "snippet": (p.get("selftext", "") or "")[:280],
                        "score": p.get("score", 0),
                        "comments": p.get("num_comments", 0),
                        "url": f"https://reddit.com{p.get('permalink', '')}",
                        "created": p.get("created_utc", 0),
                        "category": category,
                    })
                time.sleep(0.5)
            except Exception:
                continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_items]


@st.cache_data(ttl=21600)
def fetch_hn_signals(max_items: int = 10) -> list[dict]:
    results = []
    seen_ids = set()
    thirty_days_ago = int((datetime.utcnow() - timedelta(days=30)).timestamp())

    for query in HN_QUERIES:
        try:
            url = (
                f"https://hn.algolia.com/api/v1/search"
                f"?query={requests.utils.quote(query)}"
                f"&tags=story"
                f"&numericFilters=created_at_i>{thirty_days_ago},points>5"
                f"&hitsPerPage=5"
            )
            r = requests.get(url, timeout=8)
            if r.status_code != 200:
                continue
            data = r.json()
            for hit in data.get("hits", []):
                obj_id = hit.get("objectID", "")
                if obj_id in seen_ids:
                    continue
                seen_ids.add(obj_id)
                results.append({
                    "source": "Hacker News",
                    "title": hit.get("title", ""),
                    "snippet": hit.get("story_text", "") or "",
                    "score": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "url": hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}",
                    "created": hit.get("created_at_i", 0),
                    "category": "general",
                    "author": hit.get("author", ""),
                })
            time.sleep(0.3)
        except Exception:
            continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_items]


@st.cache_data(ttl=21600)
def fetch_yc_signals(max_items: int = 10) -> list[dict]:
    """YC-adjacent signals via HN 'Ask HN' posts about payroll/payments."""
    results = []
    try:
        url = (
            "https://hn.algolia.com/api/v1/search"
            "?query=payroll+contractors+payments+startup"
            "&tags=ask_hn"
            "&numericFilters=points>3"
            "&hitsPerPage=15"
        )
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            for hit in r.json().get("hits", []):
                obj_id = hit.get("objectID", "")
                results.append({
                    "source": "YC Community",
                    "title": hit.get("title", ""),
                    "snippet": hit.get("story_text", "") or "",
                    "score": hit.get("points", 0),
                    "comments": hit.get("num_comments", 0),
                    "url": f"https://news.ycombinator.com/item?id={obj_id}",
                    "created": hit.get("created_at_i", 0),
                    "category": "yc",
                    "author": hit.get("author", ""),
                })
    except Exception:
        pass

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:max_items]


# ── Summary Stats ─────────────────────────────────────────────────────────

all_signals = []
with st.spinner("Scanning for demand signals..."):
    if "Reddit" in signal_sources:
        all_signals += fetch_reddit_signals(max_results)
    if "Hacker News" in signal_sources:
        all_signals += fetch_hn_signals(max_results)
    if "YC Community" in signal_sources:
        all_signals += fetch_yc_signals(max_results)

total = len(all_signals)
hot_count = sum(1 for s in all_signals if s.get("score", 0) >= 50)
reddit_count = sum(1 for s in all_signals if s["source"] == "Reddit")
hn_count = sum(1 for s in all_signals if s["source"] == "Hacker News")
yc_count = sum(1 for s in all_signals if s["source"] == "YC Community")

c1, c2, c3, c4 = st.columns(4)
for col, label, value, color in [
    (c1, "Total Signals", total, "#6C5CE7"),
    (c2, "🔥 Hot (50+ upvotes)", hot_count, "#E17055"),
    (c3, "From Reddit", reddit_count, "#FF4500"),
    (c4, "From HN / YC", hn_count + yc_count, "#FF6600"),
]:
    with col:
        st.markdown(f"""
        <div style="background:#1A1D29;border:1px solid rgba(255,255,255,0.06);
                    border-radius:14px;padding:1.1rem;text-align:center;">
            <div style="font-size:0.65rem;color:#8A8A9A;text-transform:uppercase;
                        letter-spacing:1px;margin-bottom:0.4rem;">{label}</div>
            <div style="font-size:2rem;font-weight:800;color:{color};">{value}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# ── Key Insight ───────────────────────────────────────────────────────────
if all_signals:
    top = all_signals[0]
    st.markdown(f"""
    <div class="insight-box">
        <h4>💡 Top Signal Right Now</h4>
        <p><strong>{top['title']}</strong> — {top['score']} upvotes, {top['comments']} comments
        from {top.get('subreddit', top['source'])}. This is a warm prospect actively
        discussing the pain JustPaid solves.</p>
    </div>
    """, unsafe_allow_html=True)

# ── Signal Feed ───────────────────────────────────────────────────────────
if all_signals:
    for s in all_signals:
        source = s["source"]
        source_class = {
            "Reddit": "signal-reddit",
            "Hacker News": "signal-hn",
            "YC Community": "signal-yc",
        }.get(source, "signal-yc")

        snippet_html = ""
        if s.get("snippet") and len(s["snippet"]) > 20:
            snippet_html = f'<div class="signal-pain">"{s["snippet"][:240]}..."</div>'

        sub = s.get("subreddit", "")
        sub_html = f' · <span style="color:#6C5CE7">{sub}</span>' if sub else ""
        author_html = f' · by {s["author"]}' if s.get("author") else ""

        created_html = time_ago(s["created"]) if s.get("created") else ""

        tags = tag_for_query(s.get("category", "")) + score_badge(s.get("score", 0))

        st.markdown(f"""
        <div class="signal-card" onclick="window.open('{s['url']}','_blank')">
            <div>
                <span class="signal-source {source_class}">{source}</span>
                {tags}
            </div>
            <div class="signal-title">{s['title']}</div>
            {snippet_html}
            <div class="signal-meta">
                <span>↑ {s['score']} points</span>
                <span>💬 {s['comments']} comments</span>
                <span>{created_html}</span>
                {sub_html}{author_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View & open link"):
            st.markdown(f"[Open on {source} →]({s['url']})")
            if s.get("snippet"):
                st.caption(s["snippet"][:500])
else:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:3rem;margin-bottom:1rem;">🔍</div>
        <div style="font-size:1.1rem;font-weight:600;color:#8A8A9A;">No signals found</div>
        <div style="font-size:0.85rem;color:#5A5A6A;margin-top:0.5rem;">
            Try selecting more sources or refreshing.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Outreach Template ────────────────────────────────────────────────────
st.divider()
st.markdown("### ✉️ Outreach Playbook")
st.markdown("When you find a hot signal, use this template to engage:")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
    **Reddit Comment Template**
    ```
    Hey! We actually built JustPaid to solve exactly this.
    [specific pain they mentioned] is one of the top reasons
    founders come to us.

    Happy to show you how we handle it — no pitch, just
    a quick look if it's useful. DM me!
    ```
    """)
with col_b:
    st.markdown("""
    **HN Reply Template**
    ```
    This is exactly the problem we're solving at JustPaid.
    [their specific pain] comes up constantly — we've built
    [specific feature] to handle it.

    Would love your feedback if you want to take a look:
    justpaid.io
    ```
    """)
