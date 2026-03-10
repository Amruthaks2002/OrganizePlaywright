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
        page.get_by_test_id("sidebar-navlink-mail logs").click()
        page.locator("select").first.select_option(label="Celebration Wish")
        page.locator('input[type="date"]').first.fill("2026-02-23")
        time.sleep(1)
        page.locator("tbody tr").first.get_by_role("link", name="Happy Work Anniversary").click()
        time.sleep(2)
        expect(page.get_by_text("Congratulations")).to_be_visible()

