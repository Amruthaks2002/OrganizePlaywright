import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login


def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_delete_booking():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Deleting a booking shows a native browser confirm() dialog, so accept it
        page.on("dialog", lambda dialog: dialog.accept())

        login(page)
        page.wait_for_url("**/dashboard**")

        # Go to Meeting Room Reservation
        page.get_by_test_id("sidebar-navlink-meeting room reservation").click()
        time.sleep(2)

        # Search for an existing booking
        search_box = page.get_by_placeholder("Search by meeting title...")
        search_box.fill("automation")
        time.sleep(2)

        # Find the booking and click Delete
        booking = page.get_by_text(re.compile("automation", re.I)).last

        card = booking.locator(
            "xpath=ancestor::div[.//button[normalize-space()='Delete']][1]"
        )

        card.get_by_role("button", name="Delete", exact=True).click()

        # Verify success message
        wait_for_message(
            page,
            re.compile("Booking deleted successfully", re.I)
        )

        print("Booking deleted successfully.")
        time.sleep(3)

        browser.close()