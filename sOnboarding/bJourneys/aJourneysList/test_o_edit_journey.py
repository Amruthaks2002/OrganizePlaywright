from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, journey_dialog,
    fill_journey_form, delete_journeys,
)


def test_edit_journey():
    """OJ-015: Update Journey saves a new name and description."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        new_name = f"{name} updated"
        try:
            create_journey(page, name, description="before")
            open_journeys(page)
            journey_card(page, name).get_by_role("button", name="Edit").click()
            dialog = journey_dialog(page, "Edit Onboarding Journey")
            fill_journey_form(page, dialog, new_name, description="after")
            dialog.get_by_role("button", name="Update Journey").click()
            expect(dialog).to_be_hidden()

            open_journeys(page)
            expect(journey_card(page, new_name)).to_contain_text("after")
            expect(page.get_by_text(name, exact=True)).to_have_count(0)
        finally:
            delete_journeys(page, new_name)
            delete_journeys(page, name)

        browser.close()
