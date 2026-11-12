"""API-015: Outcome badge colours.

Steps:
1. Log in as admin and open API Logs over all time filtered to Success, then to Refused (and Failed if any).

Expected: "success" badges are green; "refused" and "failed" badges are not green (a warning/error colour), so
problems stand out.
"""
import json
import time
from datetime import date
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def all_time():
    return {"start_date": "2000-01-01", "end_date": date.today().isoformat()}


def test_api_015_outcome_badge_colours():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        problems, checked = [], []
        for outcome in ["success", "refused", "failed"]:
            props = props_at(page, list_url(outcome=outcome, **all_time()))
            if not props["apiLogs"]["total"]:
                continue
            checked.append(outcome)
            css = (page.locator("table tbody tr td:nth-child(4) span").first.get_attribute("class") or "").split()
            green = "bg-green-100" in css
            if (outcome == "success") != green:
                problems.append(f"'{outcome}' badge is {[c for c in css if c.startswith('bg-')]}")
        assert "success" in checked and len(checked) >= 2, f"only {checked} have entries"
        assert not problems, problems

        browser.close()
