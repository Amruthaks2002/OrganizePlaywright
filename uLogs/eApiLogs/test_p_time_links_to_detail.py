"""API-016: The time in each row links to that entry's page.

Steps:
1. Log in as admin and open API Logs over all time.
2. Check each row's time link, then click the first one.

Expected: every time is a link to /api-logs/<entry id>, and clicking it opens that entry (service and time match).
"""
import json
import time
from datetime import date, datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

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


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a time, e.g. 12 Nov 2026, 10:07:37 AM (India time)."""
    return to_ist(created_at).strftime("%-d %b %Y, %I:%M:%S %p")


def displayed_date(timestamp):
    return datetime.strptime(timestamp.split(",")[0].strip(), "%d %b %Y").date()


def test_api_016_time_links_to_detail():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        props = props_at(page, list_url(**all_time()))
        logs = props["apiLogs"]["data"]
        for index, log in enumerate(logs):
            href = page.locator("table tbody tr").nth(index).locator("td").first.get_by_role("link").get_attribute("href")
            assert href and href.endswith(f"/api-logs/{log['id']}"), f"{log['id']} links to {href}"

        page.locator("table tbody tr").first.locator("td").first.get_by_role("link").click()
        page.get_by_role("link", name="← Back to API Logs").wait_for(state="visible")
        time.sleep(1)
        text = page.locator("main").first.inner_text()
        label = {s["value"]: s["label"] for s in props["services"]}[logs[0]["service_name"]]
        assert label in text and display_timestamp(logs[0]["created_at"]) in text, text[:300]

        browser.close()
