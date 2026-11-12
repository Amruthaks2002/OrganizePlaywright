"""API-022: Opening Recruitment (ATS) is logged.

Steps:
1. Log in as admin and note the newest API log entry.
2. Click "Recruitment (ATS)" in the sidebar (it signs in to the ATS QC app, in a new tab or the same one).
3. Close the ATS tab (or come back) and open API Logs for today.

Expected: two new entries for Admin User, both triggered by Admin User and successful:
- "ATS · Open ATS (Sign-in)" with a reference and a GET to the ATS sign-in address.
- "ATS · User Sync" with HTTP 200/201, a duration in ms and a POST to the ATS sync address.
Both are within a few minutes of now.

Note: this signs the admin in to the ATS QC app, the same as a user clicking the link.
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


def test_api_022_ats_open_logged():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        started = datetime.now(IST)
        today = date.today().isoformat()
        before = {log["id"] for log in props_at(page, list_url(start_date=today, end_date=today))["apiLogs"]["data"]}

        page.goto(f"{BASE_URL}/dashboard")
        link = page.get_by_test_id("sidebar-navlink-recruitment (ats)")
        link.wait_for(state="visible")
        try:
            with context.expect_page(timeout=10000) as new_tab:
                link.click()
            new_tab.value.wait_for_load_state()
            new_tab.value.close()
        except Exception:
            page.wait_for_load_state()  # opened in the same tab
        time.sleep(3)

        new = [log for log in props_at(page, list_url(start_date=today, end_date=today))["apiLogs"]["data"]
               if log["id"] not in before]
        by_service = {log["service_name"]: log for log in reversed(new)}
        assert {"ats.sso_launch", "ats.user_sync"} <= set(by_service), f"new entries: {[l['service_name'] for l in new]}"

        for service, method in [("ats.sso_launch", "GET"), ("ats.user_sync", "POST")]:
            log = props_at(page, f"{LOGS_URL}/{by_service[service]['id']}")["apiLog"]
            assert log["outcome"] == "success", log
            assert log["user_name"] == "Admin User" and log["actor_name"] == "Admin User", log
            assert log["method"] == method and log["url"].startswith("https://"), log
            assert abs((to_ist(log["created_at"]) - started).total_seconds()) < 600, log["created_at"]
            if service == "ats.sso_launch":
                assert log["reference"], "the sign-in has no reference"
            else:
                assert log["http_status"] in (200, 201) and isinstance(log["duration_ms"], int), log

        browser.close()
