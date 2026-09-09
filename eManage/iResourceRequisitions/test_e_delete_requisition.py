import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_delete_requisition():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-resource-requisitions").click()
        time.sleep(2)

        # Create a requisition first, so there's one to delete
        page.get_by_text("New Requisition", exact=True).first.click()
        time.sleep(2)

        unique_suffix = str(int(time.time()))
        name = f"Automation Position {unique_suffix}"

        text_inputs = page.locator("input[type=text]")
        text_inputs.nth(0).fill(name)
        page.locator("textarea").fill("Created by automated Playwright test.")
        text_inputs.nth(1).fill("Bachelor's Degree")

        reporting = page.get_by_placeholder("Search reporting person...")
        reporting.click()
        time.sleep(1.5)
        page.locator("li[role=option]").first.click()
        time.sleep(0.3)

        page.get_by_role("button", name="Next", exact=True).click()
        time.sleep(1)

        page.get_by_role("button", name="Add Skill").first.click()
        time.sleep(0.5)
        page.get_by_placeholder("Enter required skill").fill("Python")

        page.get_by_role("button", name="Next", exact=True).click()
        time.sleep(1)

        page.locator("textarea").nth(1).fill("Automated Playwright job description.")
        page.get_by_role("button", name="Submit Request", exact=True).click()
        wait_for_message(page, re.compile("Resource requisition created successfully", re.I))
        print("Resource requisition created successfully.")
        time.sleep(2)

        # Go back to the list and delete it
        page.get_by_test_id("sidebar-child-resource-requisitions").click()
        time.sleep(2)

        search_box = page.get_by_placeholder("Search requisitions...")
        search_box.fill(name)
        time.sleep(1.5)

        row = page.locator("table tbody tr").first
        row_text = row.inner_text()
        assert name in row_text, f"Expected '{name}' in row, got: {row_text}"

        row.get_by_role("button", name="Delete", exact=True).click()
        time.sleep(1)

        page.get_by_role("button", name="Delete", exact=True).last.click()
        wait_for_message(page, re.compile("Resource requisition deleted successfully", re.I))
        print("Resource requisition deleted successfully.")
        time.sleep(3)
