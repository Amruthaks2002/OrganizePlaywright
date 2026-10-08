from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, select_cards, confirm_delete,
    open_bulk_delete, card_titles,
)


def test_delete_single():
    """EB-009: the bulk delete also works for a single event, and the dialog says 1 event(s)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix)
            open_events(page, search=prefix)
            select_cards(page, titles[1])

            dialog = open_bulk_delete(page)
            expect(dialog).to_contain_text("delete 1 selected event(s)?")
            dialog.get_by_role("button", name="Cancel").click()
            confirm_delete(page, 1)

            open_events(page, search=prefix)
            assert card_titles(page) == [titles[0]], card_titles(page)
        finally:
            delete_events(page, prefix)

        browser.close()
