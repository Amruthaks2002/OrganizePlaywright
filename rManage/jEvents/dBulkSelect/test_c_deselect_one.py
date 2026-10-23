from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, card_box, checked_cards,
    select_all_box, expect_selected,
)


def test_deselect_one():
    """EB-003: unticking one card after Select All lowers the count and unticks Select All;
    ticking it again brings Select All back."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix, 3)
            open_events(page, search=prefix)
            select_all_box(page).check()
            expect_selected(page, 3)

            card_box(page, titles[0]).uncheck()
            expect(checked_cards(page)).to_have_count(2)
            expect(select_all_box(page)).not_to_be_checked()
            expect_selected(page, 2)

            card_box(page, titles[0]).check()
            expect(select_all_box(page)).to_be_checked()
            expect_selected(page, 3)
        finally:
            delete_events(page, prefix)

        browser.close()
