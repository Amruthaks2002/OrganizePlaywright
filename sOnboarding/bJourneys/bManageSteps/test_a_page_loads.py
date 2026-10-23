from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_journeys, journey_card, main_content, journey_url, step_titles, step_cards, JOURNEYS_URL,
    SAMPLE_JOURNEY, SAMPLE_JOURNEY_ID,
)


def test_page_loads():
    """MS-001: Manage Steps opens the journey's steps in order with the step / required counts,
    and Back to Journeys returns to the list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_journeys(page)
        journey_card(page, SAMPLE_JOURNEY).get_by_role("link", name="Manage Steps").click()
        expect(page).to_have_url(journey_url(SAMPLE_JOURNEY_ID))
        main = main_content(page)

        expect(main.get_by_role("heading", name=SAMPLE_JOURNEY).first).to_be_visible()
        expect(main.get_by_text("3 steps", exact=True)).to_be_visible()
        expect(main.get_by_text("2 required", exact=True)).to_be_visible()
        expect(main.get_by_role("button", name="Add Step")).to_be_visible()
        assert step_titles(page) == ["First Day Forward", "The Starter Track", "Materials Only"], step_titles(page)
        expect(step_cards(page).nth(0).get_by_text("Required", exact=True)).to_have_count(0)
        expect(step_cards(page).nth(1).get_by_text("Required", exact=True)).to_be_visible()
        for i in range(3):
            for action in ["Move up", "Move down", "Edit step", "Delete step"]:
                expect(step_cards(page).nth(i).get_by_role("button", name=action)).to_be_visible()

        main.get_by_role("link", name="Back to Journeys").click()
        expect(page).to_have_url(JOURNEYS_URL)

        browser.close()
