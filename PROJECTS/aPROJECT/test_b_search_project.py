from playwright.sync_api import sync_playwright, expect
import time
from utils.login_helper import login

def test_search_project():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)

        page.click("[data-testid='sidebar-navlink-projects']")
        search_box=page.get_by_placeholder("Search projects...")
        search_box.fill("Automation")
        search_box.press("Enter")
        time.sleep(5)
        heading = page.locator('[data-testid="topbar-header-slot"]')
        expect(heading).to_contain_text("Automation")
        print("Heading is:", heading.inner_text())





