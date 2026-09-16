import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login


def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_cancel_requisition():
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

        # Verify that a requisition was found
        assert row.count() > 0, "No requisition found."

        row_text = row.inner_text()
        print(f"Found requisition: {row_text}")

        # Click Cancel
        row.get_by_role("button", name="Cancel", exact=True).click()
        time.sleep(1)

        # Confirm cancellation
        page.get_by_role("button", name="Confirm Cancel", exact=True).click()

        # Verify success message
        wait_for_message(
            page,
            re.compile("Resource requisition has been cancelled", re.I)
        )

        print("Resource requisition cancelled successfully.")

        time.sleep(2)
        browser.close()