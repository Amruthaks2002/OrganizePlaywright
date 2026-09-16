import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_delete_marketplace():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Removing a listing shows a native browser confirm() dialog, so accept it
        page.on("dialog", lambda dialog: dialog.accept())

        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-marketplace").click()
        time.sleep(2)

        # Approve the request

        page.get_by_role("link", name="Review queue", exact=True).click()
        time.sleep(2)

        approve_buttons = page.get_by_role("button", name="Approve")
        assert approve_buttons.count() > 0, "Expected at least one pending marketplace request"

        latest_approve = approve_buttons.last
        latest_approve.click()

        wait_for_message(page, re.compile("is now live in the marketplace", re.I))
        print("Latest marketplace request approved successfully.")
        time.sleep(2)

        page.get_by_test_id("sidebar-navlink-marketplace").click()
        time.sleep(2)

        page.get_by_test_id("sidebar-navlink-marketplace").click()
        time.sleep(2)

        # Search for the approved marketplace request created by the earlier tests
        search_box = page.get_by_placeholder("Search apps, tools and ideas…")
        search_box.fill("Automation App")
        time.sleep(1.5)

        result = page.locator("a", has_text="Automation App").first
        result_text = result.inner_text()
        assert "Approved" in result_text, f"Expected an approved 'Automation App' result, got: {result_text}"

        result.click()
        time.sleep(2)

        page.get_by_role("button", name="Remove", exact=True).click()
        wait_for_message(page, re.compile("removed from the marketplace", re.I))
        print("Marketplace request removed successfully.")
        time.sleep(3)
