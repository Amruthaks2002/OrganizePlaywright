"""LAL-027: Light and dark mode.

Steps:
1. Open Leave Audit Logs (light mode) and note the colours of the table header, a row and the filter inputs.
2. Switch the theme with the theme toggle.
3. Switch it back.

Expected: dark mode puts the "dark" class on the page, and the header text, row text and inputs change colour
(nothing keeps its light-mode colours); switching back removes the class and restores the light colours.
"""
import time

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


def colours(page):
    def css(locator, prop):
        return locator.evaluate(f"e => getComputedStyle(e).{prop}")
    return {
        "header": css(page.locator("table thead th").first, "color"),
        "row": css(page.locator("table tbody tr td").first, "color"),
        "input": css(page.locator("input[type='date']").first, "backgroundColor"),
    }


def is_dark(page):
    return "dark" in (page.locator("html").get_attribute("class") or "").split()


def test_lal_027_dark_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_leave_audit_logs(page)
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
