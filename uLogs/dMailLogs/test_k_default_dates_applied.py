"""ML-011: The default date boxes are applied when the page opens.

Steps:
1. Log in as admin in a new browser and open Logs > Mail Log.
2. Note the dates in From Date / To Date and the rows shown.
3. Load the page with those dates in the URL.

Expected: the first load already filters by the dates shown, so its total matches the URL load and every row on
page 1 is inside those dates.

Known bug: the first load ignores the date boxes and lists every mail ever sent (7,191 on 2026-11-11 against 311
for the dates shown). This test fails until that's fixed.
"""
import json
import time
from datetime import date, datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def wait_for_list(page):
    page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
    time.sleep(1)


def open_mail_logs(page):
    """Logs in as admin and opens Logs > Mail Log from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-mail-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    wait_for_list(page)


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    if "filters" in props:
        props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def table_rows(page):
    """Visible mail rows as dicts (the empty state has a single cell and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != 5:
            continue
        rows.append({
            "recipient": cells.nth(0).inner_text().strip(),
            "subject": cells.nth(1).inner_text().strip(),
            "event": cells.nth(2).inner_text().strip(),
            "status": cells.nth(3).inner_text().strip(),
            "sent_at": cells.nth(4).inner_text().strip(),
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


def to_ist(sent_at):
    return datetime.fromisoformat(sent_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(sent_at):
    """How the page shows a time, e.g. 11 Nov, 2026, 04:23 PM (India time)."""
    return to_ist(sent_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


def test_ml_011_default_dates_applied():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_mail_logs(page)

        start, end = from_date(page).input_value(), to_date(page).input_value()
        assert start and end, "the date boxes start empty"
        first = props_at(page, LOGS_URL)
        rows = table_rows(page)
        expected = props_at(page, list_url(start_date=start, end_date=end))["mailLogs"]["total"]

        problems = []
        if first["mailLogs"]["total"] != expected:
            problems.append(f"first load lists {first['mailLogs']['total']} mails, the dates shown hold {expected}")
        outside = [r["sent_at"] for r in rows
                   if not date.fromisoformat(start) <= displayed_date(r["sent_at"]) <= date.fromisoformat(end)]
        if outside:
            problems.append(f"rows outside {start}..{end}: {outside[:3]}")
        assert not problems, problems

        browser.close()
