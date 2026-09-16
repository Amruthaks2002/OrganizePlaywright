from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time


def test_audit_logs_back_navigation_resets_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-logs").click()
        audit_log_link = page.get_by_test_id("sidebar-child-audit-log")
        audit_log_link.wait_for(state="visible")
        audit_log_link.click()
        page.get_by_text("Track all system changes and user activities").wait_for(state="visible")
        time.sleep(1)

        # apply a non-default filter before navigating into a record's detail page
        page.locator("select").first.select_option(label="User")
        time.sleep(1)

        page.locator("table tbody tr").first.get_by_role("button", name="View").click()
        page.get_by_role("heading", name="Audit History").wait_for(state="visible")
        time.sleep(1)

        page.get_by_role("link", name="Back To Audit Logs").click()
        page.get_by_role("heading", name="Audit Logs").wait_for(state="visible")
        page.get_by_text("Track all system changes and user activities").wait_for(state="visible")
        time.sleep(1)

        # the list page is shown again, but the Model filter is not retained
        expect(page.locator("select").first).to_have_value("all")

        browser.close()
