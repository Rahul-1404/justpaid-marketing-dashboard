import os
from dotenv import load_dotenv

load_dotenv()

# Google Cloud
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "bionic-store-488922-d6")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "justpaid_social")

# YouTube
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

# Instagram
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

# LinkedIn
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
LINKEDIN_ORG_ID = os.getenv("LINKEDIN_ORG_ID", "")

# Twitter (Google Sheet)
TWITTER_SHEET_ID = os.getenv("TWITTER_SHEET_ID", "")
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials/sheets_service_account.json"
)

# Platform colors for consistent branding
PLATFORM_COLORS = {
    "YouTube": "#FF0000",
    "Instagram": "#E4405F",
    "LinkedIn": "#0A66C2",
    "Twitter": "#1DA1F2",
}

# JustPaid brand colors
BRAND = {
    "primary": "#6C5CE7",
    "secondary": "#A29BFE",
    "accent": "#00CEC9",
    "success": "#00B894",
    "warning": "#FDCB6E",
    "danger": "#E17055",
    "dark": "#0E1117",
    "card_bg": "#1A1D29",
    "text": "#E2E2EA",
    "text_muted": "#8A8A9A",
}
