"""WM-016: Reset clears every filter.

Steps:
1. Open Work Mode Audit Logs and note the dates the boxes start with.
2. Set Employee, Action Status = Approved, From/To = the year up to yesterday, Description = "request".
3. Click Reset.

Expected: the employee, action and description are empty again, the dates go back to what the boxes started
with, and the rows are the same as loading the page with only those dates.
"""
import json
import time
from collections import Counter
from datetime import date, timedelta
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/work-mode-logs"
SUBTITLE = "A complete history of all work mode-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def refresh(page, action):
    """Runs a filter action and returns the props of the reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: "/work-mode-logs" in r.url and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    props = info.value.json()["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def props_at(page, url):
    page.goto(url)
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    return page_props(page)


def employee_box(page):
    return page.locator(".v-select").nth(0).locator("input.vs__search")


def search_response(text):
    """Matches the dropdown's /users/search call for this text."""
    return lambda r: "/users/search" in r.url and parse_qs(urlparse(r.url).query).get("query", [""])[0] == text


def offered(page, text):
    """Types into the Employee filter and returns the names it offers. The dropdown searches on the server, and the
    empty search fired on opening it can come back after the typed one, so wait for both."""
    box = employee_box(page)
    try:
        with page.expect_response(search_response(""), timeout=5000):
            page.locator(".v-select").nth(0).locator(".vs__dropdown-toggle").click()
    except Exception:
        pass  # the list was already loaded
    with page.expect_response(search_response(text), timeout=15000):
        box.fill(text)
    time.sleep(1)
    if page.get_by_text("No employees found").is_visible():
        return []
    return [o.strip() for o in page.get_by_role("option").all_inner_texts()]


def pick_employee(page, name):
    offered(page, name)
    return refresh(page, lambda: page.get_by_role("option", name=name, exact=True).click())


def pick_first_selectable(page, names):
    """Selects the first of these names that the Employee dropdown offers (it doesn't offer every employee who has
    logs, e.g. relieved ones) and that has rows under the other filters; returns (name, props)."""
    for name in names:
        if name in offered(page, name):
            props = refresh(page, lambda: page.get_by_role("option", name=name, exact=True).click())
            if props["logs"]["total"] > 0:
                return name, props
    raise AssertionError(f"none of {names} can be picked in the Employee filter with rows to show")


def status_box(page):
    return page.locator(".v-select").nth(1).locator("input.vs__search")


def pick_status(page, label):
    page.locator(".v-select").nth(1).locator(".vs__dropdown-toggle").click()
    box = status_box(page)
    box.fill(label)
    time.sleep(1)
    return refresh(page, lambda: page.get_by_role("option", name=label, exact=True).click())


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
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def employees_with_logs(page, start, end):
    """Employees with logs in the range, most rows first. Samples the first page of several actions, because one busy
    QA account (AutoUser_tNuUc, used by the payroll tests) can fill whole pages of the unfiltered list. Leaves the
    page showing the range with no other filter."""
    counts = Counter()
    for status in ["", "created", "approved", "rejected", "cancelled", "updated"]:
        extra = f"&status={status}" if status else ""
        props = props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}{extra}")
        counts.update(log["user"]["name"] for log in props["logs"]["data"])
    props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}")
    return [name for name, _ in counts.most_common()]


def test_wm_016_reset_clears_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.goto(LOGS_URL)
        page.get_by_text(SUBTITLE).wait_for(state="visible")
        time.sleep(1)
        start_dates = (from_date(page).input_value(), to_date(page).input_value())

        pick_first_selectable(page, employees_with_logs(page, *wide_range()))
        pick_status(page, "Approved")
        refresh(page, lambda: page.locator("input[placeholder='Search text...']").fill("request"))

        props = refresh(page, lambda: page.get_by_role("button", name="Reset").click())
        for key in ["employee_id", "status", "search"]:
            assert not props["filters"].get(key), f"{key} still applied: {props['filters']}"
        assert (props["filters"].get("from_date"), props["filters"].get("to_date")) == start_dates, props["filters"]
        assert page.locator(".vs__selected").count() == 0, "a dropdown still shows a selection"
        assert page.locator("input[placeholder='Search text...']").input_value() == ""
        assert (from_date(page).input_value(), to_date(page).input_value()) == start_dates
        total = props["logs"]["total"]

        expected = props_at(page, f"{LOGS_URL}?from_date={start_dates[0]}&to_date={start_dates[1]}")["logs"]["total"]
        assert total == expected, f"Reset shows {total} logs, the default dates hold {expected}"

        browser.close()
