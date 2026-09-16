from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import re
import time


def test_audit_logs_changes_column_states():
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

        rows = page.locator("table tbody tr")
        row_count = rows.count()

        found_updated = False
        found_no_changes = False
        for i in range(row_count):
            changes_cell = rows.nth(i).locator("td").nth(5)
            text = changes_cell.text_content().strip()
            if re.search(r"\d+ fields? updated", text):
                found_updated = True
            elif text == "No changes recorded":
                found_no_changes = True
            if found_updated and found_no_changes:
                break

        assert found_updated, "expected at least one row with 'N field(s) updated'"
        assert found_no_changes, "expected at least one row with 'No changes recorded'"

        browser.close()
