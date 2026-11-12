"""ML-018: From Date later than To Date.

Steps:
1. Open Mail Logs.
2. Set From Date = 20 days ago and To Date = 25 days ago.

Expected: the page stops it: either To Date doesn't allow a date before From Date (min attribute), or a validation
message explains the range is invalid. It should not just show an empty table.

Known bug: the range is accepted silently and the table only says "No mail has been sent yet." This test fails
until that's fixed.
"""
import re
import time
from datetime import date, timedelta
from urllib.parse import urlparse

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


VALIDATION = re.compile(r"(must be|cannot be|can't be|should be).*(after|before|earlier|later)|invalid date range", re.I)


def test_ml_018_from_after_to():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_mail_logs(page)

        start = (date.today() - timedelta(days=20)).isoformat()
        end = (date.today() - timedelta(days=25)).isoformat()
        refresh(page, lambda: from_date(page).fill(start))
        try:
            refresh(page, lambda: to_date(page).fill(end))
        except Exception:
            pass  # no reload means the page refused the range itself

        blocked = to_date(page).get_attribute("min") == start or to_date(page).input_value() != end
        message = page.get_by_text(VALIDATION).count() > 0
        assert blocked or message, "From Date after To Date was accepted with no validation"

        browser.close()
