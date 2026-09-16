from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time


def test_audit_logs_reset_all_filters():
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

        default_date_from = page.locator("input[type='date']").first.input_value()
        default_date_to = page.locator("input[type='date']").last.input_value()

        # change every filter
        page.locator("select").first.select_option(label="User")
        page.locator("select").nth(1).select_option(label="Created")
        page.locator("input[type='date']").first.fill("2026-01-01")
        page.locator("input[type='date']").last.fill("2026-01-02")
        time.sleep(1)

        page.get_by_role("button", name="Reset All").click()
        time.sleep(1)

        expect(page.locator("select").first).to_have_value("all")
        expect(page.locator("select").nth(1)).to_have_value("all")
        assert page.locator("input[type='date']").first.input_value() == default_date_from
        assert page.locator("input[type='date']").last.input_value() == default_date_to

        browser.close()
