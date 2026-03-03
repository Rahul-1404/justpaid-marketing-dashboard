"""Insert scraped Q4 2025 Instagram posts into BigQuery."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from storage.bigquery_client import insert_posts

# Scraped from Instagram API (Oct 1 - Dec 31, 2025)
# Format: (date, media_type, caption, likes, comments, views)
# media_type: 1=Image, 2=Video/Reel, 8=Carousel
RAW = [
    # Page 4 (Dec 17-19)
    ("12/19/2025", 2, "Talk on Finance with Armand Zand - Full video on Youtube", 2, 0, 72),
    ("12/18/2025", 2, "Talk on Finance with Armand Zand - Full video on youtube", 2, 0, 99),
    ("12/17/2025", 2, "If an invoice isn't collectible, it isn't revenue", 2, 0, 82),
    # Page 5 (Dec 5-16)
    ("12/16/2025", 2, "Watch full video here", 2, 0, 152),
    ("12/15/2025", 2, "ARR is easy to talk about. Cash is harder to track", 2, 1, 152),
    ("12/13/2025", 2, "JustPaid is hiring new engineers", 3, 1, 25),
    ("12/12/2025", 2, "Watch Full Video here on Youtube", 2, 0, 123),
    ("12/11/2025", 2, "LLMs + crypto = insane power", 2, 0, 102),
    ("12/10/2025", 2, "A powerful idea from Prasanna Sankar", 3, 0, 166),
    ("12/10/2025", 1, "ai is noisy, especially for smbs", 1, 0, 0),
    ("12/09/2025", 1, "New conversation featuring the future of startups", 1, 0, 0),
    ("12/09/2025", 2, "Something we see a lot with our justpaid customers", 1, 1, 43),
    ("12/05/2025", 1, "The Hidden Drain on Finance And the Intelligence to Fix It", 1, 0, 0),
    ("12/05/2025", 1, "The founders talk about the future of finance", 4, 0, 0),
    ("12/05/2025", 1, "A must watch. On the JustPaid Podcast on YouTube", 3, 0, 0),
    # Page 6 (Nov 7 - Dec 4)
    ("12/04/2025", 1, "Finance math is wild", 2, 0, 0),
    ("12/04/2025", 1, "If finance teams could write a wishlist to Santa", 3, 0, 0),
    ("12/04/2025", 2, "Modern CFOs are moving beyond spreadsheet AR", 2, 0, 21),
    ("12/04/2025", 1, "Finance teams aren't adopting AI for innovation", 0, 0, 0),
    ("12/03/2025", 1, "Every finance team has a hidden workload no one talks about", 2, 0, 0),
    ("12/02/2025", 1, "The JustPaid platform has many options available", 2, 0, 0),
    ("12/02/2025", 2, "Building on JustPaid? Don't worry, we have an API", 0, 0, 26),
    ("11/27/2025", 2, "We sat down with Prasanna S - the founder behind RippleX", 2, 0, 106),
    ("11/19/2025", 2, "Just dropped the feature finance people have been waiting for", 2, 0, 206),
    ("11/11/2025", 2, "How we think at JustPaid about the future of billing", 3, 0, 26),
    ("11/11/2025", 1, "justpaid has auto-debit built in for companies", 1, 0, 0),
    ("11/07/2025", 2, "Setting up your reminders with your own domain", 2, 0, 167),
    # Page 7 (Oct 28 - Nov 7)
    ("11/07/2025", 2, "Most people setting up billing software are terrified", 0, 0, 266),
    ("11/07/2025", 2, "Contract billing is broken at most companies", 1, 0, 42),
    ("11/05/2025", 1, "Part of the JustPaid team", 6, 0, 0),
    ("11/05/2025", 2, "What we do is auto debit right after the invoice is sent", 1, 0, 33),
    ("11/05/2025", 2, "justpaid isn't just software, it's your ar agent", 2, 0, 219),
    ("11/05/2025", 2, "When a customer pays, our ai knows instantly", 2, 0, 185),
    ("11/05/2025", 2, "Here's the thing about contracts", 3, 0, 198),
    ("11/05/2025", 2, "Here's how we build at justpaid - we use our own product", 2, 0, 17),
    ("11/03/2025", 1, "Love seeing this about JustPaid", 4, 0, 0),
    ("10/28/2025", 1, "JustPaid highlights", 2, 0, 0),
    ("10/28/2025", 1, "Vinay and Juan", 3, 0, 0),
    ("10/28/2025", 1, "We were in Accounting Today for our new course", 1, 0, 0),
    # Page 8 (Oct 1-20)
    ("10/20/2025", 1, "Excited JustPaid was selected at Operators Guild Demo Day", 2, 0, 0),
    ("10/17/2025", 2, "Platform walk-through in five minutes", 1, 0, 26),
    ("10/16/2025", 8, "We hit the top of ProductHunt", 5, 1, 0),
    ("10/02/2025", 2, "Ever wondered how large language models work?", 0, 0, 221),
    ("10/01/2025", 2, "JustPaid launched a new case studies page", 2, 0, 46),
    ("10/01/2025", 2, "Looking for AI to handle billing? JustPaid automates it", 6, 1, 185),
]


def main():
    rows = []
    for i, (date_str, media_type, caption, likes, comments, views) in enumerate(RAW):
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        published = dt.strftime("%Y-%m-%dT12:00:00")

        # Map Instagram media types to dashboard types
        type_map = {1: "Post", 2: "Reel", 8: "Carousel"}
        mapped_type = type_map.get(media_type, "Post")

        rows.append({
            "post_id": f"ig_q4_{dt.strftime('%Y%m%d')}_{i}",
            "platform": "Instagram",
            "title": caption,
            "post_type": mapped_type,
            "url": "",
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": 0,
            "published_at": published,
        })

    print(f"Inserting {len(rows)} Instagram Q4 2025 posts into BigQuery...")
    insert_posts(rows)
    print("Done!")


if __name__ == "__main__":
    main()
