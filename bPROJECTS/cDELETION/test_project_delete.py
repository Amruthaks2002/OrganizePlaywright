from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
def test_delete_project():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.click("[data-testid='sidebar-navlink-projects']")
        page.locator("button.border-red-300").first.click()
        page.get_by_role("button", name="Delete").click()
        success_msg = page.locator("text=Project deleted successfully.")
        expect(success_msg).to_be_visible()
        print("project deleted successfully")


