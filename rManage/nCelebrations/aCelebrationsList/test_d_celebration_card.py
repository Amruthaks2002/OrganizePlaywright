from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, goto, wide_list_url, celebration_card, EMPLOYEE, CELEBRATION_DATE_TEXT,
)


def test_celebration_card():
    """CEL-004: a wide date range lists the celebration card with its status, details and steps."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, wide_list_url())
        card = celebration_card(page)

        expect(card).to_be_visible()
        expect(card.get_by_text("APPROVED", exact=True)).to_be_visible()
        expect(card.get_by_role("img", name=EMPLOYEE)).to_be_visible()
        expect(card.get_by_text("Work Anniversary (2 years)")).to_be_visible()
        expect(card.get_by_text(CELEBRATION_DATE_TEXT)).to_be_visible()
        for step in ["✓ User Image", "✓ Template", "✓ Final"]:
            expect(card.get_by_text(step, exact=True)).to_be_visible()
        expect(card.get_by_role("link", name="View")).to_be_visible()

        browser.close()
