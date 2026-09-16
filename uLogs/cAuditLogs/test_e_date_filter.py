from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
from datetime import datetime
import time


def test_audit_logs_date_filter():
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

        # grab a real timestamp from the current (unfiltered) table so the date
        # filter below is checked against data that actually exists
        sample_timestamp = page.locator("table tbody tr").first.locator("td").nth(4).text_content().strip()
        sample_date_display = ",".join(sample_timestamp.split(",")[:2]).strip()
        sample_date_value = datetime.strptime(sample_date_display, "%d %b, %Y").strftime("%Y-%m-%d")

        page.locator("input[type='date']").first.fill(sample_date_value)
        page.locator("input[type='date']").last.fill(sample_date_value)
        time.sleep(1)

        rows = page.locator("table tbody tr")
        row_count = rows.count()
        assert row_count > 0
        for i in range(row_count):
            timestamp_cell = rows.nth(i).locator("td").nth(4)
            expect(timestamp_cell).to_contain_text(sample_date_display)

        browser.close()
