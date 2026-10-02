from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, create_journey, unique_journey_name, open_journeys, main_content, delete_journeys


def test_duplicate_name():
    """OJ-011: journey names don't have to be unique - a second journey with the same name is
    created as a separate journey (the app currently allows it)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            first = create_journey(page, name)
            second = create_journey(page, name)
            assert first != second

            open_journeys(page)
            expect(main_content(page).get_by_text(name, exact=True)).to_have_count(2)
        finally:
            delete_journeys(page, name)

        browser.close()
