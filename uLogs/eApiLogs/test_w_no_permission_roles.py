"""API-023: Roles without access can't see or open API Logs.

Steps (each in its own browser, signed in through Development Quick Login):
1. Sign in as employee, team lead, project manager and HR.
2. Look for Logs > API Log in the sidebar.
3. Go straight to /api-logs and to an entry's page.

Expected: no menu item, both addresses answer 403 and no log data is shown. (On 2026-11-12 only admin had access.)
"""
import json
import time
from datetime import date
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def all_time():
    return {"start_date": "2000-01-01", "end_date": date.today().isoformat()}


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
    if parent.count() and not page.get_by_test_id("sidebar-child-api-log").count():
        parent.dispatch_event("click")
        time.sleep(1)
    return page.get_by_test_id("sidebar-child-api-log")


ROLES = ["employee", "team-lead", "project-manager", "hr"]


def test_api_023_no_permission_roles():
    with sync_playwright() as p:
        admin_browser = p.chromium.launch(headless=False)
        admin = admin_browser.new_page()
        login(admin)
        log_id = props_at(admin, list_url(**all_time()))["apiLogs"]["data"][0]["id"]
        admin_browser.close()

        problems = []
        for role in ROLES:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            try:
                dev_login(page, role)
                if logs_menu_item(page).count():
                    problems.append(f"{role} sees API Log in the sidebar")
                for url in [LOGS_URL, f"{LOGS_URL}/{log_id}"]:
                    response = page.goto(url)
                    if response.status != 403:
                        problems.append(f"{role} got {response.status} on {url}")
                    if page.get_by_role("heading", name="API Logs").count() or page.get_by_text("TRIGGERED BY").count():
                        problems.append(f"{role} can see API log data on {url}")
            finally:
                browser.close()
        assert not problems, problems
