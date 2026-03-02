import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config.settings import BRAND, PLATFORM_COLORS
from utils.metrics import format_number
from utils.charts import follower_growth_chart

st.set_page_config(
    page_title="Cross-Platform | JustPaid Analytics",
    page_icon="https://justpaid.io/favicon.ico",
    layout="wide",
)

with st.sidebar:
    days = st.selectbox(
        "Time Range",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days",
        key="cp_days",
    )
    if st.button("Refresh", use_container_width=True, key="cp_refresh"):
        st.cache_data.clear()
        st.rerun()


@st.cache_data(ttl=3600)
def load_all_metrics(days_back):
    try:
        from storage.bigquery_client import get_channel_metrics, get_latest_metrics_per_platform
        history = get_channel_metrics(days=days_back)
        latest = get_latest_metrics_per_platform()
        return history, latest
    except Exception:
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data(ttl=3600)
def load_all_posts(days_back):
    try:
        from storage.bigquery_client import get_posts
        return get_posts(days=days_back, limit=100)
    except Exception:
        return pd.DataFrame()


history_df, latest_df = load_all_metrics(days)
posts_df = load_all_posts(days)

st.markdown("""
<div style="padding: 1rem 0 0.5rem;">
    <span style="font-size: 1.4rem; font-weight: 800;">
        <span style="background: linear-gradient(135deg, #6C5CE7, #00CEC9);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Cross-Platform</span>
    </span>
    <span style="font-size: 1.4rem; font-weight: 800; color: #E2E2EA;"> Comparison</span>
</div>
<div style="color: #8A8A9A; font-size: 0.85rem; margin-bottom: 1.5rem;">
    Side-by-side performance analysis across all platforms
</div>
""", unsafe_allow_html=True)

if latest_df.empty:
    st.info(
        "No cross-platform data available yet. "
        "Start by setting up at least one platform collector."
    )
    st.stop()

# ============ Total Audience ============

total_followers = int(latest_df["followers"].sum()) if "followers" in latest_df.columns else 0
platforms_active = len(latest_df)

st.markdown(f"""
<div style="background: linear-gradient(135deg, rgba(108,92,231,0.1), rgba(0,206,201,0.1));
            border: 1px solid rgba(108,92,231,0.2); border-radius: 16px;
            padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;">
    <div style="font-size: 0.7rem; color: #8A8A9A; text-transform: uppercase;
                letter-spacing: 1.5px; margin-bottom: 0.5rem;">Total Audience</div>
    <div style="font-size: 2.5rem; font-weight: 800; color: #E2E2EA;">
        {format_number(total_followers)}
    </div>
    <div style="font-size: 0.8rem; color: #A29BFE;">{platforms_active} active platforms</div>
</div>
""", unsafe_allow_html=True)

# ============ Combined Follower Growth ============

st.markdown("#### Combined Follower Growth")
fig = follower_growth_chart(history_df, title="")
st.plotly_chart(fig, use_container_width=True)

# ============ Platform Comparison Table ============

st.markdown("#### Platform Comparison")

if not latest_df.empty:
    comparison_data = []
    for _, row in latest_df.iterrows():
        platform = row.get("platform", "Unknown")
        comparison_data.append({
            "Platform": platform,
            "Followers": format_number(int(row.get("followers", 0))),
            "Posts": format_number(int(row.get("total_posts", 0))),
            "Engagement Rate": f"{row.get('engagement_rate', 0):.2f}%",
            "Total Likes": format_number(int(row.get("total_likes", 0))),
            "Total Comments": format_number(int(row.get("total_comments", 0))),
        })

    comp_df = pd.DataFrame(comparison_data)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

# ============ Growth Velocity ============

st.markdown("#### Growth Velocity (Followers Over Time)")

if not history_df.empty and "platform" in history_df.columns:
    # Calculate growth rate per platform
    growth_data = []
    for platform in history_df["platform"].unique():
        pdf = history_df[history_df["platform"] == platform].sort_values("date")
        if len(pdf) >= 2:
            first = int(pdf.iloc[0].get("followers", 0))
            last = int(pdf.iloc[-1].get("followers", 0))
            change = last - first
            days_span = (pd.to_datetime(pdf["date"].iloc[-1]) - pd.to_datetime(pdf["date"].iloc[0])).days or 1
            daily_rate = change / days_span

            growth_data.append({
                "Platform": platform,
                "Start": format_number(first),
                "Current": format_number(last),
                "Net Change": f"+{format_number(change)}" if change >= 0 else format_number(change),
                "Daily Rate": f"{daily_rate:+.1f}/day",
            })

    if growth_data:
        growth_df = pd.DataFrame(growth_data)
        st.dataframe(growth_df, use_container_width=True, hide_index=True)
    else:
        st.info("Need at least 2 data points per platform to calculate growth velocity.")
else:
    st.info("Not enough historical data for growth velocity analysis.")

# ============ Engagement Benchmarks ============

st.markdown("#### Engagement Benchmarks")

if not latest_df.empty and "engagement_rate" in latest_df.columns:
    platforms = latest_df["platform"].tolist()
    rates = latest_df["engagement_rate"].tolist()
    colors = [PLATFORM_COLORS.get(p, BRAND["primary"]) for p in platforms]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=platforms,
        y=rates,
        marker_color=colors,
        text=[f"{r:.2f}%" for r in rates],
        textposition="outside",
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=BRAND["text"]),
        margin=dict(l=40, r=20, t=20, b=40),
        yaxis_title="Engagement Rate (%)",
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No engagement data available yet.")

# ============ Top Content Across All Platforms ============

st.markdown("#### Top Content Across All Platforms")

if not posts_df.empty:
    top_all = posts_df.sort_values("views", ascending=False).head(10).reset_index(drop=True)
    top_all.index = top_all.index + 1
    cols = [c for c in ["platform", "title", "post_type", "views", "likes", "comments"] if c in top_all.columns]
    st.dataframe(
        top_all[cols].rename(columns={
            "platform": "Platform", "title": "Content", "post_type": "Type",
            "views": "Views", "likes": "Likes", "comments": "Comments",
        }),
        use_container_width=True,
    )
else:
    st.info("No content data available yet.")
