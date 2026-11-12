"""LAL-029: The Description / Details search.

Steps:
1. Open Leave Audit Logs, widen the dates to the year up to yesterday and note the total.
2. Type "restored" in Description / Details.
3. Type "RESTORED" instead.
4. Clear the box.

Expected: every row's description contains "restored"; the upper-case search gives the same total;
clearing it brings back the original total.
"""
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


def refresh(page, action):
    """Runs a filter action and returns the props of the reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: "/leave-logs" in r.url and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    return info.value.json()["props"]


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
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def test_lal_029_description_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_leave_audit_logs(page)
        total = set_dates(page, *wide_range())["logs"]["total"]
        box = page.locator("input[placeholder='Search text...']")

        props = refresh(page, lambda: box.fill("restored"))
        found = props["logs"]["total"]
        assert 0 < found < total, f"'restored' matched {found} of {total}"
        assert all("restored" in log["description"].lower() for log in props["logs"]["data"])
        assert all("restored" in row["details"].lower() for row in table_rows(page))

        props = refresh(page, lambda: box.fill("RESTORED"))
        assert props["logs"]["total"] == found, "the search is case sensitive"

        props = refresh(page, lambda: box.fill(""))
        assert props["logs"]["total"] == total

        browser.close()
