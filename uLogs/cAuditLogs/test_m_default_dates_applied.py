"""AL-013: The default date boxes are applied when the page opens.

Steps:
1. Log in as admin and open Logs > Audit Logs.
2. Note the dates in Date From / Date To and the Total Records.
3. Load the page with those dates in the URL.

Expected: the first load already filters by the dates shown, so Total Records and the rows match the URL load,
and every row on page 1 is inside those dates.

Known bug: the first load ignores the date boxes and lists every record (10,317 on 2026-11-11 against 4,110 for the
dates shown). This test fails until that's fixed.
"""
import json
import time
from datetime import date, datetime, timezone
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

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


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url, wait_for=SUBTITLE):
    page.goto(url)
    page.get_by_text(wait_for).first.wait_for(state="visible")
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


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
    """Audit times come as '2026-11-11T06:33:43.793000Z' (list) or '2026-11-11 06:33:43' (detail), both UTC."""
    moment = datetime.fromisoformat(created_at.replace("Z", "").replace(" ", "T"))
    return moment.replace(tzinfo=timezone.utc).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a time, e.g. 11 Nov, 2026, 03:50 PM (India time)."""
    return to_ist(created_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


def test_al_013_default_dates_applied():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)

        start, end = from_date(page).input_value(), to_date(page).input_value()
        assert start and end, "the date boxes start empty"
        first_total = total_records(page)
        first_rows = table_rows(page)

        expected = props_at(page, list_url(date_from=start, date_to=end))["audits"]["total"]
        problems = []
        if first_total != expected:
            problems.append(f"first load shows {first_total} records, the dates shown hold {expected}")
        outside = [r["timestamp"] for r in first_rows
                   if not date.fromisoformat(start) <= displayed_date(r["timestamp"]) <= date.fromisoformat(end)]
        if outside:
            problems.append(f"rows outside {start}..{end}: {outside[:3]}")
        assert not problems, problems

        browser.close()
