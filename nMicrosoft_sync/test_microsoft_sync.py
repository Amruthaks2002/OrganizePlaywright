import time
import re

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_microsoft_sync():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page)

        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-navlink-microsoft sync").click()
        expect(page).to_have_url(re.compile(r".*microsoft/sync*"))
        time.sleep(2)