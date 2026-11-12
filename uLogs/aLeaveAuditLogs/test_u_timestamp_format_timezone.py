"""LAL-020: Timestamp format and timezone.

Steps:
1. Log in as admin and open Leave Audit Logs over the year up to yesterday.
2. Compare each row's timestamp with the stored time of the log.

Expected: every timestamp looks like "10 Nov, 2026, 03:02 PM" and is the stored UTC time converted to India
time (UTC+5:30).
"""
import json
import re
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


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


def wide_range():
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a log time, e.g. 10 Nov, 2026, 03:02 PM (India time)."""
    return to_ist(created_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    """The date part of a displayed timestamp."""
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


FORMAT = re.compile(r"^\d{1,2} [A-Z][a-z]{2}, \d{4}, (0[1-9]|1[0-2]):[0-5]\d (AM|PM)$")


def test_lal_020_timestamp_format_timezone():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        logs = props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}")["logs"]["data"]
        rows = table_rows(page)
        assert rows and len(rows) == len(logs)
        for log, row in zip(logs, rows):
            assert FORMAT.match(row["timestamp"]), f"bad format: {row['timestamp']!r}"
            assert row["timestamp"] == display_timestamp(log["created_at"]), \
                f"log {log['id']} at {log['created_at']} shows {row['timestamp']}, expected {display_timestamp(log['created_at'])}"

        browser.close()
