"""ML-016: A multi-day date range, including both boundary days.

Steps:
1. Open Mail Logs, set the dates to the year up to yesterday and take the latest day that has mails.
2. Set From Date = that day minus 3 days, To Date = that day.
3. Separately load each single day of that range.

Expected: every row's date (as shown, India time) is inside the range, and the range total equals the sum of the
single-day totals, so both boundary days are fully included.
"""
import json
import time
from datetime import date, datetime, timedelta
from urllib.parse import urlencode, urlparse
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


def refresh(page, action):
    """Runs a filter action and returns the props of the list reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: urlparse(r.url).path == "/mail-logs" and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    props = info.value.json()["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


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


def wide_range():
    """The year up to yesterday: ending yesterday so mails being sent right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


IST = ZoneInfo("Asia/Kolkata")


def to_ist(sent_at):
    return datetime.fromisoformat(sent_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(sent_at):
    """How the page shows a time, e.g. 11 Nov, 2026, 04:23 PM (India time)."""
    return to_ist(sent_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


def test_ml_016_date_range_boundaries():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_mail_logs(page)

        props = set_dates(page, *wide_range())
        assert props["mailLogs"]["data"], "no mails in the year up to yesterday"
        end = to_ist(props["mailLogs"]["data"][0]["sent_at"]).date()
        start = end - timedelta(days=3)

        props = set_dates(page, start.isoformat(), end.isoformat())
        total = props["mailLogs"]["total"]
        for row in table_rows(page):
            assert start <= displayed_date(row["sent_at"]) <= end, f"{row['sent_at']} is outside {start}..{end}"

        per_day = 0
        for offset in range(4):
            day = (start + timedelta(days=offset)).isoformat()
            per_day += props_at(page, list_url(start_date=day, end_date=day))["mailLogs"]["total"]
        assert total == per_day, f"range total {total} != sum of single days {per_day}"

        browser.close()
