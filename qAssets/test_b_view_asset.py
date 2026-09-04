import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_view_and_checkout_asset():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-assets").click()
        time.sleep(1.5)

        # View the latest created asset (first row in the assets table)
        first_row = page.locator("table tbody tr").first
        first_row.get_by_role("link", name="View").click()
        page.wait_for_url("**/assets/**", timeout=10000)
        time.sleep(1.5)

        # Check out the asset and assign it to a user
        page.get_by_role("button", name="Check Out").click()
        time.sleep(1)

        employee_input = page.get_by_placeholder(re.compile("Search for an employee", re.I))
        employee_input.click()
        time.sleep(0.5)
        page.locator("li[role=option]").first.click()
        time.sleep(0.3)

        assigned_on = page.locator("input[type=date]").first
        assigned_on.fill("2026-09-04")

        page.get_by_role("button", name="Check Out").last.click()
        wait_for_message(page, re.compile("checked out", re.I))
        print("Asset checked out successfully.")
        time.sleep(3)

        # Check in the asset
        page.get_by_role("button", name="Check In").click()
        time.sleep(1)

        returned_on = page.locator("input[type=date]").first
        returned_on.fill("2026-09-04")

        page.get_by_role("button", name="Check In").last.click()
        wait_for_message(page, re.compile("checked in", re.I))
        print("Asset checked in successfully.")
        time.sleep(3)

