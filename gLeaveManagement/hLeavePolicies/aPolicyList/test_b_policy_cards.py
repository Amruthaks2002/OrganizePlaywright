import re
from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_cards, card_name, card_status, card_meta,
)


def test_policy_cards():
    """LP-002: every policy card shows its name, status badge and employee count."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        cards = policy_cards(page).all()
        assert len(cards) > 0
        for card in cards:
            expect(card_name(card)).not_to_be_empty()
            expect(card_status(card)).to_have_text(re.compile(r"^(Active|Inactive)$"))
            # region (optional) then the employee count
            expect(card_meta(card).locator("span").last).to_have_text(re.compile(r"^\s*\d+\s*$"))

        browser.close()
