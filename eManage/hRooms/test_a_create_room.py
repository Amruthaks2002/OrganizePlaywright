import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_create_room():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-rooms").click()
        time.sleep(2)

        page.get_by_role("button", name="Add Room", exact=True).click()
        time.sleep(1)

        unique_suffix = str(int(time.time()))
        text_inputs = page.locator("input[type=text]")
        text_inputs.nth(1).fill(f"Automation Room {unique_suffix}")
        text_inputs.nth(2).fill("Calicut")
        page.locator("input[type=number]").fill("10")
        page.locator("textarea").fill("Created by automated Playwright test.")

        page.get_by_role("button", name="Create Room", exact=True).click()
        wait_for_message(page, re.compile("Room created successfully", re.I))
        print("Room created successfully.")
        time.sleep(2)
