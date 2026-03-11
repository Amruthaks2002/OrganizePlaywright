import time
from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_export_users():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-users").click()
        page.get_by_role("button", name= "Export Users").click()
        time.sleep(3)