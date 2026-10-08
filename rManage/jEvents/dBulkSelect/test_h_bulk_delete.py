from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, select_cards, confirm_delete,
    card_titles, dock, main_content, EMPTY_LIST,
)


def test_bulk_delete():
    """EB-008: deleting two of three selected events removes exactly those two and hides the dock."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix, 3)
            open_events(page, search=prefix)
            select_cards(page, titles[0], titles[1])

            confirm_delete(page, 2)
            expect(dock(page)).to_be_hidden()

            open_events(page, search=prefix)
            assert card_titles(page) == [titles[2]], card_titles(page)
            open_events(page, search=titles[0])
            expect(main_content(page).get_by_text(EMPTY_LIST)).to_be_visible()
        finally:
            delete_events(page, prefix)

        browser.close()
