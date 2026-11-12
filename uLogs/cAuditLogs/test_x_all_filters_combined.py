"""AL-024: Model, Event Type, User and dates together.

Steps:
1. Open Audit Logs and set the dates to the year up to yesterday.
2. Select User = Admin User and take the latest of their records as the sample.
3. Also select the sample's model and event and set both dates to its day.

Expected: the sample record is still listed and every row matches all four filters.
"""
import json
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def open_audit_logs(page):
    """Logs in as admin and opens Logs > Audit Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-audit-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def refresh(page, action):
    """Runs a filter action and returns the props of the list reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: urlparse(r.url).path == "/audits" and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    return info.value.json()["props"]


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


def model_select(page):
    return page.locator("main select").first


def event_select(page):
    return page.locator("main select").nth(1)


def user_box(page):
    return page.locator("input[placeholder='Search by user...']")


def search_response(text):
    """Matches the User dropdown's /users/search call for this text."""
    return lambda r: "/users/search" in r.url and parse_qs(urlparse(r.url).query).get("query", [""])[0] == text


def offered(page, text):
    """Types into the User filter and returns the names it offers. It searches on the server, and the empty search
    fired on opening it can come back after the typed one, so wait for both."""
    try:
        with page.expect_response(search_response(""), timeout=5000):
            page.locator(".v-select .vs__dropdown-toggle").first.click()
    except Exception:
        pass  # the list was already loaded
    with page.expect_response(search_response(text), timeout=15000):
        user_box(page).fill(text)
    time.sleep(1)
    listbox = page.get_by_role("listbox").last
    if listbox.get_by_text("Sorry, no matching options.").is_visible():
        return []
    return [o.strip() for o in listbox.get_by_role("option").all_inner_texts()]


def pick_user(page, name):
    assert name in offered(page, name), f"{name} is not offered in the User filter"
    return refresh(page, lambda: page.get_by_role("listbox").last.get_by_role("option", name=name, exact=True).click())


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


def test_al_024_all_filters_combined():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)

        set_dates(page, *wide_range())
        props = pick_user(page, "Admin User")
        sample = props["audits"]["data"][0]
        day = to_ist(sample["created_at"]).date()

        refresh(page, lambda: model_select(page).select_option(value=sample["model"]))
        if sample["event"] in ("created", "updated", "deleted"):
            refresh(page, lambda: event_select(page).select_option(value=sample["event"]))
        props = set_dates(page, day.isoformat(), day.isoformat())

        assert sample["id"] in [audit["id"] for audit in props["audits"]["data"]], "the sample was filtered out"
        for row in table_rows(page):
            assert row["user"] == "Admin User", row
            assert row["model"] == short(sample["model"]), row
            assert row["event"].lower() == sample["event"].lower(), row
            assert displayed_date(row["timestamp"]) == day, row

        browser.close()
