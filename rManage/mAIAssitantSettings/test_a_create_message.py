import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_create_message():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-ai-assistant-settings").click()
        time.sleep(2)

        page.get_by_role("button", name=re.compile("^create message$", re.I)).click()
        time.sleep(1)

        unique_suffix = str(int(time.time()))

        # Step 1: Content
        page.get_by_placeholder("e.g. HR Assistant Onboarding Welcome").fill(f"Automation Message {unique_suffix}")
        page.locator("#greetingInput").fill("Hello {{user_name}} from automation!")
        page.locator("#descInput").fill("Created by automated Playwright test.")

        page.get_by_role("button", name="Next", exact=True).click()
        time.sleep(1)

        # Step 2: Actions - left empty (optional)
        page.get_by_role("button", name="Next", exact=True).click()
        time.sleep(1)

        # Step 3: Targeting - left at default "Public (Everyone)"
        page.get_by_role("button", name="Create Message", exact=True).last.click()

        wait_for_message(page, re.compile("Welcome message created successfully", re.I))
        print("Welcome message created successfully.")
        time.sleep(3)
