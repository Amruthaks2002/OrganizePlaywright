from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_events, delete_events, open_events, card_box, dock, dock_delete,
    dock_clear, expect_selected,
)


def test_select_one_card():
    """EB-001: ticking one event card shows the dock with "1 event selected", Delete and Clear."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix)
            open_events(page, search=prefix)
            expect(dock(page)).to_be_hidden()

            card_box(page, titles[0]).check()
            expect_selected(page, 1)
            expect(dock_delete(page)).to_be_enabled()
            expect(dock_clear(page)).to_be_visible()
            expect(card_box(page, titles[1])).not_to_be_checked()
        finally:
            delete_events(page, prefix)

        browser.close()
