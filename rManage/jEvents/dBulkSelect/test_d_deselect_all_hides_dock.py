from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, card_box, checked_cards,
    select_all_box, dock, expect_selected,
)


def test_deselect_all_hides_dock():
    """EB-004: unticking Select All, or every card one by one, clears the selection and hides the dock."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix)
            open_events(page, search=prefix)

            select_all_box(page).check()
            expect_selected(page, 2)
            select_all_box(page).uncheck()
            expect(checked_cards(page)).to_have_count(0)
            expect(dock(page)).to_be_hidden()

            for title in titles:
                card_box(page, title).check()
            expect_selected(page, 2)
            for title in titles:
                card_box(page, title).uncheck()
            expect(dock(page)).to_be_hidden()
        finally:
            delete_events(page, prefix)

        browser.close()
