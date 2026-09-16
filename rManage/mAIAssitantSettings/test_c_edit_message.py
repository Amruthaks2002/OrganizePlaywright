import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_edit_message():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-ai-assistant-settings").click()
        time.sleep(2)

        # Find the message created earlier (this page has no search/filter box)
        row = page.locator("table tbody tr").filter(has_text="Automation Message").first
        assert row.count() > 0, "No 'Automation Message' found."

        row.get_by_title("Edit welcome message").click()
        time.sleep(1)

        title_input = page.locator("input[type=text], input:not([type])").first
        title_input.fill("Automation Message Edited")

        page.get_by_role("button", name="Next", exact=True).click()
        time.sleep(1)
        page.get_by_role("button", name="Next", exact=True).click()
        time.sleep(1)

        page.get_by_role("button", name="Save Changes", exact=True).click()
        wait_for_message(page, re.compile("Welcome message updated successfully", re.I))
        print("Welcome message updated successfully.")
        time.sleep(3)
