from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time


def test_audit_logs_event_type_filter():
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

        page.locator("select").nth(1).select_option(label="Created")
        time.sleep(1)

        rows = page.locator("table tbody tr")
        row_count = rows.count()
        assert row_count > 0
        for i in range(row_count):
            event_cell = rows.nth(i).locator("td").nth(2)
            expect(event_cell).to_have_text("created", ignore_case=True)

        browser.close()
