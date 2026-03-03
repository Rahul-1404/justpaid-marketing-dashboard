"""Insert scraped Q4 2025 X/Twitter posts into BigQuery."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from storage.bigquery_client import insert_posts

# Scraped from X/Twitter search (Oct 1 - Dec 31, 2025)
# Format: (date, views, replies, retweets, likes, text)
RAW = [
    # Batch 1: Dec 9-26
    ("12/26/2025", 39, 0, 0, 0, "Do you signup for JustPaid yet?"),
    ("12/19/2025", 41, 0, 0, 0, "Full Video on Youtube"),
    ("12/18/2025", 88, 0, 0, 0, "Here's a quick demo of how JustPaid acts as an AI-powered AR"),
    ("12/18/2025", 34, 0, 0, 0, "Full video on Youtube"),
    ("12/17/2025", 31, 0, 0, 0, "Youtube link - Talk on Finance"),
    ("12/17/2025", 48, 1, 0, 2, "If an invoice isn't collectible, it isn't revenue"),
    ("12/17/2025", 42, 0, 0, 0, "New episode of the JustPaid Podcast - Talk on Finance with Armand Zand"),
    ("12/16/2025", 62, 1, 0, 1, "New episode of the JustPaid Podcast - Prasanna Sankar"),
    ("12/16/2025", 22, 0, 0, 1, "Watch full video here"),
    ("12/15/2025", 46, 0, 0, 1, "The best founders obsess over product and finance"),
    ("12/15/2025", 37, 1, 0, 1, "ARR is easy to talk about. Cash is harder to track"),
    ("12/13/2025", 100, 1, 0, 7, "JustPaid is hiring new engineers"),
    ("12/12/2025", 32, 0, 0, 3, "Watch full video here"),
    ("12/11/2025", 28, 0, 0, 0, "Invoices paid within 7 days of issue have a 3x higher chance"),
    ("12/11/2025", 39, 0, 0, 0, "LLMs + crypto = insane power"),
    ("12/10/2025", 37, 0, 0, 1, "Before JustPaid: 4 tools, 7 spreadsheets, Manual reminders"),
    ("12/10/2025", 87, 0, 0, 1, "ai is noisy, especially for smbs"),
    ("12/10/2025", 136, 0, 0, 0, "A powerful idea from Prasanna Sankar"),
    ("12/09/2025", 372, 0, 3, 3, "We're excited to share a new conversation featuring Prasanna Sankar"),
    ("12/09/2025", 85, 0, 0, 0, "A one shot prompt from Nano Banana for JustPaid"),
    # Batch 2: Nov 11 - Dec 8
    ("12/08/2025", 26, 0, 0, 2, "Happy Monday! If your calendar already looks like a battlefield"),
    ("12/08/2025", 454, 0, 1, 1, "What is JustPaid in 2 minutes"),
    ("12/08/2025", 26, 0, 0, 1, "A must watch"),
    ("12/07/2025", 99, 0, 0, 0, "We are hiring full stack engineers with 5+ years experience"),
    ("12/05/2025", 62, 0, 0, 1, "Our latest blog breaks down how automation isn't a nice-to-have"),
    ("12/05/2025", 25, 0, 0, 1, "Friday Finance tip: If your inbox has become your AR system"),
    ("12/05/2025", 16, 0, 0, 0, "Deconstructing Finance"),
    ("12/04/2025", 288, 0, 1, 1, "Finance math is wild"),
    ("12/04/2025", 22, 0, 0, 0, "If finance teams could write a wishlist to Santa"),
    ("12/03/2025", 51, 0, 0, 2, "Finance teams aren't adopting AI for innovation"),
    ("12/03/2025", 49, 0, 0, 0, "Every finance team has a hidden workload no one talks about"),
    ("12/03/2025", 196, 0, 1, 1, "The AI journal. Why modern CFOs are rebuilding revenue ops"),
    ("12/03/2025", 44, 0, 0, 1, "The JustPaid platform has many options available to you"),
    ("12/02/2025", 41, 0, 0, 1, "building on justpaid, don't worry we have an api"),
    ("11/27/2025", 103, 0, 0, 1, "We sat down with Prasanna - the founder behind Rippling"),
    ("11/24/2025", 45, 0, 0, 0, "Tip of the week: If a customer does not want to auto-renew"),
    ("11/21/2025", 153, 0, 1, 1, "How much time does your finance team spend on RPO reporting"),
    ("11/21/2025", 42, 0, 0, 0, "Introducing: Finance Automation Meets Decision Intelligence!"),
    ("11/19/2025", 979, 0, 2, 2, "Love this!"),
    ("11/11/2025", 36, 0, 0, 0, "How we think at JustPaid about the future of billing"),
    # Batch 3: Oct 1 - Nov 8
    ("11/08/2025", 43, 0, 0, 0, "Exploring OpenAI's Sora 2 and the transformative impact of AI"),
    ("11/07/2025", 30, 0, 0, 1, "Part of the JustPaid team"),
    ("11/07/2025", 78, 0, 0, 0, "what we do is auto debit right after the invoice is sent"),
    ("11/07/2025", 43, 0, 0, 0, "Why 90% of Companies Calculate Invoice Proration Wrong"),
    ("11/06/2025", 36, 0, 0, 0, "justpaid isn't just software, it's your ar agent persona"),
    ("11/06/2025", 55, 0, 0, 0, "when a customer pays, our ai knows instantly"),
    ("11/05/2025", 31, 0, 0, 0, "here's the thing about contracts - start with clarity"),
    ("11/05/2025", 29, 0, 0, 1, "we use our own product to bill our own customers"),
    ("11/05/2025", 31, 0, 0, 0, "Automated AR Collections, Accounts Receivable with JustPaid"),
    ("11/04/2025", 29, 0, 0, 0, "Check out healthcare startups using JustPaid!"),
    ("11/03/2025", 17, 0, 0, 0, "Love seeing this about JustPaid"),
    ("10/21/2025", 168, 0, 1, 1, "Only in San Francisco would you find billboards advertising billing"),
    ("10/20/2025", 53, 0, 0, 0, "JustPaid is presenting at Operators Guild Demo Day 2025"),
    ("10/20/2025", 67, 0, 0, 1, "Excited JustPaid was selected at Operators Guild demo day"),
    ("10/17/2025", 51, 0, 0, 1, "Excited to share that JustPaid launched on Product Hunt"),
    ("10/06/2025", 54, 0, 0, 2, "This research reinforces what we see every day: AI can transform"),
    ("10/06/2025", 118, 2, 0, 3, "Thrilled to share that research at JustPaid was featured in Forbes"),
    ("10/02/2025", 57, 0, 0, 2, "This laptop is running a transformer that predicts the next token"),
    ("10/01/2025", 45, 0, 0, 1, "JustPaid's new case studies page"),
    ("10/01/2025", 46, 0, 0, 2, "JustPaid is an AI billing software that automates invoices"),
]


def main():
    rows = []
    for i, (date_str, views, replies, retweets, likes, text) in enumerate(RAW):
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        published = dt.strftime("%Y-%m-%dT12:00:00")

        rows.append({
            "post_id": f"tw_q4_{dt.strftime('%Y%m%d')}_{i}",
            "platform": "Twitter",
            "title": text,
            "post_type": "Post",
            "url": "",
            "views": views,
            "likes": likes,
            "comments": replies,
            "shares": retweets,
            "published_at": published,
        })

    print(f"Inserting {len(rows)} Twitter Q4 2025 posts into BigQuery...")
    insert_posts(rows)
    print("Done!")


if __name__ == "__main__":
    main()
