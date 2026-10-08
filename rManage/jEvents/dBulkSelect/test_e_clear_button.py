from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, card_boxes, checked_cards,
    select_all_box, dock, dock_clear, expect_selected,
)


def test_clear_button():
    """EB-005: Clear unticks every card and Select All, hides the dock and deletes nothing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_events(page, prefix)
            open_events(page, search=prefix)
            select_all_box(page).check()
            expect_selected(page, 2)

            dock_clear(page).click()
            expect(checked_cards(page)).to_have_count(0)
            expect(select_all_box(page)).not_to_be_checked()
            expect(dock(page)).to_be_hidden()
            expect(card_boxes(page)).to_have_count(2)
        finally:
            delete_events(page, prefix)

        browser.close()
