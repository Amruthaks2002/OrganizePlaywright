"""ML-017: Only one of From Date / To Date set.

Steps:
1. Log in as admin and note the totals from 2000-01-01 to 10 days ago, and from 10 days ago to today.
2. Open Mail Logs, set both dates, then clear From Date (To Date = 10 days ago).
3. Set From Date = 10 days ago and clear To Date.

Expected: with only To Date set every mail up to that day is listed; with only From Date set every mail from that
day on is listed; the cleared box stays empty.
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


IST = ZoneInfo("Asia/Kolkata")


def to_ist(sent_at):
    return datetime.fromisoformat(sent_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(sent_at):
    """How the page shows a time, e.g. 11 Nov, 2026, 04:23 PM (India time)."""
    return to_ist(sent_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


def test_ml_017_single_date_bound():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        today = date.today()
        cut = today - timedelta(days=10)
        up_to = props_at(page, list_url(start_date="2000-01-01", end_date=cut.isoformat()))["mailLogs"]["total"]
        from_on = props_at(page, list_url(start_date=cut.isoformat(), end_date=today.isoformat()))["mailLogs"]["total"]

        set_dates(page, (cut - timedelta(days=1)).isoformat(), cut.isoformat())
        props = refresh(page, lambda: from_date(page).fill(""))
        assert from_date(page).input_value() == ""
        assert props["mailLogs"]["total"] == up_to, f"To-only shows {props['mailLogs']['total']}, expected {up_to}"

        set_dates(page, cut.isoformat(), today.isoformat())
        props = refresh(page, lambda: to_date(page).fill(""))
        assert to_date(page).input_value() == ""
        assert props["mailLogs"]["total"] >= from_on, f"From-only shows {props['mailLogs']['total']}, expected {from_on}"
        for row in table_rows(page):
            assert displayed_date(row["sent_at"]) >= cut, f"{row['sent_at']} is before {cut}"

        browser.close()
