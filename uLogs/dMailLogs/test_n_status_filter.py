"""ML-014: The Status filter, alone and with Type, and its options.

Steps:
1. Open Mail Logs and set the dates to the year up to yesterday.
2. Select Status = Sent, then Failed.
3. With Status = Failed, select Type = Leave Submitted.
4. Compare the Status options with the statuses the mails actually have.

Expected: every row has the chosen status; with both filters every row matches both; every status a mail can have
can be selected, so the per-status totals add up to the unfiltered total.

Known bug: some mails are "queued" (8 in the year up to 2026-11-11), but the Status dropdown only offers Sent and
Failed, so they can't be filtered. This test fails on that last check until it's fixed.
"""
import json
import time
from datetime import date, timedelta
from urllib.parse import urlparse

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


def type_select(page):
    return page.locator("main select").first


def status_select(page):
    return page.locator("main select").last


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


def test_ml_014_status_filter():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_mail_logs(page)
        total = set_dates(page, *wide_range())["mailLogs"]["total"]

        totals = {}
        for label in ["Sent", "Failed"]:
            props = refresh(page, lambda: status_select(page).select_option(label=label))
            totals[label.lower()] = props["mailLogs"]["total"]
            assert {m["status"] for m in props["mailLogs"]["data"]} <= {label.lower()}
            assert all(row["status"] == label.lower() for row in table_rows(page)), table_rows(page)

        props = refresh(page, lambda: type_select(page).select_option(label="Leave Submitted"))
        assert props["mailLogs"]["total"] <= totals["failed"]
        for row in table_rows(page):
            assert row["status"] == "failed" and row["event"] == "Leave Submitted", row

        offered = [v for v in (o.get_attribute("value") for o in status_select(page).locator("option").all()) if v]
        missing = total - sum(totals.values())
        assert missing == 0, f"{missing} mails have a status the dropdown doesn't offer (options: {offered})"

        browser.close()
