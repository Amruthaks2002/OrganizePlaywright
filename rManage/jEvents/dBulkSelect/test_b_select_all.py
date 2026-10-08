from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, card_boxes, checked_cards,
    select_all_box, expect_selected,
)


def test_select_all():
    """EB-002: Select All ticks every event card shown and the dock counts them all."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_events(page, prefix, 3)
            open_events(page, search=prefix)
            expect(card_boxes(page)).to_have_count(3)

            select_all_box(page).check()
            expect(checked_cards(page)).to_have_count(3)
            expect_selected(page, 3)
        finally:
            delete_events(page, prefix)

        browser.close()
