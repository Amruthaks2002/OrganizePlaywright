"""WM-009: Every Action Status option filters correctly.

Steps:
1. Open Work Mode Audit Logs and widen the dates to the year up to yesterday.
2. Select each Action Status option in turn.

Expected: for each option, every row (in the table and in the data behind it) has that action; when there are
none, the page shows "No logs found for the selected criteria."
"""
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


def refresh(page, action):
    """Runs a filter action and returns the props of the reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: "/work-mode-logs" in r.url and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    props = info.value.json()["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


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


def status_box(page):
    return page.locator(".v-select").nth(1).locator("input.vs__search")


def pick_status(page, label):
    page.locator(".v-select").nth(1).locator(".vs__dropdown-toggle").click()
    box = status_box(page)
    box.fill(label)
    time.sleep(1)
    return refresh(page, lambda: page.get_by_role("option", name=label, exact=True).click())


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


STATUSES = ["Created", "Approved", "Rejected", "Cancelled", "Updated", "Deleted"]


def test_wm_009_each_action_status_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_work_mode_logs(page)
        set_dates(page, *wide_range())

        problems = []
        for label in STATUSES:
            props = pick_status(page, label)
            got = {log["action_label"] for log in props["logs"]["data"]}
            if got - {label}:
                problems.append(f"{label}: data has {got}")
            rows = table_rows(page)
            if props["logs"]["total"] == 0:
                if not page.get_by_text(EMPTY_MESSAGE).is_visible():
                    problems.append(f"{label}: no rows but no empty message")
            elif any(row["action"] != label for row in rows):
                problems.append(f"{label}: table shows {sorted({r['action'] for r in rows})}")
        assert not problems, problems

        browser.close()
