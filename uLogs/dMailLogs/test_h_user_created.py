import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_mail_logs_user_created():
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

        page.locator("select").first.select_option(label="User Created")
        time.sleep(1)

        page.locator("tbody tr").first.get_by_role("link", name="Welcome Email").click()
        time.sleep(1)
        expect(page.get_by_text("Recipient")).to_be_visible()

        browser.close()
