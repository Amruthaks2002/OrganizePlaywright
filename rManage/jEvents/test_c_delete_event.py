import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login


def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_delete_event():
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

        # Find the event
        name_el = page.get_by_text("Automation Event", exact=False).first
        assert name_el.count() > 0, "No event found."

        # Get the event card
        card = name_el.locator(
            "xpath=ancestor::div[contains(@class,'rounded-3xl')][1]"
        )

        # Select the event
        card.locator("input[type=checkbox]").check(force=True)
        time.sleep(0.5)

        # Delete selected event
        page.get_by_role(
            "button",
            name="Delete Selected",
            exact=True
        ).click()

        time.sleep(1)

        # Confirm deletion
        page.get_by_role(
            "button",
            name="Delete",
            exact=True
        ).click()

        # Verify success message
        wait_for_message(
            page,
            re.compile(r"Successfully deleted \d+ event\(s\)", re.I)
        )

        print("Event deleted successfully.")

        time.sleep(3)
        browser.close()