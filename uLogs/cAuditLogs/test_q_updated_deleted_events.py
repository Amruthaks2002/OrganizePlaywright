"""AL-017: The Updated and Deleted event filters, and the event badge colours.

Steps:
1. Open Audit Logs and set the dates to the year up to yesterday.
2. Select Event Type = Updated, then Deleted, then Created.

Expected: every row has the chosen event, and the badge is coloured by event: Created green, Updated blue,
Deleted red.
"""
import json
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


def table_rows(page):
    """Visible audit rows as dicts (the empty state has fewer cells and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != 7:
            continue
        rows.append({
            "id": cells.nth(0).inner_text().strip(),
            "model": cells.nth(1).inner_text().strip(),
            "event": cells.nth(2).inner_text().strip(),
            "user": cells.nth(3).inner_text().strip(),
            "timestamp": cells.nth(4).inner_text().strip(),
            "changes": cells.nth(5).inner_text().strip(),
        })
    return rows


def short(model):
    return model.split("\\")[-1]


def total_records(page):
    return int(page.get_by_text("Total Records:").locator("xpath=following-sibling::span[1]").inner_text().strip())


def model_select(page):
    return page.locator("main select").first


def event_select(page):
    return page.locator("main select").nth(1)


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
    """The year up to yesterday: ending yesterday so entries being written right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


COLOURS = {"Created": "green", "Updated": "blue", "Deleted": "red"}


def test_al_017_updated_deleted_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)
        set_dates(page, *wide_range())

        for label, colour in [("Updated", "blue"), ("Deleted", "red"), ("Created", "green")]:
            props = refresh(page, lambda: event_select(page).select_option(label=label))
            assert props["audits"]["total"] > 0, f"no {label} records in the year up to yesterday"
            assert {audit["event"] for audit in props["audits"]["data"]} == {label.lower()}
            rows = table_rows(page)
            assert all(row["event"].lower() == label.lower() for row in rows), [r["event"] for r in rows]
            badges = page.locator("table tbody tr td:nth-child(3) span")
            for i in range(badges.count()):
                css = (badges.nth(i).get_attribute("class") or "").split()
                assert f"bg-{colour}-100" in css, f"{label} badge is {css}"

        browser.close()
