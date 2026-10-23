import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, journey_stats, delete_journeys,
)


def test_create_inactive():
    """OJ-008: a journey created with Active off is shown as Inactive and isn't counted as active."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name, active=False)

            open_journeys(page)
            card = journey_card(page, name)
            expect(card.get_by_text("Inactive", exact=True)).to_be_visible()
            expect(card.get_by_text(re.compile(r"^Active$"))).to_have_count(0)
            total, active, _ = journey_stats(page)
            assert active < total, journey_stats(page)
        finally:
            delete_journeys(page, name)

        browser.close()
