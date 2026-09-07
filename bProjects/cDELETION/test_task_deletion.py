from playwright.sync_api import sync_playwright
import time

def test_search_project():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://organice.qc.iocod.com")
        page.fill("#email", "admin@example.com")
        page.fill("#password", "password")
        page.click("[data-testid='sign-in-button']")
        page.click("[data-testid='sidebar-navlink-projects']")
        search_box = page.get_by_placeholder("Search projects...")
        search_box.fill("Automation")
        search_box.press("Enter")
        time.sleep(3)
        page.locator("button[title='Delete']").first.click()
        time.sleep(1)
        delete_btn = page.locator("button:has-text('Delete')").filter(has_text="Delete")
        delete_btn.wait_for(state="visible")
        delete_btn.click()
        time.sleep(5)

