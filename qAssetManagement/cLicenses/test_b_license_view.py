import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_license_catelogue_view():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-licences").click()
        time.sleep(2)

        # Search for the license created by test_a_license_create
        search_box = page.get_by_placeholder("Search name, publisher, licensee…")
        search_box.fill("Automation License")
        time.sleep(1.5)

        rows = page.locator("table tbody tr")
        assert rows.count() == 1, f"Expected 1 matching license, found {rows.count()}"

        row_text = rows.first.inner_text()
        assert "Automation License" in row_text, f"Expected 'Automation License' in row, got: {row_text}"
        print(f"License found: {row_text}")
        time.sleep(3)