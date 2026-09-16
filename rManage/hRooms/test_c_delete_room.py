import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_delete_room():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Deleting a room shows a native browser confirm() dialog, so accept it
        page.on("dialog", lambda dialog: dialog.accept())

        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-rooms").click()
        time.sleep(2)

        # Delete the room created/edited by the earlier room tests
        search_box = page.get_by_placeholder("Search rooms...")
        search_box.fill("Automation Room")
        time.sleep(1.5)

        row = page.locator("table tbody tr").first
        row_text = row.inner_text()
        assert "Automation Room" in row_text, f"Expected 'Automation Room' in row, got: {row_text}"

        row.get_by_role("button", name="Delete").click()

        wait_for_message(page, re.compile("Room deleted successfully", re.I))
        print("Room deleted successfully.")
        time.sleep(3)
