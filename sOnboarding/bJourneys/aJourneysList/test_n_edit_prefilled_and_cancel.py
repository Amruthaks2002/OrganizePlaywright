from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, journey_dialog,
    fill_journey_form, is_active_on, delete_journeys,
)


def test_edit_prefilled_and_cancel():
    """OJ-014: Edit opens the journey prefilled, and Cancel discards any change."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name, designation="Business Analyst", description="QA description")
            open_journeys(page)
            journey_card(page, name).get_by_role("button", name="Edit").click()
            dialog = journey_dialog(page, "Edit Onboarding Journey")
            expect(dialog.get_by_text("Update journey details.")).to_be_visible()
            expect(dialog.get_by_placeholder("e.g., Software Engineer Onboarding")).to_have_value(name)
            expect(dialog.locator(".vs__selected")).to_have_text("Business Analyst")
            expect(dialog.get_by_placeholder("Briefly describe the purpose of this journey...")).to_have_value("QA description")
            assert is_active_on(dialog)

            fill_journey_form(page, dialog, f"{name} changed")
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()

            open_journeys(page)
            expect(journey_card(page, name)).to_have_count(1)
            expect(page.get_by_text(f"{name} changed")).to_have_count(0)
        finally:
            delete_journeys(page, name)

        browser.close()
