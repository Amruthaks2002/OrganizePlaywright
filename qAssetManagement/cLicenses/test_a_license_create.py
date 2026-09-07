import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def select_option(page, container_id, option_text):
    page.locator(f"#{container_id}").click()
    time.sleep(0.5)
    page.locator("li[role=option]", has_text=option_text).first.click()
    time.sleep(0.3)

def test_license_catelogue_create():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")
        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-licences").click()
        time.sleep(2)
        page.get_by_role("link", name="New Licence").click()
        time.sleep(1)

        unique_suffix = str(int(time.time()))

        page.locator("#name").fill(f"Automation License {unique_suffix}")
        select_option(page, "license_publisher_id", "Adobe")
        select_option(page, "license_category_id", "Subscription")

        page.locator("#seat_count").fill("5")
        page.locator("#license_key").fill(f"KEY-{unique_suffix}")

        page.locator("#licensed_to_name").fill("Automation User")
        page.locator("#licensed_to_email").fill("automation@example.com")

        page.locator("#starts_at").fill("2025-01-01")
        page.locator("#expires_at").fill("2026-01-01")

        page.locator("#notes").fill("Created by automation license test.")

        page.get_by_role("button", name="Create Licence").click()
        wait_for_message(page, re.compile("Licence created successfully", re.I))
        print("Licence created successfully.")
        time.sleep(3)

        # Search for the license just created and open it
        if not page.get_by_test_id("sidebar-child-licences").is_visible():
            page.get_by_test_id("sidebar-parent-asset management").click()
            time.sleep(1)
        page.get_by_test_id("sidebar-child-licences").click()
        time.sleep(2)

        search_box = page.get_by_placeholder("Search name, publisher, licensee…")
        search_box.fill(f"Automation License {unique_suffix}")
        time.sleep(1.5)

        row = page.locator("table tbody tr").first
        row.get_by_role("link", name="View").click()
        page.wait_for_url(re.compile(r".*/licenses/\d+$"))
        time.sleep(1)

        # Assign a seat to a user
        page.get_by_role("button", name="Assign Seat").click()
        time.sleep(1)

        page.get_by_placeholder("Search for an employee…").click()
        time.sleep(0.8)
        page.locator("li[role=option]", has_text="Admin User").first.click()
        time.sleep(0.3)

        page.get_by_role("button", name=re.compile("^assign$", re.I)).click()
        wait_for_message(page, re.compile("Seat assigned to", re.I))
        print("Seat assigned successfully.")
        time.sleep(3)