from playwright.sync_api import sync_playwright
import time
from utils.login_helper import login


def test_add_note():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")
        time.sleep(3)
        from playwright.sync_api import expect
        expect(page.get_by_text("Admin User").first).to_be_visible()
