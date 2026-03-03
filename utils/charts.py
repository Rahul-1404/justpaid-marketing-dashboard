import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config.settings import PLATFORM_COLORS, BRAND


def _base_layout() -> dict:
    """Shared Plotly layout for JustPaid brand consistency."""
    return dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=BRAND["text"]),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.04)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.04)",
        ),
    )


def follower_growth_chart(df: pd.DataFrame, title: str = "Follower Growth") -> go.Figure:
    """Line chart showing follower growth over time, one line per platform."""
    fig = go.Figure()

    if df.empty:
        fig.update_layout(**_base_layout(), title=title)
        return fig

    for platform in df["platform"].unique():
        pdf = df[df["platform"] == platform].sort_values("date")
        fig.add_trace(
            go.Scatter(
                x=pdf["date"],
                y=pdf["followers"],
                name=platform,
                mode="lines+markers",
                line=dict(
                    color=PLATFORM_COLORS.get(platform, BRAND["primary"]),
                    width=2,
                ),
                marker=dict(size=4),
                hovertemplate=f"<b>{platform}</b><br>"
                + "Date: %{x}<br>Followers: %{y:,.0f}<extra></extra>",
            )
        )

    fig.update_layout(**_base_layout(), title=title, hovermode="x unified")
    return fig


def engagement_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart comparing engagement rates across platforms."""
    fig = go.Figure()

    if df.empty:
        fig.update_layout(**_base_layout(), title="Engagement Rate by Platform")
        return fig

    platforms = df["platform"].tolist()
    rates = df["engagement_rate"].tolist()
    colors = [PLATFORM_COLORS.get(p, BRAND["primary"]) for p in platforms]

    fig.add_trace(
        go.Bar(
            x=platforms,
            y=rates,
            marker_color=colors,
            text=[f"{r:.2f}%" for r in rates],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Engagement: %{y:.2f}%<extra></extra>",
        )
    )

    fig.update_layout(
        **_base_layout(),
        title="Engagement Rate by Platform",
        yaxis_title="Engagement Rate (%)",
        showlegend=False,
    )
    return fig


def top_posts_table(df: pd.DataFrame) -> go.Figure:
    """Styled table of top-performing posts."""
    if df.empty:
        df = pd.DataFrame(
            columns=["platform", "title", "views", "likes", "comments"]
        )

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["Platform", "Title", "Views", "Likes", "Comments"],
                    fill_color=BRAND["card_bg"],
                    font=dict(color=BRAND["text"], size=12),
                    align="left",
                    line_color="rgba(255,255,255,0.06)",
                ),
                cells=dict(
                    values=[
                        df.get("platform", []),
                        df.get("title", pd.Series(dtype=str)).str[:60],
                        df.get("views", pd.Series(dtype=int)).apply(
                            lambda x: f"{x:,.0f}" if pd.notna(x) else "0"
                        ),
                        df.get("likes", pd.Series(dtype=int)).apply(
                            lambda x: f"{x:,.0f}" if pd.notna(x) else "0"
                        ),
                        df.get("comments", pd.Series(dtype=int)).apply(
                            lambda x: f"{x:,.0f}" if pd.notna(x) else "0"
                        ),
                    ],
                    fill_color=BRAND["dark"],
                    font=dict(color=BRAND["text_muted"], size=11),
                    align="left",
                    line_color="rgba(255,255,255,0.04)",
                    height=32,
                ),
            )
        ]
    )

    fig.update_layout(
        **_base_layout(),
        title="Top Performing Content",
        height=max(250, 40 * len(df) + 80),
    )
    return fig


def content_type_breakdown(df: pd.DataFrame, platform: str = None) -> go.Figure:
    """Donut chart showing content type distribution."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**_base_layout(), title="Content Type Breakdown")
        return fig

    counts = df["post_type"].value_counts()

    color_map = {
        "Video": BRAND["primary"],
        "Short": BRAND["accent"],
        "Reel": "#E4405F",
        "Story": "#FDCB6E",
        "Post": "#0A66C2",
        "Article": "#00B894",
    }
    colors = [color_map.get(t, BRAND["secondary"]) for t in counts.index]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=counts.index,
                values=counts.values,
                hole=0.5,
                marker=dict(colors=colors),
                textinfo="label+percent",
                textfont=dict(size=11),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            )
        ]
    )

    title = f"{platform} Content Breakdown" if platform else "Content Type Breakdown"
    fig.update_layout(**_base_layout(), title=title, showlegend=True)
    return fig


def posting_frequency_chart(df: pd.DataFrame, date_col: str = "published_at") -> go.Figure:
    """Bar chart showing posts per week."""
    if df.empty or date_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(**_base_layout(), title="Posting Frequency")
        return fig

    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    weekly = df.set_index(date_col).resample("W").size().reset_index(name="count")

    fig = go.Figure(
        data=[
            go.Bar(
                x=weekly[date_col],
                y=weekly["count"],
                marker_color=BRAND["primary"],
                hovertemplate="Week of %{x}<br>Posts: %{y}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        **_base_layout(),
        title="Posting Frequency (Weekly)",
        xaxis_title="Week",
        yaxis_title="Posts",
    )
    return fig


def _qoq_layout(**kwargs) -> dict:
    """Base layout for QoQ charts with horizontal legend on top."""
    layout = _base_layout()
    layout["legend"] = dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="center", x=0.5, bgcolor="rgba(0,0,0,0)", font=dict(size=11),
    )
    layout.update(kwargs)
    return layout


def qoq_comparison_bars(curr_stats: dict, prev_stats: dict,
                        curr_label: str, prev_label: str) -> go.Figure:
    """Grouped bar chart comparing two quarters across key metrics."""
    metrics = ["total_posts", "total_views", "total_likes", "total_comments"]
    labels = ["Posts", "Views", "Likes", "Comments"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=prev_label,
        x=labels,
        y=[prev_stats.get(m, 0) for m in metrics],
        marker_color=BRAND["text_muted"],
        text=[f"{prev_stats.get(m, 0):,}" for m in metrics],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name=curr_label,
        x=labels,
        y=[curr_stats.get(m, 0) for m in metrics],
        marker_color=BRAND["primary"],
        text=[f"{curr_stats.get(m, 0):,}" for m in metrics],
        textposition="outside",
    ))

    fig.update_layout(**_qoq_layout(
        barmode="group",
        title=f"{curr_label} vs {prev_label}",
        showlegend=True,
    ))
    return fig


def qoq_avg_performance_bars(curr_stats: dict, prev_stats: dict,
                              curr_label: str, prev_label: str) -> go.Figure:
    """Grouped bar chart for average per-post metrics."""
    metrics = ["avg_views", "avg_likes"]
    labels = ["Avg Views/Post", "Avg Likes/Post"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=prev_label,
        x=labels,
        y=[prev_stats.get(m, 0) for m in metrics],
        marker_color=BRAND["text_muted"],
        text=[f"{prev_stats.get(m, 0):,}" for m in metrics],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name=curr_label,
        x=labels,
        y=[curr_stats.get(m, 0) for m in metrics],
        marker_color=BRAND["accent"],
        text=[f"{curr_stats.get(m, 0):,}" for m in metrics],
        textposition="outside",
    ))

    fig.update_layout(**_qoq_layout(
        barmode="group",
        title="Average Performance Per Post",
        showlegend=True,
    ))
    return fig


def qoq_content_mix_comparison(curr_df: pd.DataFrame, prev_df: pd.DataFrame,
                                curr_label: str, prev_label: str) -> go.Figure:
    """Side-by-side content type comparison between quarters."""
    curr_counts = curr_df["post_type"].value_counts() if not curr_df.empty else pd.Series(dtype=int)
    prev_counts = prev_df["post_type"].value_counts() if not prev_df.empty else pd.Series(dtype=int)

    all_types = sorted(set(list(curr_counts.index) + list(prev_counts.index)))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=prev_label,
        x=all_types,
        y=[prev_counts.get(t, 0) for t in all_types],
        marker_color=BRAND["text_muted"],
    ))
    fig.add_trace(go.Bar(
        name=curr_label,
        x=all_types,
        y=[curr_counts.get(t, 0) for t in all_types],
        marker_color=BRAND["primary"],
    ))

    fig.update_layout(**_qoq_layout(
        barmode="group",
        title="Content Mix Comparison",
        xaxis_title="Content Type",
        yaxis_title="Count",
        showlegend=True,
    ))
    return fig
