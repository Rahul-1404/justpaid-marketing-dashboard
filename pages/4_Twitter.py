import streamlit as st
import pandas as pd
from config.settings import BRAND, PLATFORM_COLORS
from utils.metrics import format_number
from utils.charts import (
    follower_growth_chart,
    posting_frequency_chart,
)

st.set_page_config(
    page_title="X/Twitter | JustPaid Analytics",
    page_icon="https://justpaid.io/favicon.ico",
    layout="wide",
)

with st.sidebar:
    days = st.selectbox(
        "Time Range",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days",
        key="tw_days",
    )
    if st.button("Refresh", use_container_width=True, key="tw_refresh"):
        st.cache_data.clear()
        st.rerun()


@st.cache_data(ttl=3600)
def load_tw_metrics(days_back):
    try:
        from storage.bigquery_client import get_channel_metrics
        return get_channel_metrics(platform="Twitter", days=days_back)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_tw_posts(days_back):
    try:
        from storage.bigquery_client import get_posts
        return get_posts(platform="Twitter", days=days_back, limit=50)
    except Exception:
        return pd.DataFrame()


metrics_df = load_tw_metrics(days)
posts_df = load_tw_posts(days)

tw_color = PLATFORM_COLORS["Twitter"]
st.markdown(f"""
<div style="padding: 1rem 0 0.5rem;">
    <span style="font-size: 1.4rem; font-weight: 800; color: {tw_color};">X / Twitter</span>
    <span style="font-size: 1.4rem; font-weight: 800; color: #E2E2EA;"> Analytics</span>
</div>
""", unsafe_allow_html=True)

if metrics_df.empty and posts_df.empty:
    st.warning(
        "**Phase 3** — X/Twitter data comes from manual Google Sheet entry.\n\n"
        "Since the free X API tier doesn't include read access, we use a Google Sheet:\n\n"
        "1. Create a Google Sheet with columns: `date`, `followers`, `tweet_id`, `text`, "
        "`impressions`, `likes`, `replies`, `retweets`, `url`\n"
        "2. Share it with your service account email\n"
        "3. Add `TWITTER_SHEET_ID` to `.env`\n\n"
        "**Tip:** Use X Analytics export (analytics.twitter.com) to bulk-fill the sheet."
    )
    st.stop()

# KPI Row
if not metrics_df.empty:
    latest = metrics_df.iloc[-1]
    prev = metrics_df.iloc[-2] if len(metrics_df) > 1 else latest

    kpi_cols = st.columns(4)
    kpis = [
        ("Followers", int(latest.get("followers", 0)), int(prev.get("followers", 0))),
        ("Impressions", int(latest.get("total_views", 0)), int(prev.get("total_views", 0))),
        ("Likes", int(latest.get("total_likes", 0)), int(prev.get("total_likes", 0))),
        ("Engagement", latest.get("engagement_rate", 0), prev.get("engagement_rate", 0)),
    ]

    for i, (label, current, previous) in enumerate(kpis):
        with kpi_cols[i]:
            display = f"{current:.2f}%" if label == "Engagement" else format_number(current)
            st.markdown(f"""
            <div style="background: #1A1D29; border: 1px solid rgba(255,255,255,0.06);
                        border-radius: 14px; padding: 1rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #8A8A9A; text-transform: uppercase;
                            letter-spacing: 1.2px; margin-bottom: 0.4rem;">{label}</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #E2E2EA;">{display}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Follower Growth")
    fig = follower_growth_chart(metrics_df, title="")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("#### Posting Frequency")
    fig = posting_frequency_chart(posts_df)
    st.plotly_chart(fig, use_container_width=True)

# Top Tweets
st.markdown("#### Top Tweets")
if not posts_df.empty:
    display_df = posts_df.sort_values("views", ascending=False).head(10).reset_index(drop=True)
    display_df.index = display_df.index + 1
    cols = [c for c in ["title", "views", "likes", "comments", "shares"] if c in display_df.columns]
    st.dataframe(
        display_df[cols].rename(columns={
            "title": "Tweet", "views": "Impressions",
            "likes": "Likes", "comments": "Replies", "shares": "Retweets",
        }),
        use_container_width=True,
    )
else:
    st.info("No tweet data available yet.")
