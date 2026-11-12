"""API-012: Reset clears every filter.

Steps:
1. Open API Logs and note the starting dates.
2. Search "admin", select Service = ATS · User Sync, Outcome = Success and dates covering all time.
3. Click Reset.

Expected: Search, Service and Outcome are empty again, the dates are back to the starting ones, and the rows match
loading the page with just those dates.
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


def test_api_012_reset_clears_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_api_logs(page)
        start_dates = (from_date(page).input_value(), to_date(page).input_value())

        refresh(page, lambda: page.locator(SEARCH).fill("admin"))
        refresh(page, lambda: service_select(page).select_option(value="ats.user_sync"))
        refresh(page, lambda: outcome_select(page).select_option(value="success"))
        set_dates(page, "2000-01-01", date.today().isoformat())

        props = refresh(page, lambda: page.get_by_role("button", name="Reset").click())
        filters = props["filters"]
        assert not filters.get("search") and not filters.get("service_name") and not filters.get("outcome"), filters
        assert (filters.get("start_date"), filters.get("end_date")) == start_dates, filters
        assert page.locator(SEARCH).input_value() == ""
        assert service_select(page).input_value() == "" and outcome_select(page).input_value() == ""
        assert (from_date(page).input_value(), to_date(page).input_value()) == start_dates

        expected = props_at(page, list_url(start_date=start_dates[0], end_date=start_dates[1]))["apiLogs"]["total"]
        assert props["apiLogs"]["total"] == expected

        browser.close()
