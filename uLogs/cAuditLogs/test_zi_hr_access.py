"""AL-036: HR access matches the sidebar.

Steps:
1. Sign in as HR through Development Quick Login.
2. Check whether Logs > Audit Log is in the sidebar.
3. Go straight to /audits.

Expected: menu and access agree. With the menu item the page opens (200) with its table; without it the address
answers 403. (On 2026-11-11 HR had both; the test also passes if that changes.)
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def dev_login(page, role):
    """Signs in through the Development Quick Login link for a role."""
    page.goto(BASE_URL)
    page.get_by_test_id(f"dev-login-link-{role}").click()
    page.wait_for_url("**/dashboard**")
    time.sleep(1)


def logs_menu_item(page):
    """Expands the System section (a dashboard popup may cover it, hence dispatch_event) and returns the menu item."""
    section = page.get_by_test_id("sidebar-section-system")
    if section.count() and section.get_attribute("aria-expanded") != "true":
        section.dispatch_event("click")
        time.sleep(1)
    parent = page.get_by_test_id("sidebar-parent-logs")
    if parent.count() and not page.get_by_test_id("sidebar-child-audit-log").count():
        parent.dispatch_event("click")
        time.sleep(1)
    return page.get_by_test_id("sidebar-child-audit-log")


def test_al_036_hr_access():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        dev_login(page, "hr")
        has_menu = logs_menu_item(page).count() > 0

        response = page.goto(LOGS_URL)
        if has_menu:
            assert response.status == 200, f"HR has the menu item but /audits answered {response.status}"
            expect(page.get_by_text(SUBTITLE)).to_be_visible()
            expect(page.locator("table")).to_be_visible()
        else:
            assert response.status == 403, f"HR has no menu item but /audits answered {response.status}"

        browser.close()
