import datetime
import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_create_event():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-events").click()
        time.sleep(2)

        page.get_by_role("button", name="Create Event", exact=True).click()
        time.sleep(1)

        unique_suffix = str(int(time.time()))
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

        page.locator("#title").fill(f"Automation Event {unique_suffix}")
        page.locator("#category").select_option("1")
        page.locator("#event_date").fill(tomorrow)
        page.locator("#location").fill("Conference Room 1")
        page.locator("#description").fill("Created by automated Playwright test.")

        page.get_by_role("button", name="Create Event", exact=True).last.click()
        wait_for_message(page, re.compile("Event created successfully", re.I))
        print("Event created successfully.")
        time.sleep(3)
