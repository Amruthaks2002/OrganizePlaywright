"""LAL-012: Only one of From Date / To Date set.

Steps:
1. Open Leave Audit Logs. Note how many logs exist up to today (from 2000-01-01 to today).
2. Set To Date = today and clear From Date.
3. Set From Date = the 5th of the current month and clear To Date.

Expected:
- With only To Date set, every log up to today is listed (older months included), and the From box stays empty.
- With only From Date set, every row is on or after that day, and the To box stays empty.

Known bug: a cleared date box is silently replaced by the current month's boundary on the server (From falls
back to the 1st of the month, To to the month end), so older logs disappear while the box looks empty.
This test fails until that's fixed.
"""
import json
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

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


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a log time, e.g. 10 Nov, 2026, 03:02 PM (India time)."""
    return to_ist(created_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    """The date part of a displayed timestamp."""
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


def test_lal_012_single_date_bound():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        today = date.today()
        everything = props_at(page, f"{LOGS_URL}?from_date=2000-01-01&to_date={today.isoformat()}")["logs"]["total"]
        page.get_by_role("button", name="Reset").click()
        time.sleep(2)

        # only To Date
        set_dates(page, today.replace(day=1).isoformat(), today.isoformat())
        props = refresh(page, lambda: from_date(page).fill(""))
        assert from_date(page).input_value() == ""
        assert props["logs"]["total"] == everything, \
            f"To-only shows {props['logs']['total']} logs, expected all {everything} up to today " \
            f"(the server used from_date={props['filters']['from_date']})"

        # only From Date
        start = today.replace(day=5) if today.day >= 5 else today.replace(day=1)
        set_dates(page, start.isoformat(), today.isoformat())
        props = refresh(page, lambda: to_date(page).fill(""))
        assert to_date(page).input_value() == ""
        for row in table_rows(page):
            assert displayed_date(row["timestamp"]) >= start, f"{row['timestamp']} is before {start}"
        assert props["filters"]["to_date"] is None, f"an empty To box still filtered to {props['filters']['to_date']}"

        browser.close()
