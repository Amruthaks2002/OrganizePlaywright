import re
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def test_mail_logs_leave_rejected():
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

        page.locator("select").first.select_option(label="Leave Rejected")
        time.sleep(1)

        page.locator("tbody tr").first.get_by_role("link", name="Leave Application Rejected").click()
        expect(page.get_by_text("has been rejected")).to_be_visible()

        # unlike the "Leave Submitted" email, this action link navigates in the
        # same tab rather than opening a new one
        page.get_by_role("link", name="View Your Leave Applications").click()
        expect(page).to_have_url(re.compile(r".*/leave/dashboard"))

        browser.close()
