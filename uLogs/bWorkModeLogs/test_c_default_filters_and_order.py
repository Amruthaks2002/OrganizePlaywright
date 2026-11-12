"""WM-002: Default filters and row order when the page opens.

Steps:
1. Log in as admin and open Work Mode Audit Logs.
2. Load the same page with the current month's dates in the URL.

Expected:
- From Date / To Date show the first and last day of the current month.
- Employee, Action Status and Description / Details are empty.
- The table shows what the date boxes say: the same rows as the current month loaded through the URL, every row
  dated in the current month, at most 20 rows, newest first.

Known bugs (this test fails until both are fixed):
- The boxes show the month shifted back a day (e.g. 31 Oct - 29 Nov instead of 1 - 30 Nov).
- The first load ignores the dates in the boxes and lists every log ever written.
"""
import json
import time
from datetime import date, timedelta

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/work-mode-logs"
SUBTITLE = "A complete history of all work mode-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def open_work_mode_logs(page):
    """Logs in as admin and opens Logs > Work Mode Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-work-mode-logs")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


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


def test_wm_002_default_filters_and_order():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_work_mode_logs(page)
        first, last = current_month_bounds()

        assert page.locator(".vs__selected").count() == 0, "a dropdown filter is pre-selected"
        assert page.locator("input[placeholder='Search text...']").input_value() == ""

        props = props_at(page, LOGS_URL)
        logs = props["logs"]["data"]
        assert len(logs) <= 20
        assert len(table_rows(page)) == len(logs)
        created = [log["created_at"] for log in logs]
        assert created == sorted(created, reverse=True), "rows are not newest first"

        problems = []
        shown = (page.locator("input[type='date']").first.input_value(), page.locator("input[type='date']").last.input_value())
        if shown != (first, last):
            problems.append(f"date boxes show {shown}, expected {(first, last)}")
        month_total = props_at(page, f"{LOGS_URL}?from_date={first}&to_date={last}")["logs"]["total"]
        if props["logs"]["total"] != month_total:
            problems.append(f"first load lists {props['logs']['total']} logs, the current month has {month_total}")
        outside = [log["created_at"] for log in logs if not first <= log["created_at"][:10] <= last]
        if outside:
            problems.append(f"rows outside the current month: {outside[:3]}")
        assert not problems, problems

        browser.close()
