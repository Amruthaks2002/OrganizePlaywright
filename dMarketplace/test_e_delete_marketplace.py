import re
import time

from playwright.sync_api import sync_playwright
from utils.marketplace_helper import open_browser, create_app, delete_apps, review_card, app_card, show_url

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_delete_marketplace():
    with sync_playwright() as p:
        browser, page = open_browser(p)

        # Removing a listing shows a native browser confirm() dialog, so accept it
        page.on("dialog", lambda dialog: dialog.accept())

        page.wait_for_url("**/dashboard**")

        # Remove a request this test created, never someone else's listing
        name = f"Automation App {int(time.time())}"
        try:
            create_app(page, name, category="Productivity")

            page.get_by_test_id("sidebar-navlink-marketplace").click()
            time.sleep(2)

            # Approve the request

            page.get_by_role("link", name="Review queue", exact=True).click()
            time.sleep(2)

            review_card(page, name).get_by_role("button", name="Approve").click()

            wait_for_message(page, re.compile("is now live in the marketplace", re.I))
            print("Marketplace request approved successfully.")
            time.sleep(2)

            page.get_by_test_id("sidebar-navlink-marketplace").click()
            time.sleep(2)

            # Search for the approved marketplace request
            search_box = page.get_by_placeholder("Search apps, tools and ideas…")
            search_box.fill(name)
            time.sleep(1.5)

            result = app_card(page, name)
            result_text = result.inner_text()
            assert "Approved" in result_text, f"Expected '{name}' to be approved, got: {result_text}"

            result.click()
            time.sleep(2)

            page.get_by_role("button", name="Remove", exact=True).click()
            wait_for_message(page, re.compile("removed from the marketplace", re.I))
            assert page.request.get(show_url(name)).status == 404
            print("Marketplace request removed successfully.")
        finally:
            delete_apps(page, name)

        browser.close()
