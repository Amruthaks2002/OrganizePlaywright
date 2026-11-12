"""API-008: A multi-day date range, including both boundary days.

Steps:
1. Open API Logs over all time up to yesterday and take the latest day with entries.
2. Set From Date = that day minus 3 days, To Date = that day.
3. Separately load each single day of that range.

Expected: every row's date (as shown, India time) is inside the range, and the range total equals the sum of the
single-day totals.
"""
import json
import time
from datetime import date, datetime, timedelta
from urllib.parse import urlencode, urlparse
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


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a time, e.g. 12 Nov 2026, 10:07:37 AM (India time)."""
    return to_ist(created_at).strftime("%-d %b %Y, %I:%M:%S %p")


def displayed_date(timestamp):
    return datetime.strptime(timestamp.split(",")[0].strip(), "%d %b %Y").date()


def test_api_008_date_range_boundaries():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_api_logs(page)

        yesterday = (date.today() - timedelta(days=1)).isoformat()
        props = set_dates(page, "2000-01-01", yesterday)
        assert props["apiLogs"]["data"], "no entries before today"
        end = to_ist(props["apiLogs"]["data"][0]["created_at"]).date()
        start = end - timedelta(days=3)

        props = set_dates(page, start.isoformat(), end.isoformat())
        total = props["apiLogs"]["total"]
        for row in table_rows(page):
            assert start <= displayed_date(row["time"]) <= end, f"{row['time']} is outside {start}..{end}"

        per_day = 0
        for offset in range(4):
            day = (start + timedelta(days=offset)).isoformat()
            per_day += props_at(page, list_url(start_date=day, end_date=day))["apiLogs"]["total"]
        assert total == per_day, f"range total {total} != sum of single days {per_day}"

        browser.close()
