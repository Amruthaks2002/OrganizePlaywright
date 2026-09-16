from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time


def test_audit_logs_no_results_state():
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

        # a future date range guaranteed to have no audit records
        page.locator("input[type='date']").first.fill("2027-01-01")
        page.locator("input[type='date']").last.fill("2027-01-02")
        time.sleep(1)

        expect(page.get_by_text("No audit logs found")).to_be_visible()
        expect(page.get_by_text("Try adjusting your filters to see more results")).to_be_visible()

        browser.close()
