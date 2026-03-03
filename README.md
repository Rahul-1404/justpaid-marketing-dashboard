# JustPaid Social Media Analytics Dashboard

A real-time, multi-platform social media analytics dashboard built for [JustPaid](https://justpaid.io). Tracks performance across YouTube, Instagram, LinkedIn, and X/Twitter with automated daily data collection, quarter-over-quarter comparisons, and an MCP server for on-demand LinkedIn scraping.

**Live:** [justpaid-analytics-484936366711.us-central1.run.app](https://justpaid-analytics-484936366711.us-central1.run.app)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.42 + Plotly 6.0 |
| Data Warehouse | Google BigQuery |
| Deployment | Google Cloud Run (Docker) |
| Scheduled Collection | Google Cloud Functions + Cloud Scheduler |
| LinkedIn Scraping | MCP Server (Playwright) |
| APIs | YouTube Data API v3, Meta Graph API, LinkedIn Marketing API |

## Features

- **Cross-platform overview** with unified KPI cards, follower growth trends, and engagement comparison
- **Per-platform detail pages** for YouTube, Instagram, LinkedIn, and X/Twitter
- **Quarter-over-Quarter analysis** on every page — KPI delta cards, growth charts, content mix comparison, and top performers by quarter
- **Dark theme UI** with JustPaid brand colors (purple/cyan gradient)
- **LinkedIn MCP server** for browser-based scraping when API access isn't available
- **Automated daily collection** via Cloud Functions + Cloud Scheduler

## Project Structure

```
justpaid-social-dashboard/
├── app.py                        # Main dashboard (home page)
├── Dockerfile                    # Cloud Run deployment
├── requirements.txt              # Python dependencies
├── .streamlit/
│   └── config.toml               # Theme & server config
│
├── config/
│   └── settings.py               # Env vars, brand colors, platform colors
│
├── pages/                        # Streamlit multi-page app
│   ├── 1_YouTube.py              # YouTube analytics
│   ├── 2_Instagram.py            # Instagram analytics
│   ├── 3_LinkedIn.py             # LinkedIn analytics
│   ├── 4_Twitter.py              # X/Twitter analytics
│   └── 5_Cross_Platform.py       # Cross-platform comparison
│
├── collectors/                   # Platform-specific data collectors
│   ├── youtube_collector.py      # YouTube Data API v3
│   ├── instagram_collector.py    # Meta Graph API
│   ├── linkedin_collector.py     # LinkedIn Marketing API
│   └── twitter_collector.py      # Google Sheets fallback
│
├── storage/
│   ├── bigquery_client.py        # BigQuery query & insert functions
│   └── schemas.py                # Table schemas (channel_daily_metrics, posts)
│
├── utils/
│   ├── metrics.py                # Engagement calc, formatting, QoQ utilities
│   └── charts.py                 # 11 Plotly chart functions
│
├── mcp_servers/
│   └── linkedin/
│       └── server.py             # MCP server with 4 LinkedIn scraping tools
│
├── cloud_functions/
│   └── main.py                   # Daily collection orchestrator
│
└── scripts/                      # One-off data backfill scripts
    ├── insert_q4_instagram.py    # 45 Instagram posts (Q4 2025)
    ├── insert_q4_linkedin.py     # 72 LinkedIn posts (Q4 2025)
    └── insert_q4_twitter.py      # 60 Twitter posts (Q4 2025)
```

## Data Architecture

### BigQuery Tables

**`channel_daily_metrics`** — Daily platform-level rollups (partitioned by `date`, clustered by `platform`)

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Snapshot date |
| platform | STRING | YouTube / Instagram / LinkedIn / Twitter |
| followers | INTEGER | Total follower count |
| follower_change | INTEGER | Net change from previous day |
| total_posts | INTEGER | Cumulative post count |
| engagement_rate | FLOAT | (likes + comments + shares) / views * 100 |
| collected_at | TIMESTAMP | When the data was fetched |

**`posts`** — Individual post data (partitioned by `collected_at`, clustered by `platform, post_type`)

| Column | Type | Description |
|--------|------|-------------|
| post_id | STRING | Unique identifier |
| platform | STRING | Source platform |
| published_at | TIMESTAMP | When the post went live |
| post_type | STRING | Video / Short / Reel / Post / Carousel / Article |
| title | STRING | Post title or caption |
| views | INTEGER | View / impression count |
| likes | INTEGER | Like / reaction count |
| comments | INTEGER | Comment / reply count |
| shares | INTEGER | Share / retweet count |

### Data Flow

```
Cloud Scheduler (daily, 6 AM UTC)
        │
        ▼
Cloud Function: collect_social_data()
        │
        ├── YouTube API ──────┐
        ├── Instagram API ────┤
        ├── LinkedIn API ─────┤──▶ BigQuery
        └── Google Sheets ────┘    ├── channel_daily_metrics
                                   └── posts
                                        │
                                        ▼
                               Cloud Run: Streamlit App
                               ├── app.py (overview)
                               ├── pages/ (per-platform)
                               └── Plotly charts + KPI cards
```

## Dashboard Pages

### Home (`app.py`)
- 4 KPI cards (one per platform) with follower counts and delta indicators
- Follower growth line chart (all platforms)
- Engagement rate comparison bar chart
- Top 5 performing posts across all platforms
- Quarter-over-Quarter section with delta cards, comparison bars, and content mix

### Platform Pages (`pages/1-4_*.py`)
Each platform page includes:
- Platform-specific KPI cards (subscribers, views, engagement, posts)
- Follower/subscriber growth chart
- Content type breakdown (donut chart)
- Posting frequency (weekly bar chart)
- Top 10 posts table
- **Quarter-over-Quarter comparison:**
  - KPI delta cards (Posts Published, Total Views, Total Likes, Engagement Rate)
  - Growth chart (dual-axis: followers + engagement %)
  - Side-by-side comparison bars and average performance bars
  - Content mix comparison
  - Top 5 performers per quarter

### Cross-Platform (`pages/5_Cross_Platform.py`)
- Total audience count across all platforms
- Combined follower growth chart
- Platform comparison table
- Engagement and posting frequency comparisons

## Charts (`utils/charts.py`)

11 reusable Plotly chart functions, all using the `plotly_dark` template with JustPaid branding:

| Function | Description |
|----------|-------------|
| `follower_growth_chart()` | Line chart of follower count over time |
| `engagement_comparison_chart()` | Bar chart comparing engagement rates |
| `top_posts_table()` | Styled Plotly table for top content |
| `content_type_breakdown()` | Donut chart of post types |
| `posting_frequency_chart()` | Weekly posting bar chart |
| `platform_comparison_table()` | Multi-metric platform table |
| `qoq_growth_chart()` | Dual-axis grouped bar (followers + engagement %) |
| `qoq_comparison_bars()` | Side-by-side bars for posts, views, likes, comments |
| `qoq_avg_performance_bars()` | Average views/likes per post comparison |
| `qoq_content_mix_comparison()` | Stacked bars showing content type distribution |

## LinkedIn MCP Server

The LinkedIn MCP server (`mcp_servers/linkedin/server.py`) provides browser-based scraping as a fallback when API access isn't available. Built with [Playwright](https://playwright.dev/) and the [Model Context Protocol](https://modelcontextprotocol.io/).

### Tools

| Tool | Description |
|------|-------------|
| `get_follower_count()` | Scrapes follower count from LinkedIn admin analytics |
| `get_content_analytics(days)` | Fetches content performance metrics |
| `get_impressions_by_content(days)` | Post-level impression breakdown |
| `compare_to_previous_period()` | Quarter-over-quarter comparison via web |

### How It Works

- Launches a headed Chrome instance with persistent session cookies (stored in `.browser_data/`)
- No re-login required after first manual authentication
- Configured in `.mcp.json` for use with Claude Code

## Setup

### Prerequisites

- Python 3.11+
- Google Cloud project with BigQuery enabled
- YouTube Data API key

### Local Development

```bash
# Clone
git clone https://github.com/Shrinija17/justpaid-social-dashboard.git
cd justpaid-social-dashboard

# Virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Environment variables
cp .env.example .env  # Then fill in your API keys

# Required env vars:
# GCP_PROJECT_ID=your-gcp-project
# BIGQUERY_DATASET=justpaid_social
# YOUTUBE_API_KEY=your-youtube-key
# YOUTUBE_CHANNEL_ID=your-channel-id

# Optional (Phase 2):
# INSTAGRAM_ACCESS_TOKEN=...
# INSTAGRAM_BUSINESS_ACCOUNT_ID=...
# LINKEDIN_ACCESS_TOKEN=...
# LINKEDIN_ORG_ID=...

# Run
streamlit run app.py
```

### Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy justpaid-analytics \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=your-project,BIGQUERY_DATASET=justpaid_social

# Set up daily collection
gcloud functions deploy collect_social_data \
  --runtime python311 \
  --trigger-http \
  --source cloud_functions/ \
  --set-env-vars GCP_PROJECT_ID=your-project

gcloud scheduler jobs create http daily-social-collect \
  --schedule "0 6 * * *" \
  --uri YOUR_FUNCTION_URL \
  --http-method GET
```

## Data Backfill

Q4 2025 historical data was scraped from live platforms and inserted via scripts:

```bash
# Insert scraped data into BigQuery
python scripts/insert_q4_instagram.py   # 45 posts
python scripts/insert_q4_linkedin.py    # 72 posts
python scripts/insert_q4_twitter.py     # 60 posts
```

## Current Data

| Platform | Followers | Q4 2025 Posts | Q1 2026 Posts |
|----------|-----------|---------------|---------------|
| YouTube | 685 | 25 | 25 |
| Instagram | 92 | 45 | 10 |
| LinkedIn | 2,858 | 72 | 11 |
| X/Twitter | 128 | 60 | 5 |
