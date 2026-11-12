"""API-014: Each row shows the right values.

Steps:
1. Log in as admin and open API Logs over all time.
2. Compare every row on the first page with the entry behind it.

Expected: Time = the entry time in India time ("12 Nov 2026, 10:07:37 AM"), Service = the service's label,
User / Triggered By = the names, Outcome = the outcome, HTTP = the status code, Duration = "<n> ms", Reference =
the reference; empty values show "—".
"""
import json
import re
import time
from datetime import date, datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def all_time():
    return {"start_date": "2000-01-01", "end_date": date.today().isoformat()}


COLUMNS = ["time", "service", "user", "outcome", "http", "duration", "triggered_by", "reference"]


def table_rows(page):
    """Visible API log rows as dicts (the empty state has a single cell and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != len(COLUMNS):
            continue
        rows.append({key: cells.nth(i).inner_text().strip() for i, key in enumerate(COLUMNS)})
    return rows


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a time, e.g. 12 Nov 2026, 10:07:37 AM (India time)."""
    return to_ist(created_at).strftime("%-d %b %Y, %I:%M:%S %p")


def displayed_date(timestamp):
    return datetime.strptime(timestamp.split(",")[0].strip(), "%d %b %Y").date()


FORMAT = re.compile(r"^\d{1,2} [A-Z][a-z]{2} \d{4}, (0[1-9]|1[0-2]):[0-5]\d:[0-5]\d (AM|PM)$")


def dash(value, suffix=""):
    return "—" if value in (None, "") else f"{value}{suffix}"


def test_api_014_row_content_matches_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        props = props_at(page, list_url(**all_time()))
        labels = {s["value"]: s["label"] for s in props["services"]}
        logs = props["apiLogs"]["data"]
        rows = table_rows(page)
        assert rows and len(rows) == len(logs)
        problems = []
        for log, row in zip(logs, rows):
            expected = {"time": display_timestamp(log["created_at"]), "service": labels.get(log["service_name"]),
                        "user": dash(log["user_name"]), "outcome": log["outcome"], "http": dash(log["http_status"]),
                        "duration": dash(log["duration_ms"], " ms"), "triggered_by": dash(log["actor_name"]),
                        "reference": dash(log["reference"])}
            got = dict(row, outcome=row["outcome"].lower())
            for key, value in expected.items():
                if got[key] != value:
                    problems.append(f"{log['id']} {key}: shows {got[key]!r}, expected {value!r}")
            if not FORMAT.match(row["time"]):
                problems.append(f"{log['id']} time format {row['time']!r}")
        assert not problems, problems

        browser.close()
