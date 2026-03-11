import time
from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_edit_users():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-users").click()
        page.get_by_placeholder("Name, email, emp id, hire year").fill("Auto")
        time.sleep(2)
        first_row = page.locator("tbody tr").first
        first_row.get_by_role("link", name="Performance").click()
        page.get_by_role("link", name="View Full Year Leave Details").click()
        time.sleep(2)