"""ML-020: Reset clears every filter.

Steps:
1. Open Mail Logs and note the dates the boxes start with.
2. Select Type = Leave Approved, Status = Sent and the year up to yesterday.
3. Click Reset.

Expected: Type and Status are back to All, the dates are back to the starting ones, and the rows match loading the
page with just those dates.
"""
import json
import time
from datetime import date, timedelta
from urllib.parse import urlencode, urlparse

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def wait_for_list(page):
    page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
    time.sleep(1)


def open_mail_logs(page):
    """Logs in as admin and opens Logs > Mail Log from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-mail-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    wait_for_list(page)


def refresh(page, action):
    """Runs a filter action and returns the props of the list reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: urlparse(r.url).path == "/mail-logs" and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    props = info.value.json()["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


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


def type_select(page):
    return page.locator("main select").first


def status_select(page):
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


def wide_range():
    """The year up to yesterday: ending yesterday so mails being sent right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def test_ml_020_reset_clears_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_mail_logs(page)
        start_dates = (from_date(page).input_value(), to_date(page).input_value())

        refresh(page, lambda: type_select(page).select_option(label="Leave Approved"))
        refresh(page, lambda: status_select(page).select_option(label="Sent"))
        set_dates(page, *wide_range())

        props = refresh(page, lambda: page.get_by_role("button", name="Reset").click())
        assert not props["filters"].get("event_type") and not props["filters"].get("status"), props["filters"]
        assert (props["filters"].get("start_date"), props["filters"].get("end_date")) == start_dates, props["filters"]
        assert type_select(page).input_value() == "" and status_select(page).input_value() == ""
        assert (from_date(page).input_value(), to_date(page).input_value()) == start_dates

        expected = props_at(page, list_url(start_date=start_dates[0], end_date=start_dates[1]))["mailLogs"]["total"]
        assert props["mailLogs"]["total"] == expected, f"Reset shows {props['mailLogs']['total']}, expected {expected}"

        browser.close()
