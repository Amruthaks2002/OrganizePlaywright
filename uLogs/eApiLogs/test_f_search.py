"""API-006: Search by user name, email or reference.

Steps:
1. Open API Logs over all time and take an entry that has a reference.
2. Search for: its reference; its reference in lower case; part of its user's name in upper case; the user's
   email (Admin User -> admin@example.com).

Expected: each search finds the entry, and every row matches the text (in user, triggered by or reference).
"""
import json
import time
from datetime import date
from urllib.parse import urlencode, urlparse

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


def wait_for_list(page):
    page.get_by_role("heading", name="API Logs").wait_for(state="visible")
    time.sleep(1)


def open_api_logs(page):
    """Logs in as admin and opens Logs > API Log from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-api-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    wait_for_list(page)


def refresh(page, action):
    """Runs a filter action and returns the props of the list reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: urlparse(r.url).path == "/api-logs" and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    return info.value.json()["props"]


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


COLUMNS = ["time", "service", "user", "outcome", "http", "duration", "triggered_by", "reference"]


def table_rows(page):
    """Visible API log rows as dicts (the empty state has a single cell and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != len(COLUMNS):
            continue
        rows.append({key: cells.nth(i).inner_text().strip() for i, key in enumerate(COLUMNS)})
    return rows


def from_date(page):
    return page.locator("input[type='date']").first


def to_date(page):
    return page.locator("input[type='date']").last


def set_dates(page, start, end):
    """Sets the From/To boxes (in an order that never makes From later than To) and returns the last reload's props,
    or None when both already held those values."""
    props = None
    boxes = [(from_date(page), start), (to_date(page), end)]
    if to_date(page).input_value() and start > to_date(page).input_value():
        boxes.reverse()
    for box, value in boxes:
        if box.input_value() != value:
            props = refresh(page, lambda: box.fill(value))
    return props


def test_api_006_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_api_logs(page)

        props = set_dates(page, "2000-01-01", date.today().isoformat())
        sample = next((log for log in props["apiLogs"]["data"] if log["reference"] and log["user_name"] == "Admin User"), None)
        assert sample, "no Admin User entry with a reference on page 1"
        box = page.locator(SEARCH)

        for text in [sample["reference"], sample["reference"].lower(), "ADMIN US", "admin@example.com"]:
            props = refresh(page, lambda: box.fill(text))
            found = [log["id"] for log in props["apiLogs"]["data"]]
            assert props["apiLogs"]["total"] > 0, f"'{text}' found nothing"
            if text.lower() == sample["reference"].lower():
                assert found == [sample["id"]], f"'{text}' found {found}"
            for row in table_rows(page):
                if text != "admin@example.com":
                    assert text.lower() in " ".join([row["user"], row["triggered_by"], row["reference"]]).lower(), row
                else:
                    assert "Admin User" in (row["user"], row["triggered_by"]), row

        browser.close()
