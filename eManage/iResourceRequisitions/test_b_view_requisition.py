import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login


def test_view_requisition():
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

        # Search for the existing requisition
        search_box = page.get_by_placeholder("Search requisitions...")
        search_box.fill("Automation Position")
        time.sleep(1.5)

        # Get the first matching requisition
        row = page.locator("table tbody tr").first

        row_text = row.inner_text()
        print(f"Found requisition: {row_text}")

        # Click View
        row.get_by_role("link", name="View", exact=True).click()

        # Verify requisition details page
        page.wait_for_url(re.compile(r".*/resource-requisitions/\d+$"))
        time.sleep(1)

        assert page.get_by_text("Workflow Progress", exact=True).count() > 0

        print("Resource requisition viewed successfully.")

        time.sleep(3)
        browser.close()