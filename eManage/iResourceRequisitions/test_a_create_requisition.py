import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_create_requisition():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-resource-requisitions").click()
        time.sleep(2)

        page.get_by_text("New Requisition", exact=True).first.click()
        time.sleep(2)

        unique_suffix = str(int(time.time()))

        # Step 1: Basic Details
        text_inputs = page.locator("input[type=text]")
        text_inputs.nth(0).fill(f"Automation Position {unique_suffix}")
        page.locator("textarea").fill("Created by automated Playwright test.")
        text_inputs.nth(1).fill("Bachelor's Degree")

        reporting = page.get_by_placeholder("Search reporting person...")
        reporting.click()
        time.sleep(1.5)
        page.locator("li[role=option]").first.click()
        time.sleep(0.3)

        page.get_by_role("button", name="Next", exact=True).click()
        time.sleep(1)

        # Step 2: Interview & Skills
        page.get_by_role("button", name="Add Skill").first.click()
        time.sleep(0.5)
        page.get_by_placeholder("Enter required skill").fill("Python")

        page.get_by_role("button", name="Next", exact=True).click()
        time.sleep(1)

        # Step 3: Job Details
        page.locator("textarea").nth(1).fill("Automated Playwright job description.")
        page.get_by_role("button", name="Submit Request", exact=True).click()

        wait_for_message(page, re.compile("Resource requisition created successfully", re.I))
        print("Resource requisition created successfully.")
        time.sleep(3)
