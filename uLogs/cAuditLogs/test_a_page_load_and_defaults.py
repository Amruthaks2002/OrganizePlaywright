from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import re
import time


def test_audit_logs_page_load_and_defaults():
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

        # page header
        expect(page.get_by_role("heading", name="Audit Logs")).to_be_visible()

        # total records counter is a number
        total_records_text = page.get_by_text("Total Records:").locator("xpath=..").text_content()
        total_records = int(re.search(r"(\d+)", total_records_text).group(1))
        assert total_records > 0

        # table columns
        for column in ["ID", "MODEL", "EVENT", "USER", "TIMESTAMP", "CHANGES", "ACTIONS"]:
            expect(page.get_by_role("columnheader", name=column)).to_be_visible()

        # default filter values
        expect(page.locator("select").first).to_have_value("all")
        expect(page.locator("select").nth(1)).to_have_value("all")
        assert page.locator("input[type='date']").first.input_value() != ""
        assert page.locator("input[type='date']").last.input_value() != ""

        # Model dropdown options
        model_options = page.locator("select").first.locator("option").all_text_contents()
        for expected in ["All Models", "LeaveApplication", "User", "WorkMode", "WorkModeApplication",
                          "Asset", "Project", "LeaveType", "Onboarding", "PeoplePortalQuery",
                          "MarketplaceApp", "UserDocument", "License", "system_backup"]:
            assert expected in model_options

        # Event Type dropdown options
        event_options = page.locator("select").nth(1).locator("option").all_text_contents()
        assert event_options == ["All Events", "Created", "Updated", "Deleted"]

        # table has rows
        assert page.locator("table tbody tr").count() > 0

        browser.close()
