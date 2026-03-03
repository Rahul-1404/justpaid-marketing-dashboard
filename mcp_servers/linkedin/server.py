"""
LinkedIn Analytics MCP Server

Scrapes LinkedIn company analytics via Playwright browser automation.
Provides on-demand "real-time" data without needing LinkedIn API approval.

Uses headed Chrome (brief visible window) since LinkedIn blocks headless browsers.
On first run, use --login to authenticate. After that, cookies persist.

Usage:
    First-time setup:  python server.py --login
    Run as MCP server: python server.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

LINKEDIN_ORG_ID = os.getenv("LINKEDIN_ORG_ID", "89623165")
BROWSER_DATA_DIR = Path(__file__).parent / ".browser_data"
COOKIE_FILE = Path(__file__).parent / ".cookies.json"
COMPANY_ADMIN_URL = f"https://www.linkedin.com/company/{LINKEDIN_ORG_ID}/admin"

mcp = FastMCP("linkedin-analytics")


async def _get_browser(headed: bool = True):
    """Launch Playwright with persistent context.

    LinkedIn blocks headless Chrome, so we use headed mode by default.
    The Chrome window appears briefly during scraping, then closes.
    """
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    context = await pw.chromium.launch_persistent_context(
        user_data_dir=str(BROWSER_DATA_DIR),
        channel="chromium",
        headless=not headed,
        viewport={"width": 1280, "height": 900},
        args=["--window-position=-2000,-2000"] if headed else [],  # off-screen
    )
    return pw, context


async def _navigate_and_wait(page, url: str, timeout: int = 30_000):
    """Navigate to URL and wait for page to settle."""
    await page.goto(url, timeout=timeout, wait_until="domcontentloaded")
    await asyncio.sleep(4)  # let LinkedIn JS render


async def _check_logged_in(page) -> bool:
    """Check if we're on a logged-in LinkedIn page."""
    url = page.url
    if "authwall" in url or "login" in url:
        return False
    title = await page.title()
    if "Sign" in title and "Up" in title:
        return False
    return True


async def _login_interactive():
    """Launch visible browser for user to log into LinkedIn manually."""
    from playwright.async_api import async_playwright

    print("Launching browser for LinkedIn login...", file=sys.stderr)

    pw = await async_playwright().start()
    context = await pw.chromium.launch_persistent_context(
        user_data_dir=str(BROWSER_DATA_DIR),
        channel="chromium",
        headless=False,
        viewport={"width": 1280, "height": 900},
    )
    page = await context.new_page()
    await page.goto("https://www.linkedin.com/login")

    try:
        await page.wait_for_url("**/feed/**", timeout=300_000)
        print("Login successful!", file=sys.stderr)
        await asyncio.sleep(3)
    except Exception:
        print("Login timed out or was cancelled.", file=sys.stderr)
    finally:
        await context.close()
        await pw.stop()

    print("Session saved.", file=sys.stderr)


@mcp.tool()
async def get_follower_count() -> str:
    """Get the current LinkedIn follower count for the JustPaid company page.

    Opens a brief Chrome window to scrape the admin dashboard.
    Returns JSON with the follower count and timestamp.
    """
    pw, context = await _get_browser()
    try:
        page = await context.new_page()
        await _navigate_and_wait(page, f"{COMPANY_ADMIN_URL}/analytics/followers/")

        if not await _check_logged_in(page):
            return json.dumps({"error": "Not logged in. Run: python server.py --login"})

        followers = await page.evaluate("""
            () => {
                const text = document.body.innerText;
                const match = text.match(/(\\d[\\d,]+)\\s*(?:Total followers|followers)/i);
                if (match) return match[1];
                const els = document.querySelectorAll('h2, [class*="count"], [class*="metric"]');
                for (const el of els) {
                    const t = el.textContent.trim();
                    if (/^[\\d,]+$/.test(t) && parseInt(t.replace(/,/g, '')) > 100) return t;
                }
                return null;
            }
        """)

        await page.close()
        return json.dumps({
            "platform": "LinkedIn",
            "org_id": LINKEDIN_ORG_ID,
            "followers": followers or "Could not extract",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, indent=2)
    finally:
        await context.close()
        await pw.stop()


@mcp.tool()
async def get_content_analytics(days: int = 30) -> str:
    """Get LinkedIn content analytics (impressions, reactions, comments).

    Opens a brief Chrome window to scrape the content analytics page.

    Args:
        days: Number of days to look back (default 30)

    Returns:
        JSON with content performance summary and individual post data.
    """
    pw, context = await _get_browser()
    try:
        page = await context.new_page()
        await _navigate_and_wait(page, f"{COMPANY_ADMIN_URL}/analytics/updates/")

        if not await _check_logged_in(page):
            return json.dumps({"error": "Not logged in. Run: python server.py --login"})

        summary = await page.evaluate("""
            () => {
                const text = document.body.innerText;
                const r = {};
                const imp = text.match(/(\\d[\\d,]*)\\s*(?:Impressions|impressions)/);
                if (imp) r.impressions = imp[1];
                const react = text.match(/(\\d[\\d,]*)\\s*(?:Reactions|reactions)/);
                if (react) r.reactions = react[1];
                const comm = text.match(/(\\d[\\d,]*)\\s*(?:Comments|comments)/);
                if (comm) r.comments = comm[1];
                const rep = text.match(/(\\d[\\d,]*)\\s*(?:Reposts|reposts)/);
                if (rep) r.reposts = rep[1];
                return r;
            }
        """)

        posts = await page.evaluate("""
            () => {
                const rows = document.querySelectorAll('table tbody tr');
                return Array.from(rows).map(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 4) return null;
                    return {
                        title: cells[0]?.textContent?.trim()?.substring(0, 120),
                        post_type: cells[1]?.textContent?.trim(),
                        audience: cells[2]?.textContent?.trim(),
                        impressions: cells[3]?.textContent?.trim(),
                    };
                }).filter(Boolean);
            }
        """)

        await page.close()
        return json.dumps({
            "platform": "LinkedIn",
            "org_id": LINKEDIN_ORG_ID,
            "period_days": days,
            "summary": summary,
            "posts": posts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, indent=2)
    finally:
        await context.close()
        await pw.stop()


@mcp.tool()
async def get_visitor_analytics() -> str:
    """Get LinkedIn page visitor analytics (page views, unique visitors).

    Returns JSON with visitor metrics.
    """
    pw, context = await _get_browser()
    try:
        page = await context.new_page()
        await _navigate_and_wait(page, f"{COMPANY_ADMIN_URL}/analytics/visitors/")

        if not await _check_logged_in(page):
            return json.dumps({"error": "Not logged in. Run: python server.py --login"})

        metrics = await page.evaluate("""
            () => {
                const text = document.body.innerText;
                const r = {};
                const pv = text.match(/(\\d[\\d,]*)\\s*(?:Page views|page views)/);
                if (pv) r.page_views = pv[1];
                const uv = text.match(/(\\d[\\d,]*)\\s*(?:Unique visitors|unique visitors)/);
                if (uv) r.unique_visitors = uv[1];
                const bc = text.match(/(\\d[\\d,]*)\\s*(?:Custom button clicks|button clicks)/);
                if (bc) r.button_clicks = bc[1];
                return r;
            }
        """)

        await page.close()
        return json.dumps({
            "platform": "LinkedIn",
            "org_id": LINKEDIN_ORG_ID,
            "visitors": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, indent=2)
    finally:
        await context.close()
        await pw.stop()


@mcp.tool()
async def refresh_bigquery_data() -> str:
    """Scrape LinkedIn analytics and insert fresh data into BigQuery.

    Full collection cycle: scrapes followers, content analytics,
    then inserts channel metrics and posts into BigQuery.
    """
    sys.path.insert(0, str(PROJECT_ROOT))
    from storage.bigquery_client import insert_channel_metrics, insert_posts

    pw, context = await _get_browser()
    try:
        page = await context.new_page()

        # 1. Followers
        await _navigate_and_wait(page, f"{COMPANY_ADMIN_URL}/analytics/followers/")
        if not await _check_logged_in(page):
            return json.dumps({"error": "Not logged in. Run: python server.py --login"})

        followers = await page.evaluate("""
            () => {
                const text = document.body.innerText;
                const m = text.match(/(\\d[\\d,]+)\\s*(?:Total followers|followers)/i);
                if (m) return parseInt(m[1].replace(/,/g, ''));
                const nums = [...text.matchAll(/\\b(\\d{1,3}(?:,\\d{3})+|\\d{4,})\\b/g)];
                const vals = nums.map(n => parseInt(n[1].replace(/,/g, '')));
                const big = vals.filter(n => n > 100 && n < 1000000);
                return big.length ? Math.max(...big) : 0;
            }
        """)

        # 2. Content analytics
        await _navigate_and_wait(page, f"{COMPANY_ADMIN_URL}/analytics/updates/")

        content = await page.evaluate("""
            () => {
                const text = document.body.innerText;
                const s = {};
                const imp = text.match(/(\\d[\\d,]*)\\s*(?:Impressions|impressions)/);
                s.impressions = imp ? parseInt(imp[1].replace(/,/g, '')) : 0;
                const react = text.match(/(\\d[\\d,]*)\\s*(?:Reactions|reactions)/);
                s.reactions = react ? parseInt(react[1].replace(/,/g, '')) : 0;
                const comm = text.match(/(\\d[\\d,]*)\\s*(?:Comments|comments)/);
                s.comments = comm ? parseInt(comm[1].replace(/,/g, '')) : 0;

                const rows = document.querySelectorAll('table tbody tr');
                s.post_count = rows.length;

                const posts = Array.from(rows).map(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length < 4) return null;
                    const titleEl = cells[0]?.querySelector('a');
                    return {
                        title: (titleEl?.textContent?.trim() || cells[0]?.textContent?.trim() || '').substring(0, 200),
                        post_type: cells[1]?.textContent?.trim() || 'Post',
                        impressions: parseInt((cells[3]?.textContent?.trim() || '0').replace(/[^0-9]/g, '')) || 0,
                    };
                }).filter(Boolean);

                return { summary: s, posts };
            }
        """)

        await page.close()

        # 3. Insert into BigQuery
        now = datetime.now(timezone.utc)
        s = content.get("summary", {})

        eng_rate = 0
        if s.get("impressions", 0) > 0:
            eng_rate = round((s["reactions"] + s["comments"]) / s["impressions"] * 100, 2)

        insert_channel_metrics([{
            "date": now.strftime("%Y-%m-%d"),
            "platform": "LinkedIn",
            "followers": followers,
            "follower_change": 0,
            "total_posts": s.get("post_count", 0),
            "new_posts": 0,
            "total_views": s.get("impressions", 0),
            "total_likes": s.get("reactions", 0),
            "total_comments": s.get("comments", 0),
            "engagement_rate": eng_rate,
            "collected_at": now.isoformat(),
        }])

        post_rows = []
        for i, p in enumerate(content.get("posts", [])):
            post_rows.append({
                "post_id": f"li_{now.strftime('%Y%m%d')}_{i}",
                "platform": "LinkedIn",
                "title": p.get("title", "Untitled"),
                "post_type": p.get("post_type", "Post"),
                "url": f"https://www.linkedin.com/company/{LINKEDIN_ORG_ID}/",
                "views": p.get("impressions", 0),
                "likes": 0, "comments": 0, "shares": 0,
                "published_at": now.isoformat(),
                "collected_at": now.isoformat(),
            })

        if post_rows:
            insert_posts(post_rows)

        return json.dumps({
            "status": "success",
            "followers": followers,
            "impressions": s.get("impressions", 0),
            "reactions": s.get("reactions", 0),
            "comments": s.get("comments", 0),
            "posts_inserted": len(post_rows),
            "timestamp": now.isoformat(),
        }, indent=2)

    finally:
        await context.close()
        await pw.stop()


def main():
    if "--login" in sys.argv:
        asyncio.run(_login_interactive())
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
