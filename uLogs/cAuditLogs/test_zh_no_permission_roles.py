"""AL-035: Roles without access can't see or open Audit Logs.

Steps (each in its own browser, signed in through Development Quick Login):
1. Sign in as employee, team lead and project manager.
2. Look for Logs > Audit Log in the sidebar.
3. Go straight to /audits and to an Audit History address (/audits/entity?auditable_type=User&auditable_id=7).

Expected: no menu item, both addresses answer 403 and no audit data is shown.
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


ROLES = ["employee", "team-lead", "project-manager"]
DETAIL_URL = f"{LOGS_URL}/entity?auditable_type=User&auditable_id=7"


def test_al_035_no_permission_roles():
    with sync_playwright() as p:
        problems = []
        for role in ROLES:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            try:
                dev_login(page, role)
                if logs_menu_item(page).count():
                    problems.append(f"{role} sees Audit Log in the sidebar")
                for url in [LOGS_URL, DETAIL_URL]:
                    response = page.goto(url)
                    if response.status != 403:
                        problems.append(f"{role} got {response.status} on {url}")
                    if page.get_by_text(SUBTITLE).count() or page.get_by_text("Audit History").count():
                        problems.append(f"{role} can see audit data on {url}")
            finally:
                browser.close()
        assert not problems, problems
