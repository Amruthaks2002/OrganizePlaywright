import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_new_booking():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-meeting room reservation").click()
        time.sleep(2)

        page.get_by_role("button", name="New Booking", exact=True).click()
        time.sleep(1)

        unique_suffix = str(int(time.time()))

        # Pick a room, then pick the first available 30-minute slot for that room
        page.locator("input[type=radio]").first.check(force=True)
        time.sleep(1)

        slot_buttons = page.get_by_role("button", name=re.compile(r"\d{1,2}:\d{2} (AM|PM) - \d{1,2}:\d{2} (AM|PM)"))
        assert slot_buttons.count() > 0, "Expected at least one available slot for the selected room"
        slot_buttons.first.click()
        time.sleep(0.5)

        page.get_by_placeholder("Team retrospective").fill(f"Automation Booking {unique_suffix}")

        page.get_by_role("button", name="Create Booking").click()
        wait_for_message(page, re.compile("Booking created successfully", re.I))
        print("Booking created successfully.")
        time.sleep(3)
