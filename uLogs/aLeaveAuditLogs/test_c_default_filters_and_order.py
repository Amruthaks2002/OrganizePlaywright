"""LAL-002: Default filters and row order on a fresh session.

Steps:
1. Log in as admin in a new browser (filters are kept in the session, so a new session shows the defaults).
2. Open Leave Audit Logs.

Expected:
- From Date / To Date are the first and last day of the current month.
- Employee, Action Status and Description / Details are empty.
- At most 20 rows are shown, every row is dated in the current month, and rows are newest first.
"""
import json
import time
from datetime import date, timedelta

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


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    return page_props(page)


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


def current_month_bounds():
    today = date.today()
    first = today.replace(day=1)
    last = (first + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return first.isoformat(), last.isoformat()


def test_lal_002_default_filters_and_order():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_leave_audit_logs(page)
        first, last = current_month_bounds()

        assert page.locator("input[type='date']").first.input_value() == first
        assert page.locator("input[type='date']").last.input_value() == last
        assert page.locator(".vs__selected").count() == 0, "a dropdown filter is pre-selected"
        assert page.locator("input[placeholder='Search text...']").input_value() == ""

        props = props_at(page, LOGS_URL)
        assert props["filters"] == {"employee_id": None, "from_date": first, "to_date": last,
                                    "status": None, "search": None}, props["filters"]

        logs = props["logs"]["data"]
        assert len(logs) <= 20
        assert len(table_rows(page)) == len(logs)
        assert all(first <= log["created_at"][:10] <= last for log in logs), "a row outside the current month"
        created = [log["created_at"] for log in logs]
        assert created == sorted(created, reverse=True), "rows are not newest first"

        browser.close()
