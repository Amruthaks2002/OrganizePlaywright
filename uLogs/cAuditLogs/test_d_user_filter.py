from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time


def test_audit_logs_user_filter():
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

        # grab a real user from the current (unfiltered) table so the search below
        # is checked against data that actually exists. "System" is a synthetic
        # actor for automated actions, not a selectable user, so skip it.
        rows = page.locator("table tbody tr")
        sample_user = None
        for i in range(rows.count()):
            candidate = rows.nth(i).locator("td").nth(3).text_content().strip()
            if candidate != "System":
                sample_user = candidate
                break
        assert sample_user is not None

        user_combobox = page.locator("input[placeholder='Search by user...']")
        user_combobox.click()
        time.sleep(1)
        user_combobox.fill(sample_user)
        time.sleep(1)

        option = page.get_by_role("option", name=sample_user)
        expect(option).to_be_visible()
        option.click()
        time.sleep(1)

        rows = page.locator("table tbody tr")
        row_count = rows.count()
        assert row_count > 0
        for i in range(row_count):
            user_cell = rows.nth(i).locator("td").nth(3)
            expect(user_cell).to_have_text(sample_user)

        browser.close()
