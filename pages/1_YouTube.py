import streamlit as st
import pandas as pd
from config.settings import BRAND, PLATFORM_COLORS
from utils.metrics import format_number, calculate_posting_frequency
from utils.charts import (
    follower_growth_chart,
    content_type_breakdown,
    posting_frequency_chart,
)

st.set_page_config(
    page_title="YouTube | JustPaid Analytics",
    page_icon="https://justpaid.io/favicon.ico",
    layout="wide",
)

# ============ Sidebar ============

with st.sidebar:
    days = st.selectbox(
        "Time Range",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days",
        key="yt_days",
    )
    if st.button("Refresh", use_container_width=True, key="yt_refresh"):
        st.cache_data.clear()
        st.rerun()

# ============ Data Loading ============


@st.cache_data(ttl=3600)
def load_yt_metrics(days_back):
    try:
        from storage.bigquery_client import get_channel_metrics
        return get_channel_metrics(platform="YouTube", days=days_back)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_yt_posts(days_back):
    try:
        from storage.bigquery_client import get_posts
        return get_posts(platform="YouTube", days=days_back, limit=50)
    except Exception:
        return pd.DataFrame()


metrics_df = load_yt_metrics(days)
posts_df = load_yt_posts(days)

# ============ Header ============

yt_color = PLATFORM_COLORS["YouTube"]
st.markdown(f"""
<div style="padding: 1rem 0 0.5rem;">
    <span style="font-size: 1.4rem; font-weight: 800; color: {yt_color};">YouTube</span>
    <span style="font-size: 1.4rem; font-weight: 800; color: #E2E2EA;"> Analytics</span>
</div>
""", unsafe_allow_html=True)

if metrics_df.empty and posts_df.empty:
    st.info(
        "No YouTube data yet. Set `YOUTUBE_API_KEY` and `YOUTUBE_CHANNEL_ID` "
        "in your `.env` file and run the collector."
    )
    st.stop()

# ============ KPI Row ============

if not metrics_df.empty:
    latest = metrics_df.iloc[-1]
    prev = metrics_df.iloc[-2] if len(metrics_df) > 1 else latest

    kpi_cols = st.columns(4)

    kpis = [
        ("Subscribers", int(latest.get("followers", 0)), int(prev.get("followers", 0))),
        ("Total Views", int(latest.get("total_views", 0)), int(prev.get("total_views", 0))),
        ("Engagement", latest.get("engagement_rate", 0), prev.get("engagement_rate", 0)),
        ("Videos", int(latest.get("total_posts", 0)), int(prev.get("total_posts", 0))),
    ]

    for i, (label, current, previous) in enumerate(kpis):
        with kpi_cols[i]:
            if label == "Engagement":
                display = f"{current:.2f}%"
            else:
                display = format_number(current)

            diff = current - previous
            if diff > 0:
                delta_color = BRAND["success"]
                arrow = "+"
            elif diff < 0:
                delta_color = BRAND["danger"]
                arrow = ""
            else:
                delta_color = BRAND["text_muted"]
                arrow = ""

            if label == "Engagement":
                delta_display = f"{arrow}{diff:+.2f}%"
            else:
                delta_display = f"{arrow}{format_number(abs(int(diff)))}"
                if diff < 0:
                    delta_display = f"-{format_number(abs(int(diff)))}"

            st.markdown(f"""
            <div style="background: #1A1D29; border: 1px solid rgba(255,255,255,0.06);
                        border-radius: 14px; padding: 1rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #8A8A9A; text-transform: uppercase;
                            letter-spacing: 1.2px; margin-bottom: 0.4rem;">{label}</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #E2E2EA;">{display}</div>
                <div style="font-size: 0.75rem; font-weight: 600; color: {delta_color};">
                    {delta_display}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

# ============ Charts ============

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Subscriber Growth")
    fig = follower_growth_chart(metrics_df, title="")
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("#### Content Type Breakdown")
    fig = content_type_breakdown(posts_df, platform="YouTube")
    st.plotly_chart(fig, use_container_width=True)

# ============ Posting Frequency ============

st.markdown("#### Posting Frequency")
fig = posting_frequency_chart(posts_df)
st.plotly_chart(fig, use_container_width=True)

# ============ Top Videos Table ============

st.markdown("#### Top Videos")

if not posts_df.empty:
    display_df = (
        posts_df.sort_values("views", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    display_df.index = display_df.index + 1

    cols_to_show = ["title", "post_type", "views", "likes", "comments", "published_at"]
    available_cols = [c for c in cols_to_show if c in display_df.columns]

    st.dataframe(
        display_df[available_cols].rename(
            columns={
                "title": "Title",
                "post_type": "Type",
                "views": "Views",
                "likes": "Likes",
                "comments": "Comments",
                "published_at": "Published",
            }
        ),
        use_container_width=True,
        hide_index=False,
    )

    freq = calculate_posting_frequency(posts_df)
    st.caption(f"Average posting frequency: **{freq} posts/week**")
else:
    st.info("No video data available yet.")
