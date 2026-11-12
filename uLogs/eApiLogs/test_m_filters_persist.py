"""API-013: Filters survive paging and a reload.

Steps:
1. Open API Logs, set the dates to cover all time and Outcome = Success (several pages).
2. Go to page 2.
3. Select Service = ATS · User Sync while on page 2.
4. Reload the page.

Expected: page 2 still only has Success rows; changing a filter goes back to page 1; after the reload the same
filters apply and the boxes show them.
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


def pagination(page):
    return page.locator("nav").filter(has=page.locator("a[href*='page=']")).last


def test_api_013_filters_persist():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_api_logs(page)

        start, end = "2000-01-01", date.today().isoformat()
        set_dates(page, start, end)
        props = refresh(page, lambda: outcome_select(page).select_option(value="success"))
        assert props["apiLogs"]["last_page"] >= 2

        props = refresh(page, lambda: pagination(page).get_by_role("link", name="2", exact=True).click())
        assert props["apiLogs"]["current_page"] == 2
        assert props["filters"].get("outcome") == "success", props["filters"]
        assert all(row["outcome"].lower() == "success" for row in table_rows(page))

        props = refresh(page, lambda: service_select(page).select_option(value="ats.user_sync"))
        assert props["apiLogs"]["current_page"] == 1, "changing a filter didn't go back to page 1"

        page.reload()
        wait_for_list(page)
        props = page_props(page)
        assert props["filters"].get("outcome") == "success" and props["filters"].get("service_name") == "ats.user_sync", props["filters"]
        assert outcome_select(page).input_value() == "success"
        assert service_select(page).input_value() == "ats.user_sync"
        assert (from_date(page).input_value(), to_date(page).input_value()) == (start, end)

        browser.close()
