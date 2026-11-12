"""WM-018: Each row shows the right employee, actor, action and description.

Steps:
1. Log in as admin and open Work Mode Audit Logs over the year up to yesterday.
2. Compare every row on the first page with the log record behind it.

Expected:
- Employee = the request's employee, Action By = who did it, Action = the action label,
  Description = the log description.
- The log's employee is the work mode request's owner.
- "Created" rows name the work mode and number of days that were requested.
"""
import json
import time
from datetime import date, timedelta

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/work-mode-logs"
SUBTITLE = "A complete history of all work mode-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


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


def wide_range():
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def test_wm_018_row_content_matches_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        logs = props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}")["logs"]["data"]
        rows = table_rows(page)
        assert rows and len(rows) == len(logs)

        problems = []
        for log, row in zip(logs, rows):
            expected = {"employee": log["user"]["name"], "action_by": log["actor"]["name"] if log["actor"] else "",
                        "action": log["action_label"], "description": log["description"]}
            for key, value in expected.items():
                if row[key] != value.strip():
                    problems.append(f"log {log['id']} {key}: shows {row[key]!r}, expected {value!r}")
            request = log.get("work_mode_application")
            if request and request["user_id"] != log["user_id"]:
                problems.append(f"log {log['id']} is for user {log['user_id']} but request {request['id']} is user {request['user_id']}")
            details = log.get("details") or {}
            if log["action"] == "created" and "leave_type" in details and "days" in details:
                days = f"{float(details['days']):g}"
                if f"{details['leave_type']} work mode request" not in log["description"] or f"{days} day" not in log["description"]:
                    problems.append(f"log {log['id']} description {log['description']!r} doesn't match {details}")
        assert not problems, problems

        browser.close()
