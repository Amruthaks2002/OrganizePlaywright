from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_journeys, open_create_journey, fill_journey_form, unique_journey_name, main_content,
    delete_journeys,
)


def test_cancel_create():
    """OJ-005: Cancel closes the dialog without creating the journey."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            open_journeys(page)
            dialog = open_create_journey(page)
            fill_journey_form(page, dialog, name, description="should not be saved")
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()

            open_journeys(page)
            expect(main_content(page).get_by_text(name, exact=True)).to_have_count(0)
        finally:
            delete_journeys(page, name)

        browser.close()
