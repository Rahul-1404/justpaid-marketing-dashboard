import streamlit as st
import pandas as pd
from config.settings import BRAND, PLATFORM_COLORS
from utils.metrics import format_number
from utils.charts import (
    follower_growth_chart,
    content_type_breakdown,
    posting_frequency_chart,
)

st.set_page_config(
    page_title="Instagram | JustPaid Analytics",
    page_icon="https://justpaid.io/favicon.ico",
    layout="wide",
)

with st.sidebar:
    days = st.selectbox(
        "Time Range",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days",
        key="ig_days",
    )
    if st.button("Refresh", use_container_width=True, key="ig_refresh"):
        st.cache_data.clear()
        st.rerun()


@st.cache_data(ttl=3600)
def load_ig_metrics(days_back):
    try:
        from storage.bigquery_client import get_channel_metrics
        return get_channel_metrics(platform="Instagram", days=days_back)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_ig_posts(days_back):
    try:
        from storage.bigquery_client import get_posts
        return get_posts(platform="Instagram", days=days_back, limit=50)
    except Exception:
        return pd.DataFrame()


metrics_df = load_ig_metrics(days)
posts_df = load_ig_posts(days)

ig_color = PLATFORM_COLORS["Instagram"]
st.markdown(f"""
<div style="padding: 1rem 0 0.5rem;">
    <span style="font-size: 1.4rem; font-weight: 800; color: {ig_color};">Instagram</span>
    <span style="font-size: 1.4rem; font-weight: 800; color: #E2E2EA;"> Analytics</span>
</div>
""", unsafe_allow_html=True)

if metrics_df.empty and posts_df.empty:
    st.warning(
        "**Phase 2** — Instagram data collection requires Meta Graph API setup.\n\n"
        "1. Create an app at [developers.facebook.com](https://developers.facebook.com)\n"
        "2. Connect your Instagram Business account\n"
        "3. Add `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_BUSINESS_ACCOUNT_ID` to `.env`"
    )
    st.stop()

# KPI Row
if not metrics_df.empty:
    latest = metrics_df.iloc[-1]
    prev = metrics_df.iloc[-2] if len(metrics_df) > 1 else latest

    kpi_cols = st.columns(4)
    kpis = [
        ("Followers", int(latest.get("followers", 0)), int(prev.get("followers", 0))),
        ("Posts", int(latest.get("total_posts", 0)), int(prev.get("total_posts", 0))),
        ("Likes", int(latest.get("total_likes", 0)), int(prev.get("total_likes", 0))),
        ("Engagement", latest.get("engagement_rate", 0), prev.get("engagement_rate", 0)),
    ]

    for i, (label, current, previous) in enumerate(kpis):
        with kpi_cols[i]:
            display = f"{current:.2f}%" if label == "Engagement" else format_number(current)
            diff = current - previous
            delta_color = BRAND["success"] if diff > 0 else BRAND["danger"] if diff < 0 else BRAND["text_muted"]

            st.markdown(f"""
            <div style="background: #1A1D29; border: 1px solid rgba(255,255,255,0.06);
                        border-radius: 14px; padding: 1rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #8A8A9A; text-transform: uppercase;
                            letter-spacing: 1.2px; margin-bottom: 0.4rem;">{label}</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #E2E2EA;">{display}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

# Charts
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Follower Growth")
    fig = follower_growth_chart(metrics_df, title="")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("#### Content Breakdown (Reels vs Posts)")
    fig = content_type_breakdown(posts_df, platform="Instagram")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Posting Frequency")
fig = posting_frequency_chart(posts_df)
st.plotly_chart(fig, use_container_width=True)

# Top Posts
st.markdown("#### Top Posts")
if not posts_df.empty:
    display_df = posts_df.sort_values("likes", ascending=False).head(10).reset_index(drop=True)
    display_df.index = display_df.index + 1
    cols = [c for c in ["title", "post_type", "likes", "comments", "published_at"] if c in display_df.columns]
    st.dataframe(
        display_df[cols].rename(columns={
            "title": "Caption", "post_type": "Type", "likes": "Likes",
            "comments": "Comments", "published_at": "Published",
        }),
        use_container_width=True,
    )
else:
    st.info("No post data available yet.")
