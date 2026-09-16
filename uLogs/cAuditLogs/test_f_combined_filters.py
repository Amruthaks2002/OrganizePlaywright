from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time


def test_audit_logs_combined_filters():
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

        # grab a real Model + Event combination from the current table so the
        # combined filter below is checked against data that actually exists
        first_row = page.locator("table tbody tr").first
        sample_model = first_row.locator("td").nth(1).text_content().strip()
        sample_event = first_row.locator("td").nth(2).text_content().strip()

        page.locator("select").first.select_option(label=sample_model)
        page.locator("select").nth(1).select_option(label=sample_event.capitalize())
        time.sleep(1)

        rows = page.locator("table tbody tr")
        row_count = rows.count()
        assert row_count > 0
        for i in range(row_count):
            model_cell = rows.nth(i).locator("td").nth(1)
            event_cell = rows.nth(i).locator("td").nth(2)
            expect(model_cell).to_have_text(sample_model)
            expect(event_cell).to_have_text(sample_event, ignore_case=True)

        browser.close()
