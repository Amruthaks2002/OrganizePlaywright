import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login


def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_view_message():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page)
        page.wait_for_url("**/dashboard**")

        # Navigate to AI Assistant Settings
        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)

        page.get_by_test_id(
            "sidebar-child-ai-assistant-settings"
        ).click()
        time.sleep(2)

        # Find an existing message row (this page has no search/filter box)
        row = page.locator("table tbody tr").filter(
            has_text="Automation Message"
        ).first

        assert row.count() > 0, "No message found."

        # Open message preview
        row.get_by_title("Preview welcome card").click()
        time.sleep(1)

        # Verify preview
        wait_for_message(
            page,
            re.compile("Live Welcome Card Preview", re.I)
        )

        print("Message preview opened successfully.")

        time.sleep(3)
        browser.close()