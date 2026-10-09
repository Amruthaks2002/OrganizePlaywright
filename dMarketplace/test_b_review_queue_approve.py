import re
import time

from playwright.sync_api import sync_playwright
from utils.marketplace_helper import open_browser, create_app, delete_apps, app_data, review_card

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_review_queue_approve():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        page.wait_for_url("**/dashboard**")

        # Approve a request this test created, never someone else's real submission
        name = f"Automation App {int(time.time())}"
        try:
            create_app(page, name, category="Productivity")

            page.get_by_test_id("sidebar-navlink-marketplace").click()
            time.sleep(2)

            page.get_by_role("link", name="Review queue", exact=True).click()
            time.sleep(2)

            review_card(page, name).get_by_role("button", name="Approve").click()

            wait_for_message(page, re.compile("is now live in the marketplace", re.I))
            assert app_data(page, name)["status"] == "approved"
            print("Marketplace request approved successfully.")
        finally:
            delete_apps(page, name)

        browser.close()
