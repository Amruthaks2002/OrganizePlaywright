from playwright.sync_api import sync_playwright , expect
from utils.login_helper import login
import re
import  time

def test_wfh_submitted():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page  = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-navlink-mail logs").click()
        page.locator("select").first.select_option(label="WFH Approved")

        page.locator("tbody tr").first.get_by_role("link", name="WFH Request Approved").click()
        expect(page.get_by_text(" Work From Home Request has been approved")).to_be_visible()

        with context.expect_page() as new_page_info:
            page.get_by_role("link", name="View Request").click()
        new_page = new_page_info.value
        new_page.wait_for_load_state()
        expect(new_page).to_have_url(re.compile(r".*/hours"))