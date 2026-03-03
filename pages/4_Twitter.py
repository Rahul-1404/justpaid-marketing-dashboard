import streamlit as st
import pandas as pd
from config.settings import BRAND, PLATFORM_COLORS
from utils.metrics import (
    format_number,
    current_and_previous_quarter, quarter_boundaries, quarter_label,
    compute_quarter_stats,
)
from utils.charts import (
    follower_growth_chart,
    posting_frequency_chart,
    qoq_growth_chart,
    qoq_comparison_bars,
    qoq_avg_performance_bars,
    qoq_content_mix_comparison,
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

# ============ Quarter-over-Quarter Comparison ============


@st.cache_data(ttl=3600)
def load_tw_qoq():
    try:
        from storage.bigquery_client import get_posts_by_date_range
        (cy, cq), (py, pq) = current_and_previous_quarter()
        cs, ce = quarter_boundaries(cy, cq)
        ps, pe = quarter_boundaries(py, pq)
        curr_df = get_posts_by_date_range(cs, ce, platform="Twitter")
        prev_df = get_posts_by_date_range(ps, pe, platform="Twitter")
        return curr_df, prev_df, quarter_label(cy, cq), quarter_label(py, pq)
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), "", ""


qoq_curr, qoq_prev, curr_lbl, prev_lbl = load_tw_qoq()
has_both = not qoq_curr.empty and not qoq_prev.empty
has_any = not qoq_curr.empty or not qoq_prev.empty

if has_any:
    if has_both:
        section_title = f"Quarter-over-Quarter: {curr_lbl} vs {prev_lbl}"
    else:
        active_lbl = curr_lbl if not qoq_curr.empty else prev_lbl
        section_title = f"{active_lbl} Quarter Summary"

    st.markdown(f"""
    <div style="padding: 1.5rem 0 0.5rem;">
        <span style="font-size: 1.2rem; font-weight: 800; color: {tw_color};">{section_title}</span>
    </div>
    """, unsafe_allow_html=True)

    curr_stats = compute_quarter_stats(qoq_curr)
    prev_stats = compute_quarter_stats(qoq_prev)

    qoq_metrics = [
        ("Posts Published", "total_posts", False),
        ("Total Impressions", "total_views", False),
        ("Total Likes", "total_likes", False),
        ("Engagement Rate", "engagement_rate", True),
    ]

    qoq_cols = st.columns(4)
    for i, (label, key, is_pct) in enumerate(qoq_metrics):
        with qoq_cols[i]:
            curr_val = curr_stats[key]
            prev_val = prev_stats[key]
            if is_pct:
                curr_display = f"{curr_val:.2f}%"
                prev_display = f"{prev_val:.2f}%"
                diff = curr_val - prev_val
                diff_display = f"{diff:+.2f}%"
            else:
                curr_display = format_number(curr_val)
                prev_display = format_number(prev_val)
                diff = curr_val - prev_val
                diff_display = f"{(diff / prev_val * 100):+.0f}%" if prev_val > 0 else "New"

            if has_both:
                if diff > 0:
                    delta_color = BRAND["success"]
                    arrow = "^"
                elif diff < 0:
                    delta_color = BRAND["danger"]
                    arrow = "v"
                else:
                    delta_color = BRAND["text_muted"]
                    arrow = ""

                st.markdown(f"""
                <div style="background: #1A1D29; border: 1px solid rgba(255,255,255,0.06);
                            border-radius: 14px; padding: 1rem; text-align: center;">
                    <div style="font-size: 0.65rem; color: #8A8A9A; text-transform: uppercase;
                                letter-spacing: 1.2px; margin-bottom: 0.3rem;">{label}</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #E2E2EA;">{curr_display}</div>
                    <div style="font-size: 0.7rem; font-weight: 600; color: {delta_color};">
                        {arrow} {diff_display} vs {prev_lbl}
                    </div>
                    <div style="font-size: 0.6rem; color: #5A5A6A; margin-top: 0.3rem;">
                        {prev_lbl}: {prev_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                solo_val = curr_display if not qoq_curr.empty else prev_display
                st.markdown(f"""
                <div style="background: #1A1D29; border: 1px solid rgba(255,255,255,0.06);
                            border-radius: 14px; padding: 1rem; text-align: center;">
                    <div style="font-size: 0.65rem; color: #8A8A9A; text-transform: uppercase;
                                letter-spacing: 1.2px; margin-bottom: 0.3rem;">{label}</div>
                    <div style="font-size: 1.3rem; font-weight: 800; color: #E2E2EA;">{solo_val}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("")

    if has_both:
        fig = qoq_growth_chart(curr_stats, prev_stats, curr_lbl, prev_lbl,
                               platform_color=tw_color)
        st.plotly_chart(fig, use_container_width=True)

        col_left, col_right = st.columns(2)
        with col_left:
            fig = qoq_comparison_bars(curr_stats, prev_stats, curr_lbl, prev_lbl)
            st.plotly_chart(fig, use_container_width=True)
        with col_right:
            fig = qoq_avg_performance_bars(curr_stats, prev_stats, curr_lbl, prev_lbl)
            st.plotly_chart(fig, use_container_width=True)

        fig = qoq_content_mix_comparison(qoq_curr, qoq_prev, curr_lbl, prev_lbl)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Top Performers by Quarter")
        tcol_left, tcol_right = st.columns(2)
        with tcol_left:
            st.markdown(f"**{curr_lbl}**")
            if not qoq_curr.empty:
                top_curr = qoq_curr.sort_values("views", ascending=False).head(5).reset_index(drop=True)
                top_curr.index = top_curr.index + 1
                cols_show = [c for c in ["title", "views", "likes", "comments", "shares"] if c in top_curr.columns]
                st.dataframe(top_curr[cols_show].rename(columns={
                    "title": "Tweet", "views": "Impressions",
                    "likes": "Likes", "comments": "Replies", "shares": "Retweets",
                }), use_container_width=True)
        with tcol_right:
            st.markdown(f"**{prev_lbl}**")
            if not qoq_prev.empty:
                top_prev = qoq_prev.sort_values("views", ascending=False).head(5).reset_index(drop=True)
                top_prev.index = top_prev.index + 1
                cols_show = [c for c in ["title", "views", "likes", "comments", "shares"] if c in top_prev.columns]
                st.dataframe(top_prev[cols_show].rename(columns={
                    "title": "Tweet", "views": "Impressions",
                    "likes": "Likes", "comments": "Replies", "shares": "Retweets",
                }), use_container_width=True)
    else:
        active_df = qoq_curr if not qoq_curr.empty else qoq_prev
        active_label = curr_lbl if not qoq_curr.empty else prev_lbl
        missing_label = prev_lbl if not qoq_curr.empty else curr_lbl

        st.markdown(f"#### Top Performers — {active_label}")
        top_df = active_df.sort_values("views", ascending=False).head(5).reset_index(drop=True)
        top_df.index = top_df.index + 1
        cols_show = [c for c in ["title", "views", "likes", "comments", "shares"] if c in top_df.columns]
        st.dataframe(top_df[cols_show].rename(columns={
            "title": "Tweet", "views": "Impressions",
            "likes": "Likes", "comments": "Replies", "shares": "Retweets",
        }), use_container_width=True)

        st.info(f"No data available for {missing_label}. QoQ comparison charts will appear once both quarters have data.")
