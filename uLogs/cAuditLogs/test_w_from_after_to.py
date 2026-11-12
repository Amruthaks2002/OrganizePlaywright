"""AL-023: Date From later than Date To.

Steps:
1. Open Audit Logs.
2. Set Date From = 20 days ago and Date To = 25 days ago.

Expected: the page stops it: either Date To doesn't allow a date before Date From (min attribute), or a validation
message explains the range is invalid. It should not just show an empty table.

Known bug: the range is accepted silently and the table only says "No audit logs found". This test fails until
that's fixed.
"""
import re
import time
from datetime import date, timedelta
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def open_audit_logs(page):
    """Logs in as admin and opens Logs > Audit Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-audit-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def refresh(page, action):
    """Runs a filter action and returns the props of the list reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: urlparse(r.url).path == "/audits" and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    return info.value.json()["props"]


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


def test_al_023_from_after_to():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)

        start = (date.today() - timedelta(days=20)).isoformat()
        end = (date.today() - timedelta(days=25)).isoformat()
        refresh(page, lambda: from_date(page).fill(start))
        try:
            refresh(page, lambda: to_date(page).fill(end))
        except Exception:
            pass  # no reload means the page refused the range itself

        blocked = to_date(page).get_attribute("min") == start or to_date(page).input_value() != end
        message = page.get_by_text(VALIDATION).count() > 0
        assert blocked or message, "Date From after Date To was accepted with no validation"

        browser.close()
