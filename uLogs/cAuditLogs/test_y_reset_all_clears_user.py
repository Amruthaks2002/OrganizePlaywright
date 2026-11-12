"""AL-025: Reset All clears every filter, including the User filter.

Steps:
1. Open Audit Logs and note the dates the boxes start with.
2. Select Model = LeaveApplication, Event Type = Updated, User = Admin User and the year up to yesterday.
3. Click Reset All.

Expected: Model and Event Type are back to "all", the User filter is empty, the dates are back to the starting
ones, and the rows/Total Records match loading the page with just those dates.
"""
import json
import time
from datetime import date, timedelta
from urllib.parse import parse_qs, urlencode, urlparse

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


def test_al_025_reset_all_clears_user():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)
        start_dates = (from_date(page).input_value(), to_date(page).input_value())

        refresh(page, lambda: model_select(page).select_option(label="LeaveApplication"))
        refresh(page, lambda: event_select(page).select_option(label="Updated"))
        pick_user(page, "Admin User")
        set_dates(page, *wide_range())

        props = refresh(page, lambda: page.get_by_role("button", name="Reset All").click())
        assert props["filters"]["model"] == "all" and props["filters"]["event"] == "all", props["filters"]
        assert props["filters"]["user"] in (None, "", "all"), props["filters"]
        expect(model_select(page)).to_have_value("all")
        expect(event_select(page)).to_have_value("all")
        assert page.locator(".vs__selected").count() == 0, "the User filter still shows a user"
        assert (from_date(page).input_value(), to_date(page).input_value()) == start_dates

        expected = props_at(page, list_url(date_from=start_dates[0], date_to=start_dates[1]))["audits"]["total"]
        assert props["audits"]["total"] == expected, f"Reset All shows {props['audits']['total']}, expected {expected}"

        browser.close()
