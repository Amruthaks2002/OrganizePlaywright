import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login


def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_edit_requisition():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page)
        page.wait_for_url("**/dashboard**")

        # Navigate to Resource Requisitions
        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)

        page.get_by_test_id("sidebar-child-resource-requisitions").click()
        time.sleep(2)

        # Search for an existing requisition
        search_box = page.get_by_placeholder("Search requisitions...")
        search_box.fill("Automation Position")
        time.sleep(1.5)

        # Get the first matching requisition
        row = page.locator("table tbody tr").first

        row_text = row.inner_text()
        print(f"Found requisition: {row_text}")

        # Verify that a requisition was found
        assert row.count() > 0, "No requisition found."

        # Click Edit
        row.get_by_role("link", name="Edit", exact=True).click()
        time.sleep(1.5)

        # Edit the requisition name
        edit_text_inputs = page.locator("input[type=text]")
        current_name = edit_text_inputs.nth(0).input_value()

        new_name = f"{current_name} Edited"
        edit_text_inputs.nth(0).fill(new_name)

        # Move through the edit steps
        page.get_by_role("button", name="Next Step", exact=True).click()
        time.sleep(1)

        page.get_by_role("button", name="Next Step", exact=True).click()
        time.sleep(1)

        # Update the requisition
        page.get_by_role("button", name="Update Requisition", exact=True).click()

        wait_for_message(
            page,
            re.compile("Resource requisition updated successfully", re.I)
        )

        print(f"Resource requisition updated successfully: {new_name}")

        time.sleep(3)
        browser.close()