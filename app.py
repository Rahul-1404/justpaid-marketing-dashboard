import streamlit as st
import pandas as pd
from config.settings import BRAND, PLATFORM_COLORS
from utils.metrics import format_number, delta_indicator
from utils.charts import (
    follower_growth_chart,
    engagement_comparison_chart,
    top_posts_table,
)

# ============ Page Config ============

st.set_page_config(
    page_title="JustPaid Social Analytics",
    page_icon="https://justpaid.io/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ Styling ============

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: #0E1117; }
    header[data-testid="stHeader"] { background: transparent; }

    section[data-testid="stSidebar"] {
        background: #1A1D29;
        border-right: 1px solid rgba(255,255,255,0.04);
    }

    .brand-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
    }
    .brand-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #E2E2EA;
        letter-spacing: -0.5px;
    }
    .brand-title span {
        background: linear-gradient(135deg, #6C5CE7, #A29BFE, #00CEC9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-subtitle {
        color: #8A8A9A;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }

    .kpi-card {
        background: #1A1D29;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        text-align: center;
        transition: all 0.2s;
    }
    .kpi-card:hover {
        border-color: rgba(108,92,231,0.3);
        box-shadow: 0 4px 20px rgba(108,92,231,0.08);
    }
    .kpi-platform {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.5rem;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #E2E2EA;
        margin-bottom: 0.3rem;
    }
    .kpi-delta {
        font-size: 0.78rem;
        font-weight: 600;
    }
    .kpi-label {
        font-size: 0.68rem;
        color: #8A8A9A;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.4rem;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #E2E2EA;
        margin: 2rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .empty-state {
        text-align: center;
        padding: 4rem 0;
    }
    .empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }
    .empty-title { color: #8A8A9A; font-size: 1.1rem; font-weight: 600; }
    .empty-desc { color: #5A5A6A; font-size: 0.85rem; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ============ Sidebar ============

with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #E2E2EA;">
            <span style="background: linear-gradient(135deg, #6C5CE7, #00CEC9);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            JustPaid</span> Analytics
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    days = st.selectbox(
        "Time Range",
        options=[7, 14, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Last {x} days",
    )

    st.divider()

    st.caption("Auto-refreshes every 24 hours")
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ============ Data Loading ============


@st.cache_data(ttl=3600)
def load_metrics(days_back):
    try:
        from storage.bigquery_client import get_latest_metrics_per_platform
        return get_latest_metrics_per_platform()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_follower_history(days_back):
    try:
        from storage.bigquery_client import get_channel_metrics
        return get_channel_metrics(days=days_back)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def load_top_posts():
    try:
        from storage.bigquery_client import get_top_posts_all_platforms
        return get_top_posts_all_platforms(limit=5)
    except Exception:
        return pd.DataFrame()


metrics_df = load_metrics(days)
history_df = load_follower_history(days)
top_posts_df = load_top_posts()

# ============ Header ============

st.markdown("""
<div class="brand-header">
    <div class="brand-title">Social Media <span>Analytics</span></div>
    <div class="brand-subtitle">Real-time performance tracking across all platforms</div>
</div>
""", unsafe_allow_html=True)

# ============ KPI Cards ============

if not metrics_df.empty:
    st.markdown('<div class="section-title">Platform Overview</div>', unsafe_allow_html=True)

    platform_order = ["YouTube", "Instagram", "LinkedIn", "Twitter"]
    cols = st.columns(4)

    for i, platform in enumerate(platform_order):
        row = metrics_df[metrics_df["platform"] == platform]
        with cols[i]:
            if not row.empty:
                r = row.iloc[0]
                raw_followers = r.get("followers", 0)
                followers = 0 if pd.isna(raw_followers) else int(raw_followers)
                raw_change = r.get("follower_change", 0)
                change = 0 if pd.isna(raw_change) else int(raw_change)
                color = PLATFORM_COLORS.get(platform, BRAND["primary"])

                if change > 0:
                    delta_text = f"+{format_number(change)}"
                    delta_color = BRAND["success"]
                elif change < 0:
                    delta_text = f"-{format_number(abs(change))}"
                    delta_color = BRAND["danger"]
                else:
                    delta_text = "0"
                    delta_color = BRAND["text_muted"]

                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-platform" style="color: {color};">{platform}</div>
                    <div class="kpi-value">{format_number(followers)}</div>
                    <div class="kpi-delta" style="color: {delta_color};">{delta_text}</div>
                    <div class="kpi-label">Followers</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-platform" style="color: {PLATFORM_COLORS.get(platform, '#8A8A9A')};">
                        {platform}
                    </div>
                    <div class="kpi-value">--</div>
                    <div class="kpi-delta" style="color: #8A8A9A;">No data</div>
                    <div class="kpi-label">Followers</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("")

    # ============ Charts ============

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-title">Follower Growth</div>', unsafe_allow_html=True)
        fig = follower_growth_chart(history_df)
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">Engagement Rate</div>', unsafe_allow_html=True)
        fig = engagement_comparison_chart(metrics_df)
        st.plotly_chart(fig, use_container_width=True)

    # ============ Top Posts ============

    st.markdown('<div class="section-title">Top Performing Content</div>', unsafe_allow_html=True)
    fig = top_posts_table(top_posts_df)
    st.plotly_chart(fig, use_container_width=True)

else:
    # Empty state — no data yet
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📊</div>
        <div class="empty-title">No data yet</div>
        <div class="empty-desc">
            Run the data collector to start populating your dashboard.<br>
            <code>python -c "from collectors.youtube_collector import collect_all; print(collect_all())"</code>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "**Quick start:** Set your `YOUTUBE_API_KEY` and `YOUTUBE_CHANNEL_ID` "
        "in `.env`, then run the collector to see data here."
    )
