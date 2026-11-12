"""ML-032: HR access matches the sidebar.

Steps:
1. Sign in as HR through Development Quick Login.
2. Check whether Logs > Mail Log is in the sidebar.
3. Go straight to /mail-logs and to a mail's page.

Expected: menu and access agree: with the menu item both pages open (200); without it both answer 403.

Known bug: HR has no Mail Log menu item but can open /mail-logs and every mail page (200). This test fails until
the menu and the access agree, whichever way that is fixed.
"""
import json
import time
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    if "filters" in props:
        props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


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
    if parent.count() and not page.get_by_test_id("sidebar-child-mail-log").count():
        parent.dispatch_event("click")
        time.sleep(1)
    return page.get_by_test_id("sidebar-child-mail-log")


def test_ml_032_hr_access():
    with sync_playwright() as p:
        admin_browser = p.chromium.launch(headless=False)
        admin = admin_browser.new_page()
        login(admin)
        mail_id = props_at(admin, LOGS_URL)["mailLogs"]["data"][0]["id"]
        admin_browser.close()

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        dev_login(page, "hr")
        has_menu = logs_menu_item(page).count() > 0
        expected = 200 if has_menu else 403
        problems = []
        for url in [LOGS_URL, f"{LOGS_URL}/{mail_id}"]:
            status = page.goto(url).status
            if status != expected:
                problems.append(f"HR {'has' if has_menu else 'has no'} menu item but {url} answered {status}")
        assert not problems, problems

        browser.close()
