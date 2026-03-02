"""LinkedIn collector — Phase 2.
Requires LinkedIn Marketing API access with r_organization_social scope.
Note: LinkedIn API approval can take several days.
"""

from datetime import datetime, date
import requests

from config.settings import LINKEDIN_ACCESS_TOKEN, LINKEDIN_ORG_ID

API_BASE = "https://api.linkedin.com/v2"


def _headers():
    return {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def collect_channel_stats() -> dict:
    """Fetch LinkedIn organization follower count."""
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_ORG_ID:
        return {}

    url = f"{API_BASE}/networkSizes/urn:li:organization:{LINKEDIN_ORG_ID}"
    params = {"edgeType": "CompanyFollowedByMember"}
    resp = requests.get(url, headers=_headers(), params=params)
    resp.raise_for_status()
    data = resp.json()

    return {
        "date": date.today().isoformat(),
        "platform": "LinkedIn",
        "followers": data.get("firstDegreeSize", 0),
        "collected_at": datetime.utcnow().isoformat(),
    }


def collect_recent_posts(limit: int = 25) -> list[dict]:
    """Fetch recent LinkedIn organization posts."""
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_ORG_ID:
        return []

    url = f"{API_BASE}/ugcPosts"
    params = {
        "q": "authors",
        "authors": f"List(urn:li:organization:{LINKEDIN_ORG_ID})",
        "count": limit,
    }
    resp = requests.get(url, headers=_headers(), params=params)
    resp.raise_for_status()
    items = resp.json().get("elements", [])

    now = datetime.utcnow().isoformat()
    posts = []
    for item in items:
        post_id = item.get("id", "")
        # Extract text from specificContent
        content = (
            item.get("specificContent", {})
            .get("com.linkedin.ugc.ShareContent", {})
        )
        text = (
            content.get("shareCommentary", {}).get("text", "")[:100]
        )

        posts.append({
            "post_id": post_id,
            "platform": "LinkedIn",
            "published_at": datetime.fromtimestamp(
                item.get("created", {}).get("time", 0) / 1000
            ).isoformat() if item.get("created", {}).get("time") else None,
            "post_type": "Post",
            "title": text,
            "url": f"https://www.linkedin.com/feed/update/{post_id}",
            "views": 0,  # Requires separate analytics endpoint
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "collected_at": now,
        })

    return posts


def collect_all() -> tuple[dict, list[dict]]:
    """Run full LinkedIn collection."""
    channel_metrics = collect_channel_stats()
    posts = collect_recent_posts()

    if channel_metrics:
        channel_metrics["new_posts"] = len(posts)
        channel_metrics["total_posts"] = len(posts)

    return channel_metrics, posts
