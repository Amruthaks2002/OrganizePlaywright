"""WM-022: The "via AI" badges.

Steps:
1. Log in as admin and open Work Mode Audit Logs over the last year (up to today).
2. Go through the first pages until a log made through the AI assistant (source "ai") is found.

Expected: rows whose source is "ai" show a "... via AI" badge in Description & Details ("Applied via AI" on
Created rows, "Approved via AI" on Approved rows); rows from the web show none.
"""
import json
import time
from datetime import date, timedelta

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/work-mode-logs"
SUBTITLE = "A complete history of all work mode-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def props_at(page, url):
    page.goto(url)
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    return page_props(page)


def wide_range():
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


EXPECTED_BADGE = {"created": "Applied via AI", "approved": "Approved via AI"}


def test_wm_022_ai_source_badge():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, _ = wide_range()
        end = date.today().isoformat()  # AI-made requests are rare, so include today's logs too

        seen_ai = 0
        problems = []
        for number in range(1, 6):
            props = props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}&page={number}")
            cells = page.locator("table tbody tr td:nth-child(5)")
            for i, log in enumerate(props["logs"]["data"]):
                badge = cells.nth(i).locator("span").filter(has_text="via AI")
                is_ai = log.get("source") == "ai"
                seen_ai += is_ai
                if is_ai and badge.count() == 0:
                    problems.append(f"log {log['id']} ({log['action']}) from AI has no badge")
                elif not is_ai and badge.count():
                    problems.append(f"log {log['id']} from {log.get('source')} shows {badge.first.inner_text()!r}")
                elif is_ai and log["action"] in EXPECTED_BADGE and badge.first.inner_text().strip() != EXPECTED_BADGE[log["action"]]:
                    problems.append(f"log {log['id']} ({log['action']}) badge says {badge.first.inner_text()!r}")
            if seen_ai or number >= props["logs"]["last_page"]:
                break
        assert seen_ai, "no AI-made log in the first 5 pages of the last year"
        assert not problems, problems

        browser.close()
