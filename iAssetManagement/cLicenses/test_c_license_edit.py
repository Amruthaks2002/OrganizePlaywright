import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_license_catelogue_edit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-licences").click()
        time.sleep(2)

        # Edit the license created by test_a_license_create
        search_box = page.get_by_placeholder("Search name, publisher, licensee…")
        search_box.fill("Automation License")
        time.sleep(1.5)

        row = page.locator("table tbody tr").first
        row.get_by_role("link", name="Edit").click()
        page.wait_for_url("**/licenses/*/edit")
        time.sleep(1)

        page.locator("#name").fill("Automation License Edited")
        page.locator("#notes").fill("Updated by automation license edit test.")

        page.get_by_role("button", name="Save Changes").click()
        wait_for_message(page, re.compile("Licence updated successfully", re.I))
        print("Licence updated successfully.")
        time.sleep(3)