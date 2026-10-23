from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, main_content, journey_url, open_journeys, journey_card,
    delete_journeys,
)


def test_create_journey():
    """OJ-006: a journey with just a name is created active for all designations, and the app opens
    its (empty) Manage Steps page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            journey_id = create_journey(page, name)
            expect(page).to_have_url(journey_url(journey_id))
            expect(main_content(page).get_by_role("heading", name=name)).to_be_visible()
            expect(main_content(page).get_by_text("0 steps")).to_be_visible()

            open_journeys(page)
            card = journey_card(page, name)
            for text in ["Designation : Applicable to all", "Active"]:
                expect(card).to_contain_text(text)
            expect(card).to_contain_text("0")
        finally:
            delete_journeys(page, name)

        browser.close()
