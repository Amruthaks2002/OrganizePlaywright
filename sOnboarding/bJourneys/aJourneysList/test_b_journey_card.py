from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_journeys, journey_card, journey_url, SAMPLE_JOURNEY, SAMPLE_JOURNEY_ID


def test_journey_card():
    """OJ-002: a journey card shows its name, description, designation, status, step count,
    created date, Manage Steps, Edit and Delete."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_journeys(page)

        card = journey_card(page, SAMPLE_JOURNEY)
        expect(card).to_have_count(1)
        for text in ["Happy Onboarding", "Designation : Applicable to all", "Active", "steps", "19 Jun, 2026, 11:43 AM"]:
            expect(card).to_contain_text(text)
        expect(card).to_contain_text("3")
        expect(card.get_by_role("link", name="Manage Steps")).to_have_attribute("href", journey_url(SAMPLE_JOURNEY_ID))
        expect(card.get_by_role("button", name="Edit")).to_be_visible()
        expect(card.get_by_role("button", name="Delete")).to_be_visible()

        browser.close()
