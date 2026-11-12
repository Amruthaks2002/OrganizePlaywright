"""API-010: From Date later than To Date.

Steps:
1. Open API Logs.
2. Set From Date = 10 days ago, then To Date = 15 days ago.

Expected: the message "The end date field must be a date after or equal to start date." is shown; after setting a
valid To Date the message goes away and the rows are inside the new range.
"""
import json
import time
from datetime import date, datetime, timedelta
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

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


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a time, e.g. 12 Nov 2026, 10:07:37 AM (India time)."""
    return to_ist(created_at).strftime("%-d %b %Y, %I:%M:%S %p")


def displayed_date(timestamp):
    return datetime.strptime(timestamp.split(",")[0].strip(), "%d %b %Y").date()


MESSAGE = "The end date field must be a date after or equal to start date."


def test_api_010_from_after_to():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_api_logs(page)

        start = date.today() - timedelta(days=10)
        end = date.today() - timedelta(days=15)
        refresh(page, lambda: from_date(page).fill(start.isoformat()))
        to_date(page).fill(end.isoformat())
        time.sleep(2)

        expect(page.get_by_text(MESSAGE)).to_be_visible()

        # fixing the range clears the message and lists that range again
        props = refresh(page, lambda: to_date(page).fill(date.today().isoformat()))
        expect(page.get_by_text(MESSAGE)).to_be_hidden()
        assert all(displayed_date(r["time"]) >= start for r in table_rows(page))

        browser.close()
