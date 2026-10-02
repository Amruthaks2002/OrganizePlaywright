import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, add_step, open_journeys, journey_card, delete_journeys,
    SESSIONS,
)


def test_step_count_on_card():
    """MS-014: the journey card on the Journeys page shows how many steps the journey has."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name)
            for session in SESSIONS:
                add_step(page, session)

            open_journeys(page)
            expect(journey_card(page, name)).to_contain_text(re.compile(r"(?<!\d)2\s*steps"))
        finally:
            delete_journeys(page, name)

        browser.close()
