from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login



def test_view_request():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page)

        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()

        main = page.get_by_test_id("main-content")

        # Open View for an existing work mode request
        row = main.locator('table tbody tr').first
        row.get_by_role("button", name="View", exact=True).click()

        view_modal = page.locator("div.fixed.inset-0").last

        # Verify request details
        expect(view_modal).to_contain_text("Admin User")
        expect(view_modal).to_contain_text("Work From Home Request")
        expect(view_modal).to_contain_text("Duration")
        expect(view_modal).to_contain_text("Request Status")
        expect(view_modal).to_contain_text("Pending")

        # Close the view modal
        view_modal.get_by_role("button", name="✕").click()
        expect(view_modal).not_to_be_visible()
        

        browser.close()