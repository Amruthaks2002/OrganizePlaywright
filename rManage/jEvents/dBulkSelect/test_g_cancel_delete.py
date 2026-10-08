from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, select_cards, open_bulk_delete,
    checked_cards, card_titles, expect_selected,
)


def test_cancel_delete():
    """EB-007: Cancel closes the confirmation, deletes nothing and keeps the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix)
            open_events(page, search=prefix)
            select_cards(page, *titles)

            dialog = open_bulk_delete(page)
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()
            expect(checked_cards(page)).to_have_count(2)
            expect_selected(page, 2)

            open_events(page, search=prefix)
            assert sorted(card_titles(page)) == sorted(titles), card_titles(page)
        finally:
            delete_events(page, prefix)

        browser.close()
