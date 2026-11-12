"""LAL-017: A filter combination with no matches.

Steps:
1. Open Leave Audit Logs.
2. Select Employee = Admin User and search the description for "zzqx-no-such-text".

Expected: no rows, the message "No logs found for the selected criteria." and no pagination.
"""
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


def test_lal_017_no_results_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_leave_audit_logs(page)

        pick_employee(page, "Admin User")
        props = refresh(page, lambda: page.locator("input[placeholder='Search text...']").fill("zzqx-no-such-text"))
        assert props["logs"]["total"] == 0
        assert table_rows(page) == []
        expect(page.get_by_text(EMPTY_MESSAGE)).to_be_visible()
        assert page.locator("a[href*='page=']").count() == 0

        browser.close()
