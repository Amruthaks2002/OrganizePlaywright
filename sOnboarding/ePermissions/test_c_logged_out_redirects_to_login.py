import os
import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import protected_urls


def test_logged_out_redirects_to_login():
    """PM-003: opening an onboarding page without logging in sends you to the login page."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        page = browser.new_page()

        for url in protected_urls():
            page.goto(url)
            expect(page).to_have_url(re.compile(r"/login$"))
            expect(page.get_by_test_id("sign-in-button")).to_be_visible()

        browser.close()
