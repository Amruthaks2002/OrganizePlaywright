"""LAL-022: The "Applied via AI" badge.

Steps:
1. Log in as admin and open Leave Audit Logs over the last year (up to today).
2. Go through the first pages until a log made by the AI assistant (source "ai") is found.

Expected: rows whose source is "ai" show the "Applied via AI" badge in Description & Details; rows from the web
don't.
"""
import json
import time
from datetime import date, timedelta

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    return page_props(page)


def wide_range():
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def test_lal_022_ai_source_badge():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()
        end = date.today().isoformat()  # AI-made leaves are rare, so include today's logs too

        seen_ai = 0
        problems = []
        for number in range(1, 6):
            logs = props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}&page={number}")["logs"]["data"]
            cells = page.locator("table tbody tr td:nth-child(5)")
            for i, log in enumerate(logs):
                has_badge = cells.nth(i).get_by_text("Applied via AI").count() > 0
                is_ai = log.get("source") == "ai"
                seen_ai += is_ai
                if has_badge != is_ai:
                    problems.append(f"log {log['id']} source={log.get('source')} badge={has_badge}")
            if seen_ai:
                break
        assert seen_ai, "no AI-made log in the first 5 pages of the last year"
        assert not problems, problems

        browser.close()
