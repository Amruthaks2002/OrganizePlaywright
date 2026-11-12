"""ML-013: Every Type option filters correctly.

Steps:
1. Open Mail Logs and set the dates to the year up to yesterday.
2. Select each Type option in turn.

Expected: the options are the server's event types (All Types first), and for each one every row (in the table and
in the data behind it) has that event; when there are none the page says "No mail has been sent yet."
"""
import json
import time
from datetime import date, timedelta
from urllib.parse import urlencode, urlparse

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


def test_ml_013_each_type_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_mail_logs(page)
        types = props_at(page, LOGS_URL)["eventTypes"]

        labels = [o.strip() for o in type_select(page).locator("option").all_inner_texts()]
        assert labels == ["All Types"] + [t["label"] for t in types], labels
        set_dates(page, *wide_range())

        problems = []
        for event in types:
            props = refresh(page, lambda: type_select(page).select_option(value=event["value"]))
            got = {mail["event_type"] for mail in props["mailLogs"]["data"]}
            if got - {event["value"]}:
                problems.append(f"{event['label']}: data has {got}")
            rows = table_rows(page)
            if props["mailLogs"]["total"] == 0:
                if not page.get_by_text(EMPTY_MESSAGE).is_visible():
                    problems.append(f"{event['label']}: no rows but no empty message")
            elif any(row["event"] != event["label"] for row in rows):
                problems.append(f"{event['label']}: table shows {sorted({r['event'] for r in rows})}")
        assert not problems, problems

        browser.close()
