import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_catelogue_edit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-asset-catalogue").click()
        time.sleep(2)

        # Edit the latest created asset model (from test_a_catelogue_create)
        search_box = page.get_by_placeholder("Search by name…")
        search_box.fill("Automation Model")
        time.sleep(1)

        row = page.locator("table tbody tr").first
        row.get_by_role("button", name="Edit").click()
        time.sleep(1)

        text_inputs = page.locator("input[type=text]")
        text_inputs.nth(1).fill("Automation Model Edited")
        page.locator("textarea").fill("Updated by automation catalogue edit test.")

        page.get_by_role("button", name="Save Changes").click()
        wait_for_message(page, re.compile("Asset Model updated successfully", re.I))
        print("Asset Model updated successfully.")
        time.sleep(3)
