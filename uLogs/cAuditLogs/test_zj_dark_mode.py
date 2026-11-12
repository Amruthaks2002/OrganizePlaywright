"""AL-037: Light and dark mode.

Steps:
1. Open Audit Logs (light mode) and note the colours of the table header, a row, the filter inputs and the
   Total Records number.
2. Switch the theme with the theme toggle, then switch it back.

Expected: dark mode puts the "dark" class on the page and all of those colours change; switching back restores
them.
"""
import time

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


def colours(page):
    def css(locator, prop):
        return locator.evaluate(f"e => getComputedStyle(e).{prop}")
    return {
        "header": css(page.locator("table thead th").first, "color"),
        "row": css(page.locator("table tbody tr td span").first, "color"),
        "input": css(page.locator("input[type='date']").first, "backgroundColor"),
        "total": css(page.get_by_text("Total Records:").locator("xpath=following-sibling::span[1]"), "color"),
    }


def is_dark(page):
    return "dark" in (page.locator("html").get_attribute("class") or "").split()


def test_al_037_dark_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)
        toggle = page.get_by_test_id("theme-toggle-button")
        try:
            if is_dark(page):
                toggle.click()
                time.sleep(1)
            light = colours(page)
            toggle.click()
            time.sleep(1)
            assert is_dark(page)
            dark = colours(page)
            same = [key for key in light if light[key] == dark[key]]
            assert not same, f"unchanged in dark mode: {same} ({dark})"
            toggle.click()
            time.sleep(1)
            assert not is_dark(page)
            assert colours(page) == light
        finally:
            browser.close()
