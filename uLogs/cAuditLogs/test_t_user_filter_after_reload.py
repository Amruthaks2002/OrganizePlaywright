"""AL-020: The User filter still shows the chosen user after a reload.

Steps:
1. Open Audit Logs and select "Admin User" in the User filter.
2. Reload the page.

Expected: the rows are still Admin User's and the User filter shows "Admin User".

Known bug: after a reload (or any load with user=... in the URL) the rows are filtered but the User dropdown is
empty. This test fails until that's fixed.
"""
import json
import time
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


def test_al_020_user_filter_after_reload():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)

        pick_user(page, "Admin User")
        page.reload()
        page.get_by_text(SUBTITLE).wait_for(state="visible")
        time.sleep(1)

        props = page_props(page)
        assert props["filters"]["user"] == "7", props["filters"]
        assert all(row["user"] == "Admin User" for row in table_rows(page))
        selected = [s.strip() for s in page.locator(".vs__selected").all_inner_texts()]
        assert "Admin User" in selected, f"the User filter is empty after reload although the rows are Admin User's"

        browser.close()
