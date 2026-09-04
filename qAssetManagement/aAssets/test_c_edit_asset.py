import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_edit_asset():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-assets").click()
        time.sleep(1.5)

        # Edit the latest created asset (first row in the assets table)
        first_row = page.locator("table tbody tr").first
        first_row.get_by_role("link", name="Edit").click()
        page.wait_for_url("**/edit**", timeout=10000)
        time.sleep(1.5)

        unique_suffix = str(int(time.time()))

        page.locator("#name").fill(f"Automation Test Asset - Edited {unique_suffix}")
        page.locator("#warranty_provider").fill("Dell Warranty Updated")
        page.locator("#warranty_reference_number").fill(f"WREF-{unique_suffix}")
        page.locator("#purchase_cost").fill("55000")
        page.locator("#notes").fill("Updated by automation edit test.")

        page.get_by_role("button", name="Save Changes").click()
        wait_for_message(page, re.compile("updated successfully", re.I))
        print("Asset updated successfully.")
        time.sleep(3)