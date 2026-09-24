from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_view_policy_work_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-modes").click()
        main = page.get_by_test_id("main-content")
        main.get_by_role("button", name="Policy Work Modes").click()
        page.wait_for_timeout(1000)

        row = main.locator("table tbody tr", has_text="Probation").filter(has_text="Onsite")
        row.get_by_role("button", name="View").click()
        view_modal = page.locator("div.fixed.inset-0").filter(has_text="Summary").last
        expect(view_modal).to_contain_text("Details", timeout=10000)
        expect(view_modal).to_contain_text("Entire testing")

        browser.close()
