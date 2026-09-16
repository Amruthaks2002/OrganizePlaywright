from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import re
import time


def get_total_records(page):
    text = page.get_by_text("Total Records:").locator("xpath=..").text_content()
    return int(re.search(r"(\d+)", text).group(1))


def test_audit_logs_model_filter():
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

        records_before = get_total_records(page)

        page.locator("select").first.select_option(label="User")
        time.sleep(1)

        records_after = get_total_records(page)
        assert records_after <= records_before

        # every row's MODEL column should now say "User"
        rows = page.locator("table tbody tr")
        row_count = rows.count()
        assert row_count > 0
        for i in range(row_count):
            model_cell = rows.nth(i).locator("td").nth(1)
            expect(model_cell).to_have_text("User")

        browser.close()
