import pandas as pd
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.cloud.bigquery import TimePartitioning

from config.settings import GCP_PROJECT_ID, BIGQUERY_DATASET
from storage.schemas import TABLE_CONFIGS


def _get_client():
    return bigquery.Client(project=GCP_PROJECT_ID)


def _table_id(table_name: str) -> str:
    return f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.{table_name}"


def ensure_tables_exist():
    """Create dataset and tables if they don't exist."""
    client = _get_client()

    dataset_ref = bigquery.DatasetReference(GCP_PROJECT_ID, BIGQUERY_DATASET)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"
    client.create_dataset(dataset, exists_ok=True)

    for table_name, config in TABLE_CONFIGS.items():
        table_ref = dataset_ref.table(table_name)
        table = bigquery.Table(table_ref, schema=config["schema"])
        if config.get("time_partitioning_field"):
            table.time_partitioning = TimePartitioning(
                field=config["time_partitioning_field"]
            )
        if config.get("clustering_fields"):
            table.clustering_fields = config["clustering_fields"]
        client.create_table(table, exists_ok=True)


def insert_channel_metrics(rows: list[dict]):
    """Insert rows into channel_daily_metrics table."""
    if not rows:
        return
    client = _get_client()
    now = datetime.utcnow().isoformat()
    for row in rows:
        row.setdefault("collected_at", now)
    errors = client.insert_rows_json(_table_id("channel_daily_metrics"), rows)
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")


def insert_posts(rows: list[dict]):
    """Insert rows into posts table."""
    if not rows:
        return
    client = _get_client()
    now = datetime.utcnow().isoformat()
    for row in rows:
        row.setdefault("collected_at", now)
    errors = client.insert_rows_json(_table_id("posts"), rows)
    if errors:
        raise RuntimeError(f"BigQuery insert errors: {errors}")


def get_channel_metrics(
    platform: str = None, days: int = 90
) -> pd.DataFrame:
    """Fetch channel daily metrics as a DataFrame."""
    client = _get_client()
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    query = f"""
        SELECT *
        FROM `{_table_id('channel_daily_metrics')}`
        WHERE date >= '{cutoff}'
        {"AND platform = '" + platform + "'" if platform else ""}
        ORDER BY date ASC
    """
    return client.query(query).to_dataframe()


def get_posts(
    platform: str = None, days: int = 90, limit: int = 50
) -> pd.DataFrame:
    """Fetch posts as a DataFrame."""
    client = _get_client()
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    query = f"""
        SELECT *
        FROM `{_table_id('posts')}`
        WHERE collected_at >= TIMESTAMP('{cutoff}')
        {"AND platform = '" + platform + "'" if platform else ""}
        ORDER BY views DESC
        LIMIT {limit}
    """
    return client.query(query).to_dataframe()


def get_latest_metrics_per_platform() -> pd.DataFrame:
    """Get the most recent row per platform for KPI cards."""
    client = _get_client()
    query = f"""
        SELECT m.*
        FROM `{_table_id('channel_daily_metrics')}` m
        INNER JOIN (
            SELECT platform, MAX(date) as max_date
            FROM `{_table_id('channel_daily_metrics')}`
            GROUP BY platform
        ) latest
        ON m.platform = latest.platform AND m.date = latest.max_date
    """
    return client.query(query).to_dataframe()


def get_posts_by_date_range(
    start_date: str, end_date: str, platform: str = None
) -> pd.DataFrame:
    """Fetch posts published within a date range."""
    client = _get_client()
    query = f"""
        SELECT DISTINCT post_id, platform, title, post_type, url,
               views, likes, comments, shares, published_at, collected_at
        FROM `{_table_id('posts')}`
        WHERE published_at >= TIMESTAMP('{start_date}')
          AND published_at < TIMESTAMP('{end_date}T23:59:59')
        {"AND platform = '" + platform + "'" if platform else ""}
        ORDER BY views DESC
    """
    return client.query(query).to_dataframe()


def get_top_posts_all_platforms(limit: int = 5) -> pd.DataFrame:
    """Get top posts across all platforms by views."""
    client = _get_client()
    query = f"""
        SELECT DISTINCT post_id, platform, title, post_type, url,
               views, likes, comments, shares, published_at
        FROM `{_table_id('posts')}`
        WHERE views IS NOT NULL
        ORDER BY views DESC
        LIMIT {limit}
    """
    return client.query(query).to_dataframe()
