import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_mail_logs_type_and_status_filter():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page)

        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-logs").click()
        mail_log_link = page.get_by_test_id("sidebar-child-mail-log")
        mail_log_link.wait_for(state="visible")
        mail_log_link.click()
        page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
        time.sleep(1)

        # widen the date range so every event type below has a chance of matching data
        page.locator("input[type='date']").first.fill("2020-01-01")
        time.sleep(1)

        for label in ["Leave Approved", "Leave Submitted", "Leave Rejected", "User Created"]:
            page.locator("select").first.select_option(label=label)
            time.sleep(2)
            page.locator("tbody tr").first.wait_for()
            events = page.locator("tbody tr td:nth-child(3) span")
            count = events.count()
            for i in range(count):
                text = events.nth(i).text_content().strip()
                assert text == label, f"Unexpected event found: {text}"

        page.get_by_role("button", name="Reset").click()
        time.sleep(1)

        page.locator("select").last.select_option(label="Sent")
        time.sleep(2)
        page.locator("tbody tr").first.wait_for()
        statuses = page.locator("tbody tr td:nth-child(4) span")
        count = statuses.count()
        assert count > 0
        for i in range(count):
            text = statuses.nth(i).text_content().strip()
            assert text == "sent", f"Unexpected status found: {text}"

        page.locator("select").last.select_option(label="Failed")
        time.sleep(2)
        page.locator("tbody tr").first.wait_for()
        statuses = page.locator("tbody tr td:nth-child(4) span")
        count = statuses.count()
        assert count > 0
        for i in range(count):
            text = statuses.nth(i).text_content().strip()
            assert text == "failed", f"Unexpected status found: {text}"

        browser.close()
