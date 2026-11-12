"""WM-012: Only one of From Date / To Date set.

Steps:
1. Log in as admin and note how many logs exist from 2000-01-01 up to 10 days ago, and from 10 days ago up to today.
2. Open Work Mode Audit Logs, set both dates, then clear From Date (To = 10 days ago).
3. Set From Date = 10 days ago and clear To Date.

Expected:
- With only To Date set, every log up to that day is listed, and the From box stays empty.
- With only From Date set, every log from that day on is listed, every row is on or after it, and the To box
  stays empty.
"""
import json
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

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


def test_wm_012_single_date_bound():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        today = date.today()
        cut = today - timedelta(days=10)
        up_to = props_at(page, f"{LOGS_URL}?from_date=2000-01-01&to_date={cut.isoformat()}")["logs"]["total"]
        from_on = props_at(page, f"{LOGS_URL}?from_date={cut.isoformat()}&to_date={today.isoformat()}")["logs"]["total"]

        # only To Date (the page is showing 2000-01-01 .. today from the URL above)
        set_dates(page, (cut - timedelta(days=1)).isoformat(), cut.isoformat())
        props = refresh(page, lambda: from_date(page).fill(""))
        assert from_date(page).input_value() == ""
        assert props["logs"]["total"] == up_to, f"To-only shows {props['logs']['total']} logs, expected {up_to}"

        # only From Date
        set_dates(page, cut.isoformat(), today.isoformat())
        props = refresh(page, lambda: to_date(page).fill(""))
        assert to_date(page).input_value() == ""
        assert props["logs"]["total"] == from_on, f"From-only shows {props['logs']['total']} logs, expected {from_on}"
        for row in table_rows(page):
            assert displayed_date(row["timestamp"]) >= cut, f"{row['timestamp']} is before {cut}"

        browser.close()
