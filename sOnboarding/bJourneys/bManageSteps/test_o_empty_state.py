from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, main_content, add_step_dialog, delete_journeys,
)


def test_empty_state():
    """MS-015: a journey without steps shows the "No steps yet" state, and Add First Step opens Add Step."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name)
            main = main_content(page)
            expect(main.get_by_text("No steps yet")).to_be_visible()
            expect(main.get_by_text("This journey doesn't have any steps. Add your first step to get started.")).to_be_visible()

            main.get_by_role("button", name="Add First Step").click()
            expect(add_step_dialog(page)).to_be_visible()
        finally:
            page.keyboard.press("Escape")
            delete_journeys(page, name)

        browser.close()
