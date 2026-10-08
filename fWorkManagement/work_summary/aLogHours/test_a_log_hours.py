from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_log_hours():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-summary").click()
        main = page.get_by_test_id("main-content")

        main.get_by_role("button", name="Log Hours").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Log Working Hours").first
        modal.locator("select").select_option(label="project Beta")
        modal.locator("input[type=number]").fill("2")
        modal.locator("textarea").fill("Auto test A")
        modal.get_by_role("button", name="Log Hours").click()

        expect(page.get_by_text("Working hours logged successfully.")).to_be_visible(timeout=10000)

        main.get_by_role("button", name="Regular Hours").click()
        page.wait_for_timeout(1500)
        row = main.locator("table tbody tr", has_text="Auto test A")
        expect(row).to_contain_text("Admin User")
        expect(row).to_contain_text("project Beta")
        expect(row).to_contain_text("2.00")

        # cleanup
        row.locator("td").last.locator("button").last.click()
        page.wait_for_timeout(500)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Delete Work Log").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Working hours deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
