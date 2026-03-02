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


def calculate_posting_frequency(df: pd.DataFrame, date_col: str = "published_at") -> float:
    """Calculate average posts per week from a DataFrame."""
    if df.empty or date_col not in df.columns:
        return 0.0
    dates = pd.to_datetime(df[date_col])
    if len(dates) < 2:
        return 0.0
    span_days = (dates.max() - dates.min()).days or 1
    return round(len(df) / (span_days / 7), 1)
