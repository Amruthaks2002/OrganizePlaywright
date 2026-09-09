import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login


def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=10000)
    return msg


def test_edit_event():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page)
        page.wait_for_url("**/dashboard**")

        # Navigate to Events
        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)

        page.get_by_test_id("sidebar-child-events").click()
        time.sleep(2)

        # Search for an existing event
        search_box = page.get_by_label("Search")
        search_box.fill("Automation Event")
        time.sleep(1.5)

        # Verify that an event was found
        event = page.get_by_text("Edit Event", exact=True).first
        assert event.count() > 0, "No event found."

        # Click Edit Event
        event.click()
        time.sleep(1)

        # Edit the event title
        title_input = page.locator("#title")
        current_name = title_input.input_value()

        new_name = f"{current_name} Edited"
        title_input.fill(new_name)

        # Update the event
        page.get_by_role("button", name="Update Event", exact=True).click()

        # Verify success message
        wait_for_message(
            page,
            re.compile("Event updated successfully", re.I)
        )

        print(f"Event updated successfully: {new_name}")

        time.sleep(3)
        browser.close()