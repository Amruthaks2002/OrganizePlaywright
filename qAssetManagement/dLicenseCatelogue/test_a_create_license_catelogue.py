import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_create_license_catelogue():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-licence-catalogue").click()
        time.sleep(2)

        page.get_by_role("button", name="Add Licence Category").click()
        time.sleep(1)

        unique_suffix = str(int(time.time()))
        text_inputs = page.locator("input[type=text]")
        text_inputs.nth(1).fill(f"Automation Category {unique_suffix}")
        page.locator("textarea").fill("Created by automation license category test.")

        page.get_by_role("button", name="Create", exact=True).click()
        wait_for_message(page, re.compile("Licence Category created successfully", re.I))
        print("Licence Category created successfully.")
        time.sleep(3)
