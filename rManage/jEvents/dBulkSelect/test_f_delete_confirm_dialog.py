from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, select_cards, open_bulk_delete,
)


def test_delete_confirm_dialog():
    """EB-006: Delete asks for confirmation, naming how many events and that it can't be undone."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix)
            open_events(page, search=prefix)
            select_cards(page, *titles)

            dialog = open_bulk_delete(page)
            expect(dialog).to_contain_text("Bulk Delete Events")
            expect(dialog).to_contain_text("Are you sure you want to delete 2 selected event(s)? "
                                           "This action cannot be undone.")
            expect(dialog.get_by_role("button", name="Cancel")).to_be_visible()
            expect(dialog.get_by_role("button", name="Delete", exact=True)).to_be_visible()
        finally:
            delete_events(page, prefix)

        browser.close()
