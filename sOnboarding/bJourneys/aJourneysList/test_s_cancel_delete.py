from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, modal, delete_journeys,
)


def test_cancel_delete():
    """OJ-019: Delete asks for confirmation naming the journey, and Cancel keeps it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name)
            open_journeys(page)
            journey_card(page, name).get_by_role("button", name="Delete").click()
            dialog = modal(page, "Delete Journey")
            expect(dialog.get_by_text(f'Are you sure you want to delete "{name}"?')).to_be_visible()

            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()
            open_journeys(page)
            expect(journey_card(page, name)).to_have_count(1)
        finally:
            delete_journeys(page, name)

        browser.close()
