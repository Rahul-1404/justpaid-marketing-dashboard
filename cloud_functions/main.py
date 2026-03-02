"""Cloud Function for daily social media data collection.

Deploy with:
    gcloud functions deploy collect_social_data \
        --runtime python311 \
        --trigger-http \
        --allow-unauthenticated \
        --entry-point collect_social_data \
        --source cloud_functions/ \
        --set-env-vars GCP_PROJECT_ID=bionic-store-488922-d6

Schedule with Cloud Scheduler:
    gcloud scheduler jobs create http daily-social-collect \
        --schedule "0 6 * * *" \
        --uri <FUNCTION_URL> \
        --http-method GET \
        --time-zone "UTC"
"""

import functions_framework
import traceback


@functions_framework.http
def collect_social_data(request):
    """HTTP Cloud Function that collects data from all platforms."""
    import sys
    import os

    # Add parent dir to path so we can import our modules
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from storage.bigquery_client import (
        ensure_tables_exist,
        insert_channel_metrics,
        insert_posts,
    )

    results = {"success": [], "errors": []}

    # Ensure tables exist
    try:
        ensure_tables_exist()
    except Exception as e:
        results["errors"].append(f"Table setup: {e}")

    # YouTube
    try:
        from collectors.youtube_collector import collect_all as yt_collect
        channel, posts = yt_collect()
        if channel:
            insert_channel_metrics([channel])
        if posts:
            insert_posts(posts)
        results["success"].append(f"YouTube: {len(posts)} posts collected")
    except Exception as e:
        results["errors"].append(f"YouTube: {traceback.format_exc()}")

    # Instagram
    try:
        from collectors.instagram_collector import collect_all as ig_collect
        channel, posts = ig_collect()
        if channel:
            insert_channel_metrics([channel])
        if posts:
            insert_posts(posts)
        results["success"].append(f"Instagram: {len(posts)} posts collected")
    except Exception as e:
        results["errors"].append(f"Instagram: {traceback.format_exc()}")

    # LinkedIn
    try:
        from collectors.linkedin_collector import collect_all as li_collect
        channel, posts = li_collect()
        if channel:
            insert_channel_metrics([channel])
        if posts:
            insert_posts(posts)
        results["success"].append(f"LinkedIn: {len(posts)} posts collected")
    except Exception as e:
        results["errors"].append(f"LinkedIn: {traceback.format_exc()}")

    # Twitter (from Google Sheets)
    try:
        from collectors.twitter_collector import collect_all as tw_collect
        channel, posts = tw_collect()
        if channel:
            insert_channel_metrics([channel])
        if posts:
            insert_posts(posts)
        results["success"].append(f"Twitter: {len(posts)} posts collected")
    except Exception as e:
        results["errors"].append(f"Twitter: {traceback.format_exc()}")

    status_code = 200 if not results["errors"] else 207
    return (results, status_code)
