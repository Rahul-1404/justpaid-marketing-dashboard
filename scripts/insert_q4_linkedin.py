"""Insert scraped Q4 2025 LinkedIn posts into BigQuery."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from storage.bigquery_client import insert_posts

# Scraped from LinkedIn admin analytics (Oct 1 - Dec 31, 2025)
# Format: (date, post_type, title, impressions, clicks, reactions, comments, reposts)
RAW = [
    # Page 1 (Dec 16-31)
    ("12/31/2025", "Article", "Sales Isn't Revenue: What Founders Get Wrong About Billing, Tracking, and Collecting", 190, 1, 9, 0, 0),
    ("12/26/2025", "Video", "Do you signup for JustPaid yet?", 151, 0, 8, 0, 0),
    ("12/19/2025", "Video", "Full Video on Youtube", 138, 1, 5, 0, 0),
    ("12/18/2025", "Article", "JustPaid Demo by Daniel Kivatinos", 109, 3, 4, 0, 0),
    ("12/18/2025", "Video", "Full video on Youtube", 90, 1, 3, 0, 1),
    ("12/17/2025", "Image", "We got around 200 registrations and gathered nearly 60 founders", 0, 0, 0, 0, 0),
    ("12/17/2025", "Video", "If an invoice isn't collectible, it isn't revenue", 133, 2, 3, 1, 0),
    ("12/17/2025", "Article", "Sales isn't Revenue | Talk on Finance with Armand Zand", 137, 0, 1, 0, 0),
    ("12/16/2025", "Article", "The Future of Startups: DAOs, Crypto, AI & Building Beyond Silicon Valley", 110, 3, 0, 0, 0),
    ("12/16/2025", "Video", "JustPaid is hiring new engineers", 347, 44, 12, 0, 1),
    ("12/16/2025", "Video", "Watch full video here", 54, 1, 1, 0, 0),
    ("12/15/2025", "Article", "Sales isn't Revenue | Talk on Finance with Armand Zand", 94, 2, 2, 1, 0),
    ("12/15/2025", "Video", "ARR is easy to talk about. Cash is harder to track", 79, 4, 3, 0, 0),
    ("12/12/2025", "Video", "Watch full video here", 69, 3, 1, 0, 0),
    ("12/11/2025", "Article", "Discovering Your Life's Purpose: Zuny Fester of JustPaid", 121, 4, 2, 0, 1),
    ("12/11/2025", "Post", "Invoices paid within 7 days of issue have a 3x higher collection rate", 119, 0, 0, 0, 0),
    ("12/11/2025", "Video", "LLMs + crypto = insane power", 53, 1, 0, 0, 0),
    ("12/10/2025", "Article", "JustPaid - AI Revenue Operations Platform", 64, 0, 3, 0, 0),
    ("12/10/2025", "Image", "ai is noisy, especially for smbs", 96, 3, 5, 0, 0),
    ("12/10/2025", "Video", "A powerful idea from Prasanna Sankar", 80, 2, 0, 0, 0),
    # Page 2 (Dec 2-9)
    ("12/9/2025", "Article", "The Future of Startups: DAOs, Crypto, AI & Building", 126, 3, 1, 0, 0),
    ("12/9/2025", "Image", "A one shot prompt from Nano Banana for JustPaid", 60, 0, 2, 0, 0),
    ("12/9/2025", "Image", "Companies with connected AR workflows recover faster", 132, 0, 0, 0, 0),
    ("12/8/2025", "Post", "Happy Monday! If your calendar already looks full", 163, 5, 2, 0, 0),
    ("12/8/2025", "Image", "What is JustPaid in 2 minutes", 65, 2, 2, 0, 0),
    ("12/8/2025", "Image", "A must watch", 66, 0, 3, 0, 1),
    ("12/7/2025", "Image", "We are hiring full stack engineers with 5+ years", 145, 11, 3, 0, 0),
    ("12/5/2025", "Article", "The Hidden Drain on Finance And the Intelligence to Fix It", 56, 0, 1, 0, 0),
    ("12/5/2025", "Post", "Friday Finance tip: If your inbox has become a graveyard", 123, 4, 2, 0, 0),
    ("12/5/2025", "Image", "Deconstructing Finance", 96, 6, 4, 0, 1),
    ("12/4/2025", "Image", "Finance math is wild", 142, 6, 6, 0, 0),
    ("12/4/2025", "Image", "If finance teams could write a wishlist to Santa", 76, 5, 1, 0, 0),
    ("12/4/2025", "Article", "The Hidden Drain on Finance And the Intelligence to Fix It", 196, 4, 4, 0, 1),
    ("12/3/2025", "Image", "Finance teams aren't adopting AI for innovation", 77, 1, 2, 0, 0),
    ("12/3/2025", "Image", "Every finance team has a hidden workload no one talks about", 96, 3, 5, 0, 1),
    ("12/3/2025", "Video", "Building on JustPaid? Don't worry, we have an API", 63, 1, 2, 0, 0),
    ("12/3/2025", "Image", "The AI journal. Why modern CFOs are rebuilding", 154, 8, 7, 0, 2),
    ("12/3/2025", "Article", "Lessons from GHC 2025: Blending Data, Storytelling", 144, 4, 4, 0, 1),
    ("12/3/2025", "Image", "The JustPaid platform has many options available", 229, 4, 8, 1, 2),
    ("12/2/2025", "Article", "Why Modern CFOs Are Rebuilding Revenue Ops from Scratch", 761, 17, 20, 8, 2),
    # Page 3 (Nov 5-25)
    ("11/25/2025", "Article", "Unbound: Shrinija's Grace Hopper Celebration Journey", 223, 4, 4, 0, 1),
    ("11/24/2025", "Post", "Tip of the week: If a customer does not want to pay", 1631, 15, 3, 0, 0),
    ("11/21/2025", "Article", "Navigating the Complexities of Remaining Performance Obligations", 320492, 98, 4, 1, 1),
    ("11/21/2025", "Image", "Introducing: Finance Automation Meets Decision Intelligence", 92, 3, 1, 0, 0),
    ("11/19/2025", "Video", "What is bill-in-advance when you upload a sales order", 254, 5, 3, 0, 1),
    ("11/19/2025", "Image", "Love this!", 147, 5, 4, 1, 1),
    ("11/15/2025", "Image", "justpaid has auto-debit built in for companies", 147, 1, 0, 0, 0),
    ("11/14/2025", "Article", "Finance Automation Meets Decision Intelligence", 281, 4, 8, 0, 1),
    ("11/12/2025", "Post", "We're excited to announce our partnership", 120, 4, 0, 0, 0),
    ("11/12/2025", "Image", "We're excited to announce our partnership", 11275, 208, 26, 5, 4),
    ("11/11/2025", "Image", "justpaid has auto-debit built in for companies", 128, 0, 1, 0, 0),
    ("11/10/2025", "Video", "Setting up your billing emails shouldn't break you", 147, 3, 1, 0, 0),
    ("11/7/2025", "Image", "Part of the JustPaid team", 377, 20, 20, 0, 1),
    ("11/7/2025", "Video", "what we do is auto debit right after the invoice", 76, 4, 4, 0, 0),
    ("11/7/2025", "Video", "Deen diving deep into how businesses handle collections", 90, 2, 3, 0, 0),
    ("11/6/2025", "Video", "justpaid isn't just software, it's your ar agent", 100, 0, 2, 0, 0),
    ("11/6/2025", "Video", "when a customer pays, our ai knows instantly", 93, 3, 2, 0, 0),
    ("11/5/2025", "Video", "here's the thing about contracts - start with clarity", 94, 0, 2, 0, 0),
    ("11/5/2025", "Video", "we use our own product to bill our own customers", 131, 6, 4, 1, 0),
    ("11/5/2025", "Video", "Automated AR Collections, Accounts Receivable", 99, 8, 4, 0, 0),
    # Page 4 (Oct 1 - Nov 4)
    ("11/4/2025", "Video", "JustPaid is presenting at Operators Guild Demo Day", 93, 1, 3, 0, 0),
    ("11/3/2025", "Image", "Excited to share that JustPaid launched on Product Hunt", 125, 0, 3, 0, 0),
    ("10/23/2025", "Article", "AI Agent Economics, The SaaS Playbook", 416, 1, 4, 0, 1),
    ("10/21/2025", "Image", "Why Founder-Led Sales Shouldn't Mean Founder-Led Billing", 222, 2, 5, 0, 0),
    ("10/20/2025", "Image", "CapTablePro is now a certified service provider", 250, 0, 5, 0, 2),
    ("10/17/2025", "Video", "We launched a new case studies page on our website", 226, 5, 10, 2, 0),
    ("10/10/2025", "Article", "Only in San Francisco", 388, 4, 5, 0, 1),
    ("10/6/2025", "Article", "Check out healthcare startups using JustPaid!", 267, 2, 0, 0, 0),
    ("10/3/2025", "Image", "Love seeing this about JustPaid", 0, 0, 0, 0, 0),
    ("10/1/2025", "Video", "Why Revenue Recovery Matters for Cash Flow", 309, 23, 6, 2, 0),
    ("10/1/2025", "Article", "JustPaid - Case Studies", 347, 8, 18, 0, 0),
    ("10/1/2025", "Video", "Discover JustPaid, an AI billing software", 187, 9, 2, 0, 0),
]


def main():
    rows = []
    for i, (date_str, post_type, title, impressions, clicks, reactions, comments, reposts) in enumerate(RAW):
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        published = dt.strftime("%Y-%m-%dT12:00:00")

        # Map LinkedIn types to dashboard types
        type_map = {"Post": "Post", "Article": "Article", "Video": "Video",
                    "Image": "Post", "Text": "Post", "Repost": "Post"}
        mapped_type = type_map.get(post_type, "Post")

        rows.append({
            "post_id": f"li_q4_{dt.strftime('%Y%m%d')}_{i}",
            "platform": "LinkedIn",
            "title": title,
            "post_type": mapped_type,
            "url": "",
            "views": impressions,
            "likes": reactions,
            "comments": comments,
            "shares": reposts,
            "published_at": published,
        })

    print(f"Inserting {len(rows)} LinkedIn Q4 2025 posts into BigQuery...")
    insert_posts(rows)
    print("Done!")


if __name__ == "__main__":
    main()
