"""API-011: Search, Service, Outcome and dates together.

Steps:
1. Open API Logs over all time and take the newest entry with a reference as the sample.
2. Filter by its service, its outcome, its day (From = To) and search its user's name.

Expected: the sample is still listed and every row matches all filters.
"""
import json
import time
from datetime import date, datetime
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


def service_select(page):
    return page.locator("main select").first


def outcome_select(page):
    return page.locator("main select").last


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


def test_api_011_all_filters_combined():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_api_logs(page)

        props = set_dates(page, "2000-01-01", date.today().isoformat())
        sample = next(log for log in props["apiLogs"]["data"] if log["user_name"])
        labels = {s["value"]: s["label"] for s in props["services"]}
        day = to_ist(sample["created_at"]).date().isoformat()

        refresh(page, lambda: service_select(page).select_option(value=sample["service_name"]))
        refresh(page, lambda: outcome_select(page).select_option(value=sample["outcome"]))
        set_dates(page, day, day)
        props = refresh(page, lambda: page.locator(SEARCH).fill(sample["user_name"]))

        assert sample["id"] in [log["id"] for log in props["apiLogs"]["data"]], "the sample was filtered out"
        for row in table_rows(page):
            assert row["service"] == labels[sample["service_name"]], row
            assert row["outcome"].lower() == sample["outcome"], row
            assert displayed_date(row["time"]).isoformat() == day, row
            assert sample["user_name"].lower() in (row["user"] + " " + row["triggered_by"]).lower(), row

        browser.close()
