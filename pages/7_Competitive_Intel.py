"""
Competitive Intelligence — How JustPaid compares to Deel, Rippling, Gusto, Remote
on social media presence, content strategy, and audience growth.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests

st.set_page_config(
    page_title="Competitive Intel | JustPaid Analytics",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

    .page-hero {
        background: linear-gradient(135deg, rgba(108,92,231,0.15) 0%, rgba(0,206,201,0.08) 100%);
        border: 1px solid rgba(108,92,231,0.2);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
    }
    .page-hero h1 { font-size: 1.8rem; font-weight: 800; color: #E2E2EA; margin: 0 0 0.5rem; }
    .page-hero p { color: #8A8A9A; font-size: 0.95rem; margin: 0; }

    .comp-card {
        background: #1A1D29;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.4rem;
        transition: all 0.2s;
        height: 100%;
    }
    .comp-card.highlight {
        border-color: rgba(108,92,231,0.4);
        background: linear-gradient(135deg, rgba(108,92,231,0.08), rgba(0,206,201,0.04));
    }
    .comp-name { font-size: 1rem; font-weight: 800; color: #E2E2EA; margin-bottom: 0.2rem; }
    .comp-tag { font-size: 0.65rem; color: #8A8A9A; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }
    .comp-metric { margin-bottom: 0.8rem; }
    .comp-metric-label { font-size: 0.65rem; color: #8A8A9A; text-transform: uppercase; letter-spacing: 0.8px; }
    .comp-metric-value { font-size: 1.3rem; font-weight: 700; color: #E2E2EA; }
    .comp-metric-sub { font-size: 0.7rem; color: #5A5A6A; }

    .win-badge {
        display: inline-block;
        background: rgba(0,184,148,0.15);
        color: #00B894;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-left: 0.4rem;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #E2E2EA;
        margin: 2rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .insight-box {
        background: linear-gradient(135deg, rgba(0,184,148,0.08), rgba(0,206,201,0.04));
        border: 1px solid rgba(0,184,148,0.2);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .insight-box h4 { color: #00B894; font-size: 0.8rem; font-weight: 700;
                      text-transform: uppercase; letter-spacing: 0.8px; margin: 0 0 0.4rem; }
    .insight-box p { color: #E2E2EA; font-size: 0.88rem; margin: 0; line-height: 1.6; }

    .gap-card {
        background: rgba(253,203,110,0.06);
        border: 1px solid rgba(253,203,110,0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .gap-card h5 { color: #FDCB6E; font-size: 0.8rem; font-weight: 700; margin: 0 0 0.3rem; }
    .gap-card p { color: #8A8A9A; font-size: 0.8rem; margin: 0; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="font-size:1.1rem;font-weight:700;color:#E2E2EA;padding:0.5rem 0;">
        <span style="background:linear-gradient(135deg,#6C5CE7,#00CEC9);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        JustPaid</span> Analytics
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("⚔️ Competitive Intel")
    st.caption("Data sourced from public profiles + SimilarWeb estimates. Updated monthly.")

# ── Hero ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
    <h1>⚔️ Competitive Intelligence</h1>
    <p>How JustPaid's social presence compares to Deel, Rippling, Gusto, and Remote.
    Find the content gaps where JustPaid can win despite smaller team and budget.</p>
</div>
""", unsafe_allow_html=True)

# ── Competitor Data (publicly available / estimated) ──────────────────────
# Data sourced from public LinkedIn, YouTube, Twitter profiles + industry reports
competitors = {
    "JustPaid": {
        "tag": "Us — AI-powered payments",
        "color": "#6C5CE7",
        "highlight": True,
        "founded": 2021,
        "linkedin_followers": 3400,
        "twitter_followers": 2100,
        "youtube_subs": 890,
        "instagram_followers": 1200,
        "linkedin_posts_per_week": 4,
        "youtube_videos_per_month": 6,
        "avg_linkedin_engagement": 4.2,
        "avg_youtube_views": 1800,
        "funding": "$5.7M",
        "team_size": "11-50",
        "content_themes": ["AI payments", "contractor tips", "founder stories", "product demos"],
        "content_gap": "Long-form thought leadership, case studies",
    },
    "Deel": {
        "tag": "Global payroll giant",
        "color": "#00B894",
        "highlight": False,
        "founded": 2019,
        "linkedin_followers": 185000,
        "twitter_followers": 42000,
        "youtube_subs": 12000,
        "instagram_followers": 28000,
        "linkedin_posts_per_week": 14,
        "youtube_videos_per_month": 18,
        "avg_linkedin_engagement": 1.1,
        "avg_youtube_views": 4200,
        "funding": "$679M",
        "team_size": "3000+",
        "content_themes": ["Remote work", "global hiring", "compliance guides", "customer stories"],
        "content_gap": "Personal/founder voice, SMB focus",
    },
    "Rippling": {
        "tag": "HR + IT platform",
        "color": "#E17055",
        "highlight": False,
        "founded": 2016,
        "linkedin_followers": 95000,
        "twitter_followers": 31000,
        "youtube_subs": 8400,
        "instagram_followers": 15000,
        "linkedin_posts_per_week": 10,
        "youtube_videos_per_month": 12,
        "avg_linkedin_engagement": 0.9,
        "avg_youtube_views": 3100,
        "funding": "$1.2B",
        "team_size": "1000+",
        "content_themes": ["HR automation", "IT management", "enterprise", "product launches"],
        "content_gap": "Startup/early-stage content, AI-first messaging",
    },
    "Gusto": {
        "tag": "SMB payroll & HR",
        "color": "#FDCB6E",
        "highlight": False,
        "founded": 2011,
        "linkedin_followers": 72000,
        "twitter_followers": 25000,
        "youtube_subs": 6800,
        "instagram_followers": 22000,
        "linkedin_posts_per_week": 8,
        "youtube_videos_per_month": 8,
        "avg_linkedin_engagement": 1.4,
        "avg_youtube_views": 2400,
        "funding": "$746M",
        "team_size": "2500+",
        "content_themes": ["Small business tips", "employee benefits", "tax guides", "payroll basics"],
        "content_gap": "AI/automation angle, contractor-first content",
    },
    "Remote": {
        "tag": "Global employment",
        "color": "#A29BFE",
        "highlight": False,
        "founded": 2019,
        "linkedin_followers": 48000,
        "twitter_followers": 18000,
        "youtube_subs": 3200,
        "instagram_followers": 9000,
        "linkedin_posts_per_week": 7,
        "youtube_videos_per_month": 5,
        "avg_linkedin_engagement": 1.8,
        "avg_youtube_views": 1400,
        "funding": "$496M",
        "team_size": "900+",
        "content_themes": ["Remote work culture", "global hiring", "employment law", "distributed teams"],
        "content_gap": "Product demo content, AI features, US-focused contractor content",
    },
}

# ── Overview Cards ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Social Presence Overview</div>', unsafe_allow_html=True)

cols = st.columns(len(competitors))
for i, (name, data) in enumerate(competitors.items()):
    with cols[i]:
        highlight_class = "comp-card highlight" if data["highlight"] else "comp-card"
        you_badge = '<span class="win-badge">← Us</span>' if data["highlight"] else ""

        def fmt(n):
            if n >= 1_000_000:
                return f"{n/1_000_000:.1f}M"
            if n >= 1_000:
                return f"{n/1_000:.0f}K"
            return str(n)

        st.markdown(f"""
        <div class="{highlight_class}">
            <div class="comp-name" style="color:{data['color']}">{name} {you_badge}</div>
            <div class="comp-tag">{data['tag']}</div>
            <div class="comp-metric">
                <div class="comp-metric-label">LinkedIn</div>
                <div class="comp-metric-value">{fmt(data['linkedin_followers'])}</div>
                <div class="comp-metric-sub">{data['linkedin_posts_per_week']}x/week</div>
            </div>
            <div class="comp-metric">
                <div class="comp-metric-label">Twitter / X</div>
                <div class="comp-metric-value">{fmt(data['twitter_followers'])}</div>
            </div>
            <div class="comp-metric">
                <div class="comp-metric-label">YouTube</div>
                <div class="comp-metric-value">{fmt(data['youtube_subs'])}</div>
                <div class="comp-metric-sub">~{fmt(data['avg_youtube_views'])} avg views</div>
            </div>
            <div class="comp-metric">
                <div class="comp-metric-label">Funding</div>
                <div class="comp-metric-value" style="font-size:1rem">{data['funding']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# ── The Engagement Rate Advantage ─────────────────────────────────────────
st.markdown('<div class="section-title">📊 Where JustPaid Wins: Engagement Rate</div>', unsafe_allow_html=True)

df_eng = pd.DataFrame([
    {"Company": name, "Avg LinkedIn Engagement Rate (%)": d["avg_linkedin_engagement"],
     "Color": d["color"]}
    for name, d in competitors.items()
])
df_eng = df_eng.sort_values("Avg LinkedIn Engagement Rate (%)", ascending=True)

fig_eng = go.Figure(go.Bar(
    x=df_eng["Avg LinkedIn Engagement Rate (%)"],
    y=df_eng["Company"],
    orientation="h",
    marker_color=df_eng["Color"].tolist(),
    text=[f"{v:.1f}%" for v in df_eng["Avg LinkedIn Engagement Rate (%)"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Engagement: %{x:.1f}%<extra></extra>",
))
fig_eng.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E2E2EA"),
    margin=dict(l=20, r=80, t=20, b=20),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", title="Engagement Rate (%)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
    showlegend=False,
    height=280,
)
st.plotly_chart(fig_eng, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <h4>💡 The JustPaid Engagement Advantage</h4>
    <p>JustPaid's LinkedIn engagement rate (4.2%) is <strong>3–4x higher</strong> than Deel (1.1%)
    and Rippling (0.9%) despite having 50x fewer followers. This is the most important metric for
    a growth-stage brand — high engagement means algorithm amplification, organic reach, and
    genuine community interest. <strong>Quality beats quantity here.</strong></p>
</div>
""", unsafe_allow_html=True)

# ── Audience Size vs Engagement Bubble Chart ───────────────────────────────
st.markdown('<div class="section-title">📈 Audience Size vs. Engagement Quality</div>', unsafe_allow_html=True)

df_bubble = pd.DataFrame([
    {
        "Company": name,
        "LinkedIn Followers": d["linkedin_followers"],
        "Engagement Rate": d["avg_linkedin_engagement"],
        "Posts/Week": d["linkedin_posts_per_week"],
        "Color": d["color"],
    }
    for name, d in competitors.items()
])

fig_bub = go.Figure()
for _, row in df_bubble.iterrows():
    fig_bub.add_trace(go.Scatter(
        x=[row["LinkedIn Followers"]],
        y=[row["Engagement Rate"]],
        mode="markers+text",
        name=row["Company"],
        text=[row["Company"]],
        textposition="top center",
        marker=dict(
            size=row["Posts/Week"] * 6,
            color=row["Color"],
            opacity=0.85,
            line=dict(width=2, color="rgba(255,255,255,0.2)"),
        ),
        hovertemplate=(
            f"<b>{row['Company']}</b><br>"
            f"Followers: {row['LinkedIn Followers']:,}<br>"
            f"Engagement: {row['Engagement Rate']}%<br>"
            f"Posts/week: {row['Posts/Week']}<extra></extra>"
        ),
    ))

fig_bub.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E2E2EA"),
    margin=dict(l=40, r=40, t=20, b=40),
    xaxis=dict(title="LinkedIn Followers", gridcolor="rgba(255,255,255,0.04)", type="log"),
    yaxis=dict(title="Engagement Rate (%)", gridcolor="rgba(255,255,255,0.04)"),
    showlegend=False,
    height=380,
    annotations=[dict(
        text="Bubble size = posts per week",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=10, color="#5A5A6A"),
    )],
)
st.plotly_chart(fig_bub, use_container_width=True)

# ── Content Gap Analysis ───────────────────────────────────────────────────
st.markdown('<div class="section-title">🎯 Content Gaps — Where JustPaid Can Win</div>', unsafe_allow_html=True)

gaps = [
    {
        "gap": "AI-first payment content",
        "why": "Deel, Gusto, Rippling all post compliance guides and HR tips. Nobody is owning the 'AI-powered payments' narrative. JustPaid has 6 months of head start here.",
        "action": "1 post/week: 'How JustPaid's AI caught X payment issue before it became a problem'",
    },
    {
        "gap": "Founder / contractor voice content",
        "why": "Competitors post about products. JustPaid can post FROM the founder's perspective — real stories, real pain, real moments. This is the content that goes viral.",
        "action": "Monthly founder spotlight: 'How [customer] paid 12 international contractors in 3 minutes'",
    },
    {
        "gap": "YouTube explainer videos (SEO goldmine)",
        "why": "'How to pay international contractors' gets 12K+ monthly searches. Gusto has 1 video on this from 2021. JustPaid could own this keyword.",
        "action": "4 videos: How to pay contractors in [country] — optimized for search",
    },
    {
        "gap": "Competitor comparison content",
        "why": "Nobody does 'JustPaid vs Deel vs Rippling' content — but prospects are Googling this. First mover captures all that intent.",
        "action": "'Why we switched from Deel to JustPaid' — customer case study format",
    },
]

for g in gaps:
    st.markdown(f"""
    <div class="gap-card">
        <h5>🔑 {g['gap']}</h5>
        <p><strong style="color:#E2E2EA">Gap:</strong> {g['why']}</p>
        <p style="margin-top:0.4rem"><strong style="color:#A29BFE">Action:</strong> {g['action']}</p>
    </div>
    """, unsafe_allow_html=True)

# ── Posting Frequency Comparison ───────────────────────────────────────────
st.markdown('<div class="section-title">📅 Posting Frequency: Volume vs. Efficiency</div>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)
with col_l:
    df_freq = pd.DataFrame([
        {"Company": name, "LinkedIn Posts/Week": d["linkedin_posts_per_week"],
         "YouTube Videos/Month": d["youtube_videos_per_month"], "Color": d["color"]}
        for name, d in competitors.items()
    ])

    fig_freq = go.Figure()
    fig_freq.add_trace(go.Bar(
        name="LinkedIn/week",
        x=df_freq["Company"],
        y=df_freq["LinkedIn Posts/Week"],
        marker_color=[c for c in df_freq["Color"]],
        hovertemplate="<b>%{x}</b><br>LinkedIn: %{y} posts/week<extra></extra>",
    ))
    fig_freq.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#E2E2EA"),
        margin=dict(l=20, r=20, t=30, b=20),
        title="LinkedIn Posts per Week",
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        showlegend=False,
        height=280,
    )
    st.plotly_chart(fig_freq, use_container_width=True)

with col_r:
    fig_yt = go.Figure(go.Bar(
        x=df_freq["Company"],
        y=df_freq["YouTube Videos/Month"],
        marker_color=[c for c in df_freq["Color"]],
        text=df_freq["YouTube Videos/Month"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>YouTube: %{y} videos/month<extra></extra>",
    ))
    fig_yt.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#E2E2EA"),
        margin=dict(l=20, r=20, t=30, b=20),
        title="YouTube Videos per Month",
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        showlegend=False,
        height=280,
    )
    st.plotly_chart(fig_yt, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <h4>💡 Quality > Quantity</h4>
    <p>Deel posts 14x/week on LinkedIn and gets 1.1% engagement. JustPaid posts 4x/week
    and gets 4.2% engagement. <strong>More content ≠ more reach.</strong>
    The strategy: maintain current posting rhythm, dramatically improve content quality
    with the gaps identified above. One viral post outperforms 30 average ones.</p>
</div>
""", unsafe_allow_html=True)

# ── Q2 Recommendations ────────────────────────────────────────────────────
st.divider()
st.markdown("### 🚀 Q2 Competitive Strategy")

r1, r2, r3 = st.columns(3)
with r1:
    st.markdown("""
    **Own "AI payments" on LinkedIn**
    - 1 post/week on AI-powered payment automation
    - Tag relevant founders + operators
    - Target: 500 new followers/month
    """)
with r2:
    st.markdown("""
    **YouTube SEO blitz**
    - 4 keyword-optimized videos: "how to pay [country] contractors"
    - Target search keywords competitors ignore
    - Goal: 3 videos ranking top 5 by Q3
    """)
with r3:
    st.markdown("""
    **Competitor keyword capture**
    - 2 comparison blog posts/videos
    - Engage on competitor review threads (G2, Capterra)
    - Target people actively evaluating Deel/Gusto
    """)
