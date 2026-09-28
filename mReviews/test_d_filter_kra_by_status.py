from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_filter_kra_by_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-reviews").click()
        page.get_by_test_id("sidebar-child-template-content").click()
        main = page.get_by_test_id("main-content")

        main.get_by_role("button", name="Inactive", exact=True).click()
        page.wait_for_timeout(1000)
        inactive_count = main.locator("h4").count()
        assert inactive_count > 0, "Expected at least one inactive KRA"

        main.get_by_role("button", name="Active", exact=True).click()
        page.wait_for_timeout(1000)
        active_count = main.locator("h4").count()
        assert active_count > 0, "Expected at least one active KRA"

        main.get_by_role("button", name="All", exact=True).click()
        page.wait_for_timeout(1000)
        all_count = main.locator("h4").count()
        assert all_count >= max(active_count, inactive_count), (
            "Expected the 'All' filter to show at least as many KRAs as either single-status filter"
        )

        browser.close()
