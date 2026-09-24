from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_filter_by_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()
        main = page.get_by_test_id("main-content")

        status_filter = main.locator("select").nth(0)
        status_filter.select_option(label="Pending")
        page.wait_for_timeout(1000)

        status_badges = main.locator('table:has-text("EMPLOYEE") tbody tr td:nth-child(5) span')
        count = status_badges.count()
        assert count > 0, "Expected at least one pending request in the results"
        for i in range(count):
            expect(status_badges.nth(i)).to_have_text("pending")

        browser.close()
