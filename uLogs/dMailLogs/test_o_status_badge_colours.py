"""ML-015: Status badge colours.

Steps:
1. Log in as admin and open Mail Logs filtered to Sent, then to Failed, over the year up to yesterday.

Expected: "sent" badges are green and "failed" badges are red, so failures stand out.

Known bug: "failed" badges are green, the same as "sent". This test fails until that's fixed.
"""
import json
import time
from datetime import date, timedelta
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    if "filters" in props:
        props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def wide_range():
    """The year up to yesterday: ending yesterday so mails being sent right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


COLOURS = {"sent": "green", "failed": "red"}


def test_ml_015_status_badge_colours():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        problems = []
        for status, colour in COLOURS.items():
            props = props_at(page, list_url(status=status, start_date=start, end_date=end))
            assert props["mailLogs"]["total"] > 0, f"no {status} mails in the year up to yesterday"
            badge = page.locator("table tbody tr td:nth-child(4) span").first
            css = (badge.get_attribute("class") or "").split()
            if f"bg-{colour}-100" not in css:
                problems.append(f"'{status}' badge is {[c for c in css if c.startswith('bg-')]}, expected {colour}")
        assert not problems, problems

        browser.close()
