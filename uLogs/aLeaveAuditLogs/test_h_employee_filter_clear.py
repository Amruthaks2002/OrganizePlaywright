"""LAL-007: The clear (x) button on the Employee filter.

Steps:
1. Open Leave Audit Logs and note the total number of logs.
2. Select "Admin User" in the Employee filter.
3. Click the clear (x) button in the Employee filter.

Expected: the x appears once an employee is selected; clearing removes the selection, hides the x, drops the
employee filter and brings back the original total.
"""
import json
import time
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def open_leave_audit_logs(page):
    """Logs in as admin and opens Logs > Leave Audit Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-leave-audit-logs")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def refresh(page, action):
    """Runs a filter action and returns the props of the reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: "/leave-logs" in r.url and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    return info.value.json()["props"]


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


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


def test_lal_007_employee_filter_clear():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_leave_audit_logs(page)
        total = props_at(page, LOGS_URL)["logs"]["total"]

        clear = page.locator(".vs__clear").first
        expect(clear).to_be_hidden()
        pick_employee(page, "Admin User")
        expect(clear).to_be_visible()

        props = refresh(page, lambda: clear.click())
        assert props["filters"]["employee_id"] is None
        assert props["logs"]["total"] == total
        expect(clear).to_be_hidden()
        assert page.locator(".vs__selected").count() == 0
        expect(employee_box(page)).to_have_attribute("placeholder", "Search by employee...")

        browser.close()
