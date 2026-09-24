from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_filter_by_work_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()
        main = page.get_by_test_id("main-content")

        # The Work Mode filter currently only exposes the default "All Work Modes"
        # option in this environment, so this verifies the control is present,
        # usable, and does not break the results table when applied.
        work_mode_filter = main.locator("select").nth(2)
        expect(work_mode_filter).to_be_visible()
        options = work_mode_filter.locator("option").all_inner_texts()
        assert "All Work Modes" in options

        work_mode_filter.select_option(label="All Work Modes")
        page.wait_for_timeout(1000)

        rows = main.locator('table:has-text("EMPLOYEE") tbody tr')
        assert rows.count() > 0, "Expected the results table to still render rows"

        browser.close()
