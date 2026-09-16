import time

from playwright.sync_api import sync_playwright , expect
from utils.login_helper import login

def test_wfh_submitted():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page  = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-navlink-mail template editor").click()
        page.locator("#mail-live-editor-btn-fullscreen").click()
        time.sleep(1)
        page.locator("#mail-live-editor-btn-fullscreen").click()
        time.sleep(1)




