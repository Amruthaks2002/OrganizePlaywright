from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_filter_by_date_range():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()
        main = page.get_by_test_id("main-content")

        date_inputs = main.locator("input[type='date']")
        date_inputs.nth(0).fill("2026-08-01")
        date_inputs.nth(1).fill("2026-08-31")
        page.wait_for_timeout(1000)

        date_cells = main.locator('table:has-text("EMPLOYEE") tbody tr td:nth-child(3)')
        count = date_cells.count()
        assert count > 0, "Expected at least one request within the selected date range"
        for i in range(count):
            expect(date_cells.nth(i)).to_contain_text("Aug")

        browser.close()
