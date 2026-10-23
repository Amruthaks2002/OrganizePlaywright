import os
from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import BASE_URL, APP_RELEASES_URL


def test_logged_out_redirects_to_login():
    """AR-054: someone who isn't signed in is sent to the login page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        page = browser.new_context().new_page()

        page.goto(APP_RELEASES_URL)
        expect(page).to_have_url(f"{BASE_URL}/login")

        browser.close()
