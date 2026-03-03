import pandas as pd


def engagement_rate(likes: int, comments: int, shares: int, views: int) -> float:
    """Calculate engagement rate as percentage."""
    if views == 0:
        return 0.0
    return round((likes + comments + shares) / views * 100, 4)


def follower_change_pct(current: int, previous: int) -> float:
    """Calculate percentage change in followers."""
    if previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 2)


def format_number(n: int | float) -> str:
    """Format large numbers for display (1.2K, 3.4M, etc.)."""
    if n is None:
        return "0"
    n = int(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def delta_indicator(current: int | float, previous: int | float) -> tuple[str, str]:
    """Return (formatted_delta, css_color) for KPI cards."""
    if previous == 0:
        return "+0", "#8A8A9A"
    diff = current - previous
    pct = (diff / previous) * 100
    if diff > 0:
        return f"+{format_number(abs(diff))} ({pct:+.1f}%)", "#00B894"
    elif diff < 0:
        return f"-{format_number(abs(diff))} ({pct:.1f}%)", "#E17055"
    return "0 (0.0%)", "#8A8A9A"


def quarter_boundaries(year: int, quarter: int) -> tuple[str, str]:
    """Return (start_date, end_date) ISO strings for a given quarter."""
    starts = {1: f"{year}-01-01", 2: f"{year}-04-01", 3: f"{year}-07-01", 4: f"{year}-10-01"}
    ends = {1: f"{year}-03-31", 2: f"{year}-06-30", 3: f"{year}-09-30", 4: f"{year}-12-31"}
    return starts[quarter], ends[quarter]


def current_and_previous_quarter(today=None) -> tuple[tuple[int, int], tuple[int, int]]:
    """Return ((curr_year, curr_q), (prev_year, prev_q))."""
    if today is None:
        today = pd.Timestamp.now()
    curr_q = (today.month - 1) // 3 + 1
    curr_year = today.year
    if curr_q == 1:
        return (curr_year, 1), (curr_year - 1, 4)
    return (curr_year, curr_q), (curr_year, curr_q - 1)


def quarter_label(year: int, quarter: int) -> str:
    return f"Q{quarter} {year}"


def compute_quarter_stats(df: pd.DataFrame, date_col: str = "published_at") -> dict:
    """Compute aggregate stats for a set of posts."""
    if df.empty:
        return {
            "total_posts": 0, "total_views": 0, "total_likes": 0,
            "total_comments": 0, "avg_views": 0, "avg_likes": 0,
            "engagement_rate": 0.0, "top_post": None,
        }
    total_views = int(df["views"].sum())
    total_likes = int(df["likes"].sum())
    total_comments = int(df["comments"].sum())
    total_shares = int(df["shares"].sum()) if "shares" in df.columns else 0
    total_posts = len(df)

    top_row = df.loc[df["views"].idxmax()]

    return {
        "total_posts": total_posts,
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "avg_views": round(total_views / total_posts) if total_posts else 0,
        "avg_likes": round(total_likes / total_posts) if total_posts else 0,
        "engagement_rate": round(
            (total_likes + total_comments + total_shares) / max(total_views, 1) * 100, 2
        ),
        "top_post": top_row.get("title", ""),
    }


def calculate_posting_frequency(df: pd.DataFrame, date_col: str = "published_at") -> float:
    """Calculate average posts per week from a DataFrame."""
    if df.empty or date_col not in df.columns:
        return 0.0
    dates = pd.to_datetime(df[date_col])
    if len(dates) < 2:
        return 0.0
    span_days = (dates.max() - dates.min()).days or 1
    return round(len(df) / (span_days / 7), 1)
