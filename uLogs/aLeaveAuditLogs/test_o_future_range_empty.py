"""LAL-014: A future date range shows the empty state.

Steps:
1. Open Leave Audit Logs.
2. Set From Date = 2030-01-01 and To Date = 2030-01-31.

Expected: no rows, the message "No logs found for the selected criteria." and no pagination.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def open_leave_audit_logs(page):
    """Logs in as admin and opens Logs > Leave Audit Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-leave-audit-logs")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def table_rows(page):
    """Visible log rows as dicts (the empty-state row has a single cell and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != 5:
            continue
        rows.append({
            "timestamp": cells.nth(0).inner_text().strip(),
            "employee": cells.nth(1).inner_text().strip(),
            "action_by": cells.nth(2).inner_text().strip(),
            "action": cells.nth(3).inner_text().strip(),
            "description": cells.nth(4).locator("p").first.inner_text().strip(),
            "details": cells.nth(4).inner_text().strip(),
        })
    return rows


def refresh(page, action):
    """Runs a filter action and returns the props of the reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: "/leave-logs" in r.url and r.request.method == "GET") as info:
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


def test_lal_014_future_range_empty():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_leave_audit_logs(page)

        props = set_dates(page, "2030-01-01", "2030-01-31")
        assert props["logs"]["total"] == 0
        assert table_rows(page) == []
        expect(page.get_by_text(EMPTY_MESSAGE)).to_be_visible()
        assert page.locator("a[href*='page=']").count() == 0, "pagination shown for an empty result"

        browser.close()
