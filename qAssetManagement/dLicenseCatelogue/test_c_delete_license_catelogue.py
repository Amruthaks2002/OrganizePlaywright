import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_delete_license_catelogue():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-licence-catalogue").click()
        time.sleep(2)

        # Delete the license category created/edited by the earlier license catalogue tests
        search_box = page.get_by_placeholder("Search by name…")
        search_box.fill("Automation Category")
        time.sleep(1.5)

        row = page.locator("table tbody tr").first
        row_text = row.inner_text()
        assert "Automation Category" in row_text, f"Expected 'Automation Category' in row, got: {row_text}"

        row.get_by_role("button", name="Delete").click()
        time.sleep(1)

        page.get_by_role("button", name="Delete", exact=True).last.click()
        wait_for_message(page, re.compile("Licence Category deleted successfully", re.I))
        print("Licence Category deleted successfully.")
        time.sleep(3)
