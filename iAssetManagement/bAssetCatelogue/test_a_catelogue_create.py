import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_catelogue_create():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-asset-catalogue").click()
        time.sleep(2)

        page.get_by_role("button", name="Add Asset Model").click()
        time.sleep(1)

        unique_suffix = str(int(time.time()))
        text_inputs = page.locator("input[type=text]")
        text_inputs.nth(1).fill(f"Automation Model {unique_suffix}")

        category_input = page.get_by_placeholder(re.compile("Select a category", re.I))
        category_input.click()
        time.sleep(0.5)
        page.locator("li[role=option]", has_text="Laptop").first.click()
        time.sleep(0.3)

        text_inputs.nth(2).fill(f"MN-{unique_suffix}")

        number_inputs = page.locator("input[type=number]")
        number_inputs.nth(0).fill("36")
        number_inputs.nth(1).fill("12")

        page.locator("textarea").fill("Created by automation catalogue test.")

        page.get_by_role("button", name="Create", exact=True).click()
        wait_for_message(page, re.compile("Asset Model created successfully", re.I))
        print("Asset Model created successfully.")
        time.sleep(3)
