from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, create_journey, unique_journey_name, open_journeys, journey_card, delete_journeys


def test_create_with_designation():
    """OJ-007: a journey created for a designation, with a description, shows both on its card."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name, designation="Business Analyst", description="QA journey for analysts")

            open_journeys(page)
            card = journey_card(page, name)
            expect(card).to_contain_text("Designation : Business Analyst")
            expect(card).to_contain_text("QA journey for analysts")
        finally:
            delete_journeys(page, name)

        browser.close()
