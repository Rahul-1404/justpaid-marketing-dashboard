"""Instagram collector — Phase 2.
Requires Meta Graph API access token + IG Business Account ID.
"""

from datetime import datetime, date
import requests

from config.settings import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


def collect_channel_stats() -> dict:
    """Fetch Instagram business account follower count and media count."""
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        return {}

    url = f"{GRAPH_API_BASE}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}"
    params = {
        "fields": "followers_count,media_count,username",
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    return {
        "date": date.today().isoformat(),
        "platform": "Instagram",
        "followers": data.get("followers_count", 0),
        "total_posts": data.get("media_count", 0),
        "collected_at": datetime.utcnow().isoformat(),
    }


def collect_recent_posts(limit: int = 25) -> list[dict]:
    """Fetch recent Instagram posts with engagement metrics."""
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        return []

    url = f"{GRAPH_API_BASE}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    params = {
        "fields": "id,caption,timestamp,media_type,permalink,like_count,comments_count",
        "limit": limit,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    items = resp.json().get("data", [])

    now = datetime.utcnow().isoformat()
    posts = []
    for item in items:
        media_type = item.get("media_type", "IMAGE")
        post_type_map = {
            "IMAGE": "Post",
            "VIDEO": "Reel",
            "CAROUSEL_ALBUM": "Post",
        }
        posts.append({
            "post_id": item["id"],
            "platform": "Instagram",
            "published_at": item.get("timestamp"),
            "post_type": post_type_map.get(media_type, "Post"),
            "title": (item.get("caption") or "")[:100],
            "url": item.get("permalink", ""),
            "views": 0,  # Requires insights endpoint
            "likes": item.get("like_count", 0),
            "comments": item.get("comments_count", 0),
            "shares": 0,
            "collected_at": now,
        })

    return posts


def collect_all() -> tuple[dict, list[dict]]:
    """Run full Instagram collection."""
    channel_metrics = collect_channel_stats()
    posts = collect_recent_posts()

    if channel_metrics and posts:
        total_likes = sum(p["likes"] for p in posts)
        total_comments = sum(p["comments"] for p in posts)
        followers = channel_metrics.get("followers", 1) or 1
        channel_metrics["total_likes"] = total_likes
        channel_metrics["total_comments"] = total_comments
        channel_metrics["new_posts"] = len(posts)
        channel_metrics["engagement_rate"] = round(
            (total_likes + total_comments) / followers * 100, 4
        )

    return channel_metrics, posts
