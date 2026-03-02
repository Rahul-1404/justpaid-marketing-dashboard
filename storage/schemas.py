from google.cloud.bigquery import SchemaField

CHANNEL_DAILY_METRICS_SCHEMA = [
    SchemaField("date", "DATE", mode="REQUIRED"),
    SchemaField("platform", "STRING", mode="REQUIRED"),
    SchemaField("followers", "INTEGER"),
    SchemaField("follower_change", "INTEGER"),
    SchemaField("total_posts", "INTEGER"),
    SchemaField("new_posts", "INTEGER"),
    SchemaField("total_views", "INTEGER"),
    SchemaField("total_likes", "INTEGER"),
    SchemaField("total_comments", "INTEGER"),
    SchemaField("engagement_rate", "FLOAT"),
    SchemaField("collected_at", "TIMESTAMP", mode="REQUIRED"),
]

POSTS_SCHEMA = [
    SchemaField("post_id", "STRING", mode="REQUIRED"),
    SchemaField("platform", "STRING", mode="REQUIRED"),
    SchemaField("published_at", "TIMESTAMP"),
    SchemaField("post_type", "STRING"),
    SchemaField("title", "STRING"),
    SchemaField("url", "STRING"),
    SchemaField("views", "INTEGER"),
    SchemaField("likes", "INTEGER"),
    SchemaField("comments", "INTEGER"),
    SchemaField("shares", "INTEGER"),
    SchemaField("collected_at", "TIMESTAMP", mode="REQUIRED"),
]

TABLE_CONFIGS = {
    "channel_daily_metrics": {
        "schema": CHANNEL_DAILY_METRICS_SCHEMA,
        "time_partitioning_field": "date",
        "clustering_fields": ["platform"],
    },
    "posts": {
        "schema": POSTS_SCHEMA,
        "time_partitioning_field": "collected_at",
        "clustering_fields": ["platform", "post_type"],
    },
}
