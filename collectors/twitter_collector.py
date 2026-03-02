"""Twitter/X collector — Phase 3.
Reads from a Google Sheet since the free X API tier has no read access.
Expected sheet columns: date, followers, tweet_id, text, impressions,
likes, replies, retweets, url
"""

from datetime import datetime, date

import gspread
from google.oauth2.service_account import Credentials

from config.settings import TWITTER_SHEET_ID, GOOGLE_SHEETS_CREDENTIALS_FILE

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def _get_sheet():
    creds = Credentials.from_service_account_file(
        GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    return gc.open_by_key(TWITTER_SHEET_ID).sheet1


def collect_channel_stats() -> dict:
    """Read latest follower count from the Google Sheet."""
    if not TWITTER_SHEET_ID:
        return {}

    sheet = _get_sheet()
    records = sheet.get_all_records()
    if not records:
        return {}

    latest = records[-1]
    return {
        "date": latest.get("date", date.today().isoformat()),
        "platform": "Twitter",
        "followers": int(latest.get("followers", 0)),
        "collected_at": datetime.utcnow().isoformat(),
    }


def collect_recent_posts() -> list[dict]:
    """Read tweet data from the Google Sheet."""
    if not TWITTER_SHEET_ID:
        return []

    sheet = _get_sheet()
    records = sheet.get_all_records()
    now = datetime.utcnow().isoformat()

    posts = []
    for row in records:
        if not row.get("tweet_id"):
            continue
        posts.append({
            "post_id": str(row["tweet_id"]),
            "platform": "Twitter",
            "published_at": row.get("date"),
            "post_type": "Tweet",
            "title": str(row.get("text", ""))[:100],
            "url": row.get("url", ""),
            "views": int(row.get("impressions", 0)),
            "likes": int(row.get("likes", 0)),
            "comments": int(row.get("replies", 0)),
            "shares": int(row.get("retweets", 0)),
            "collected_at": now,
        })

    return posts


def collect_all() -> tuple[dict, list[dict]]:
    """Run full Twitter collection from Google Sheets."""
    channel_metrics = collect_channel_stats()
    posts = collect_recent_posts()

    if channel_metrics and posts:
        total_likes = sum(p["likes"] for p in posts)
        total_comments = sum(p["comments"] for p in posts)
        total_views = sum(p["views"] for p in posts) or 1
        channel_metrics["total_likes"] = total_likes
        channel_metrics["total_comments"] = total_comments
        channel_metrics["new_posts"] = len(posts)
        channel_metrics["total_views"] = total_views
        channel_metrics["engagement_rate"] = round(
            (total_likes + total_comments) / total_views * 100, 4
        )

    return channel_metrics, posts
