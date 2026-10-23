from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, journey_dialog, vue_select,
    delete_journeys,
)


def test_edit_designation():
    """OJ-016: editing can change the designation, and clearing it makes the journey apply to all."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name, designation="Business Analyst")

            open_journeys(page)
            journey_card(page, name).get_by_role("button", name="Edit").click()
            dialog = journey_dialog(page, "Edit Onboarding Journey")
            vue_select(page, dialog, None, "Accountant")
            dialog.get_by_role("button", name="Update Journey").click()
            expect(dialog).to_be_hidden()
            open_journeys(page)
            expect(journey_card(page, name)).to_contain_text("Designation : Accountant")

            journey_card(page, name).get_by_role("button", name="Edit").click()
            dialog = journey_dialog(page, "Edit Onboarding Journey")
            dialog.get_by_role("button", name="Clear Selected").click()
            dialog.get_by_role("button", name="Update Journey").click()
            expect(dialog).to_be_hidden()
            open_journeys(page)
            expect(journey_card(page, name)).to_contain_text("Designation : Applicable to all")
        finally:
            delete_journeys(page, name)

        browser.close()
