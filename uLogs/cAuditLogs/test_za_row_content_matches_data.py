"""AL-027: Each row shows the right ID, model, event, user and time.

Steps:
1. Log in as admin and open Audit Logs over the year up to yesterday.
2. Compare every row on the first page with the record behind it.

Expected: ID = "#" + record id, Model = the model's short name, Event = the event, User = who made the change,
Timestamp = the record time in India time ("11 Nov, 2026, 03:50 PM").
"""
import json
import re
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


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


def wide_range():
    """The year up to yesterday: ending yesterday so entries being written right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


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


FORMAT = re.compile(r"^\d{1,2} [A-Z][a-z]{2}, \d{4}, (0[1-9]|1[0-2]):[0-5]\d (AM|PM)$")


def test_al_027_row_content_matches_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        audits = props_at(page, list_url(date_from=start, date_to=end))["audits"]["data"]
        rows = table_rows(page)
        assert rows and len(rows) == len(audits)
        problems = []
        for audit, row in zip(audits, rows):
            expected = {"id": f"#{audit['id']}", "model": short(audit["model"]), "event": audit["event"].lower(),
                        "user": audit["user"] or "System", "timestamp": display_timestamp(audit["created_at"])}
            got = dict(row, event=row["event"].lower())
            for key, value in expected.items():
                if got[key] != value:
                    problems.append(f"{audit['id']} {key}: shows {got[key]!r}, expected {value!r}")
            if not FORMAT.match(row["timestamp"]):
                problems.append(f"{audit['id']} timestamp format {row['timestamp']!r}")
        assert not problems, problems

        browser.close()
