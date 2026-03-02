from datetime import datetime, date
from googleapiclient.discovery import build

from config.settings import YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID


def _get_youtube_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def collect_channel_stats() -> dict:
    """Fetch current channel-level stats (subscribers, views, videos)."""
    youtube = _get_youtube_client()
    response = (
        youtube.channels()
        .list(part="statistics,snippet", id=YOUTUBE_CHANNEL_ID)
        .execute()
    )
    if not response.get("items"):
        raise ValueError(f"No channel found for ID: {YOUTUBE_CHANNEL_ID}")

    stats = response["items"][0]["statistics"]
    return {
        "date": date.today().isoformat(),
        "platform": "YouTube",
        "followers": int(stats.get("subscriberCount", 0)),
        "total_posts": int(stats.get("videoCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "collected_at": datetime.utcnow().isoformat(),
    }


def collect_recent_videos(max_results: int = 50) -> list[dict]:
    """Fetch recent video details with view/like/comment counts."""
    youtube = _get_youtube_client()

    # Step 1: Search for recent uploads
    search_response = (
        youtube.search()
        .list(
            part="id,snippet",
            channelId=YOUTUBE_CHANNEL_ID,
            order="date",
            maxResults=max_results,
            type="video",
        )
        .execute()
    )

    video_ids = [
        item["id"]["videoId"]
        for item in search_response.get("items", [])
        if item["id"].get("videoId")
    ]

    if not video_ids:
        return []

    # Step 2: Get detailed stats for each video (batch up to 50)
    videos_response = (
        youtube.videos()
        .list(
            part="statistics,snippet,contentDetails",
            id=",".join(video_ids),
        )
        .execute()
    )

    posts = []
    now = datetime.utcnow().isoformat()

    for video in videos_response.get("items", []):
        snippet = video["snippet"]
        stats = video.get("statistics", {})

        # Determine content type from duration
        duration = video.get("contentDetails", {}).get("duration", "")
        if "M" not in duration and "H" not in duration:
            post_type = "Short"
        else:
            post_type = "Video"

        posts.append(
            {
                "post_id": video["id"],
                "platform": "YouTube",
                "published_at": snippet.get("publishedAt"),
                "post_type": post_type,
                "title": snippet.get("title", ""),
                "url": f"https://youtube.com/watch?v={video['id']}",
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "shares": 0,  # YouTube API doesn't expose share count
                "collected_at": now,
            }
        )

    return posts


def collect_all() -> tuple[dict, list[dict]]:
    """Run full YouTube collection. Returns (channel_metrics, posts)."""
    channel_metrics = collect_channel_stats()
    posts = collect_recent_videos()

    # Calculate engagement for channel metrics
    total_likes = sum(p["likes"] for p in posts)
    total_comments = sum(p["comments"] for p in posts)
    total_views = sum(p["views"] for p in posts) or 1

    channel_metrics["total_likes"] = total_likes
    channel_metrics["total_comments"] = total_comments
    channel_metrics["new_posts"] = len(posts)
    channel_metrics["engagement_rate"] = round(
        (total_likes + total_comments) / total_views * 100, 4
    )

    return channel_metrics, posts
