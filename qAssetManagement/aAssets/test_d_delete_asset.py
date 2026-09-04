import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_delete_asset():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-assets").click()
        time.sleep(1.5)

        # Delete the latest created asset (first row in the assets table)
        first_row = page.locator("table tbody tr").first
        first_row.get_by_role("button", name="Delete").click()
        time.sleep(1)

        page.get_by_role("button", name="Delete", exact=True).last.click()
        wait_for_message(page, re.compile("deleted successfully", re.I))
        print("Asset deleted successfully.")
        time.sleep(3)