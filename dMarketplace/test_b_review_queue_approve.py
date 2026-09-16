import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_review_queue_approve():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-marketplace").click()
        time.sleep(2)

        page.get_by_role("link", name="Review queue", exact=True).click()
        time.sleep(2)

        # Submissions are listed oldest first, so the latest created request is the last card
        approve_buttons = page.get_by_role("button", name="Approve")
        assert approve_buttons.count() > 0, "Expected at least one pending marketplace request"

        latest_approve = approve_buttons.last
        latest_approve.click()

        wait_for_message(page, re.compile("is now live in the marketplace", re.I))
        print("Latest marketplace request approved successfully.")
        time.sleep(2)
