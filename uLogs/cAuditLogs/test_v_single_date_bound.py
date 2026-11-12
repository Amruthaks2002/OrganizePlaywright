"""AL-022: Only one of Date From / Date To set.

Steps:
1. Log in as admin and note the totals from 2000-01-01 to 10 days ago, and from 10 days ago to today.
2. Open Audit Logs, set both dates, then clear Date From (Date To = 10 days ago).
3. Set Date From = 10 days ago and clear Date To.

Expected: with only Date To set every record up to that day is listed; with only Date From set every record from
that day on is listed; the cleared box stays empty.
"""
import json
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode, urlparse
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def refresh(page, action):
    """Runs a filter action and returns the props of the list reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: urlparse(r.url).path == "/audits" and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    return info.value.json()["props"]


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


def test_al_022_single_date_bound():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        today = date.today()
        cut = today - timedelta(days=10)
        up_to = props_at(page, list_url(date_from="2000-01-01", date_to=cut.isoformat()))["audits"]["total"]
        from_on = props_at(page, list_url(date_from=cut.isoformat(), date_to=today.isoformat()))["audits"]["total"]

        set_dates(page, (cut - timedelta(days=1)).isoformat(), cut.isoformat())
        props = refresh(page, lambda: from_date(page).fill(""))
        assert from_date(page).input_value() == ""
        assert props["audits"]["total"] == up_to, f"To-only shows {props['audits']['total']}, expected {up_to}"

        set_dates(page, cut.isoformat(), today.isoformat())
        props = refresh(page, lambda: to_date(page).fill(""))
        assert to_date(page).input_value() == ""
        assert props["audits"]["total"] == from_on, f"From-only shows {props['audits']['total']}, expected {from_on}"
        for row in table_rows(page):
            assert displayed_date(row["timestamp"]) >= cut, f"{row['timestamp']} is before {cut}"

        browser.close()
