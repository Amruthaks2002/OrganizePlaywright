from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_filter_by_search_employee():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()
        main = page.get_by_test_id("main-content")

        search = main.locator(".vs__search")
        search.click()
        search.fill("Admin")
        page.get_by_role("option", name="Admin User").click(timeout=20000)
        page.wait_for_timeout(1000)

        rows = main.locator('table:has-text("EMPLOYEE") tbody tr')
        count = rows.count()
        assert count > 0, "Expected at least one request for Admin User"
        for i in range(count):
            expect(rows.nth(i).locator("td").first).to_have_text("Admin User")

        browser.close()
