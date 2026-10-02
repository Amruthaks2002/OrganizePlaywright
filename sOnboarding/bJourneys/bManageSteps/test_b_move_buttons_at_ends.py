from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_steps, step_cards, SAMPLE_JOURNEY_ID


def test_move_buttons_at_ends():
    """MS-002: the first step can't move up and the last step can't move down."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_steps(page, SAMPLE_JOURNEY_ID)
        cards = step_cards(page)

        expect(cards.first.get_by_role("button", name="Move up")).to_be_disabled()
        expect(cards.first.get_by_role("button", name="Move down")).to_be_enabled()
        expect(cards.nth(1).get_by_role("button", name="Move up")).to_be_enabled()
        expect(cards.nth(1).get_by_role("button", name="Move down")).to_be_enabled()
        expect(cards.last.get_by_role("button", name="Move up")).to_be_enabled()
        expect(cards.last.get_by_role("button", name="Move down")).to_be_disabled()

        browser.close()
