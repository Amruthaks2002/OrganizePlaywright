import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_approve_requisition():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-resource-requisitions").click()
        time.sleep(2)

        # Create a requisition first, so there's one to approve
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

        # Search for it and click View
        search_box = page.get_by_placeholder("Search requisitions...")
        search_box.fill(name)
        time.sleep(1.5)

        row = page.locator("table tbody tr").first
        row_text = row.inner_text()
        assert name in row_text, f"Expected '{name}' in row, got: {row_text}"

        row.get_by_role("link", name="View", exact=True).click()
        page.wait_for_url(re.compile(r".*/resource-requisitions/\d+$"))
        time.sleep(1)

        # Initial Approval
        page.get_by_role("button", name="Initial Approval", exact=True).click()
        time.sleep(1)
        page.get_by_role("button", name="Confirm Initial Approval", exact=True).click()
        wait_for_message(page, re.compile("initially approved", re.I))
        print("Resource requisition initially approved.")
        time.sleep(2)

        # Final Approval
        page.get_by_role("button", name="Final Approval", exact=True).click()
        time.sleep(1)
        page.get_by_role("button", name="Confirm Final Approval", exact=True).click()
        wait_for_message(page, re.compile("finally approved", re.I))
        print("Resource requisition finally approved.")
        time.sleep(3)
