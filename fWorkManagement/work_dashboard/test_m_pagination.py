import re
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_pagination():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()
        main = page.get_by_test_id("main-content")

        first_row_page1 = main.locator('table:has-text("EMPLOYEE") tbody tr').first.inner_text()

        main.get_by_role("button", name="Next »", exact=True).click()
        page.wait_for_timeout(1000)

        page_two_button = main.get_by_role("button", name="2", exact=True)
        expect(page_two_button).to_have_class(re.compile("bg-blue-600"))

        first_row_page2 = main.locator('table:has-text("EMPLOYEE") tbody tr').first.inner_text()
        assert first_row_page1 != first_row_page2, "Expected page 2 to show different results than page 1"

        main.get_by_role("button", name="« Previous", exact=True).click()
        page.wait_for_timeout(1000)
        first_row_back_on_page1 = main.locator('table:has-text("EMPLOYEE") tbody tr').first.inner_text()
        assert first_row_back_on_page1 == first_row_page1, "Expected returning to page 1 to show the original results"

        browser.close()
