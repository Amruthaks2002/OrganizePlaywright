import re
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_mail_logs_filter():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-navlink-mail logs").click()
        page.locator("select").first.select_option(label="Leave Submitted")

        page.locator("tbody tr").first.get_by_role("link", name = "Leave Application Submitted").click()
        expect(page.get_by_text("submitted a new leave request")).to_be_visible()
        page.get_by_role("link", name="View Request").click()
        time.sleep(3)
        with context.expect_page() as new_page_info:
            page.get_by_role("link", name="View Request").click()
        new_page = new_page_info.value
        new_page.wait_for_load_state()
        expect(new_page).to_have_url(re.compile(r".*/leave/manageRequests"))