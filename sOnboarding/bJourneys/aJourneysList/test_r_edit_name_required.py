from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, journey_dialog,
    fill_journey_form, delete_journeys,
)


def test_edit_name_required():
    """OJ-018: Update Journey with the name cleared is blocked and the name is kept."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name)
            open_journeys(page)
            journey_card(page, name).get_by_role("button", name="Edit").click()
            dialog = journey_dialog(page, "Edit Onboarding Journey")

            fill_journey_form(page, dialog, "")
            dialog.get_by_role("button", name="Update Journey").click()
            page.wait_for_timeout(1500)
            expect(dialog).to_be_visible()
            assert dialog.get_by_placeholder("e.g., Software Engineer Onboarding").evaluate("e => !e.checkValidity()")

            open_journeys(page)
            expect(journey_card(page, name)).to_have_count(1)
        finally:
            delete_journeys(page, name)

        browser.close()
