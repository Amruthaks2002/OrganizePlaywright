import datetime
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_celebrations, celebration_cards, empty_state, add_months, CELEBRATION_DATE,
)


def test_default_range_empty_state():
    """CEL-003: with nothing in the default date range the list shows the empty state."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_celebrations(page)
        today = datetime.date.today()
        assert not today <= CELEBRATION_DATE <= add_months(today, 3), \
            "the only celebration falls in the default range, so there's no empty state to check"

        expect(empty_state(page)).to_be_visible()
        expect(celebration_cards(page)).to_have_count(0)

        browser.close()
