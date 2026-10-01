from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_cards, card_name, card_status, card_meta,
    select_policy, detail_badges, employees_count, card_employee_count,
)


def test_select_policy_updates_details():
    """LP-004: clicking another policy card shows that policy's details."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        cards = policy_cards(page)
        assert cards.count() >= 2, "need at least two policies to switch between"
        for card in [cards.nth(1), cards.first]:
            name = card_name(card).inner_text().strip()
            select_policy(page, name)

            meta = card_meta(card).locator("span")
            expected_badges = [card_status(card).inner_text().strip()]
            if meta.count() == 2:
                expected_badges.append(meta.first.inner_text().strip())
            expect(detail_badges(page)).to_have_text(expected_badges)
            assert employees_count(page) == card_employee_count(card)

        browser.close()
