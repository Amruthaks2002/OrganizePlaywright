from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, delete_journeys,
)


def test_long_name_and_description():
    """OJ-012: a long name with special / non-Latin characters and a long description are saved as typed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = f"{unique_journey_name()} – Ingénieur's Onboarding & Setup 入职 " + "x" * 60
        description = "Long description. " * 40
        try:
            create_journey(page, name, description=description)

            open_journeys(page)
            card = journey_card(page, name)
            expect(card).to_have_count(1)
            expect(card).to_contain_text(description.strip())
        finally:
            delete_journeys(page, name)

        browser.close()
