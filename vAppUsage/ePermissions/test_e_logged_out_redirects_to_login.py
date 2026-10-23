import os
from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import BASE_URL, APP_USAGE_URL, ACTIVITIES_URL


def test_logged_out_redirects_to_login():
    """PM-005: someone who isn't signed in is sent to the login page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        page = browser.new_context().new_page()

        for url in [APP_USAGE_URL, ACTIVITIES_URL]:
            page.goto(url)
            expect(page).to_have_url(f"{BASE_URL}/login")

        browser.close()
