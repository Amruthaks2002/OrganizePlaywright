"""WM-025: Roles without access can't see or open the page.

Steps (each in its own browser, signed in through Development Quick Login):
1. Sign in as employee, team lead and project manager.
2. Look for Logs > Work Mode Logs in the sidebar.
3. Go straight to /work-mode-logs.

Expected: the menu item isn't there, the URL answers 403 ("This action is unauthorized.") and no log data is shown.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/work-mode-logs"
SUBTITLE = "A complete history of all work mode-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


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
    if parent.count() and not page.get_by_test_id("sidebar-child-work-mode-logs").count():
        parent.dispatch_event("click")
        time.sleep(1)
    return page.get_by_test_id("sidebar-child-work-mode-logs")


ROLES = ["employee", "team-lead", "project-manager"]


def test_wm_025_no_permission_roles():
    with sync_playwright() as p:
        problems = []
        for role in ROLES:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            try:
                dev_login(page, role)
                if logs_menu_item(page).count():
                    problems.append(f"{role} sees Work Mode Audit Logs in the sidebar")
                response = page.goto(LOGS_URL)
                if response.status != 403:
                    problems.append(f"{role} got {response.status} on /work-mode-logs")
                if page.get_by_text(SUBTITLE).count() or page.locator("table tbody tr").count():
                    problems.append(f"{role} can see the logs")
            finally:
                browser.close()
        assert not problems, problems
