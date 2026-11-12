"""AL-026: Filters survive paging and a reload.

Steps:
1. Open Audit Logs, set the dates to the year up to yesterday and Model = LeaveApplication.
2. Go to page 2.
3. Select Event Type = Updated while on page 2.
4. Reload the page.

Expected: page 2 still only has LeaveApplication rows; changing a filter goes back to page 1; after the reload the
same filters apply and the Model / Event Type / date boxes show them.
"""
import json
import time
from datetime import date, timedelta
from urllib.parse import urlencode, urlparse

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


def model_select(page):
    return page.locator("main select").first


def event_select(page):
    return page.locator("main select").nth(1)


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


def pagination(page):
    return page.locator("nav").filter(has=page.locator("a[href*='page=']")).last


def test_al_026_filters_in_url_and_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)

        start, end = wide_range()
        set_dates(page, start, end)
        props = refresh(page, lambda: model_select(page).select_option(label="LeaveApplication"))
        assert props["audits"]["last_page"] >= 2

        props = refresh(page, lambda: pagination(page).get_by_role("link", name="2", exact=True).click())
        assert props["audits"]["current_page"] == 2
        assert props["filters"]["model"] == "App\\Models\\LeaveApplication", props["filters"]
        assert all(row["model"] == "LeaveApplication" for row in table_rows(page))

        props = refresh(page, lambda: event_select(page).select_option(label="Updated"))
        assert props["audits"]["current_page"] == 1, "changing a filter didn't go back to page 1"

        page.reload()
        page.get_by_text(SUBTITLE).wait_for(state="visible")
        time.sleep(1)
        props = page_props(page)
        assert props["filters"]["event"] == "updated" and props["filters"]["date_from"] == start, props["filters"]
        expect(model_select(page)).to_have_value("App\\Models\\LeaveApplication")
        expect(event_select(page)).to_have_value("updated")
        assert (from_date(page).input_value(), to_date(page).input_value()) == (start, end)
        assert all(row["model"] == "LeaveApplication" and row["event"].lower() == "updated" for row in table_rows(page))

        browser.close()
