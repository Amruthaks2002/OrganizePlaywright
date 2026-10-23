from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, create_event, delete_events, open_events, select_all_box, checked_cards,
    card_titles, dock, expect_selected, settle,
)


def test_filter_change_clears():
    """EB-010: changing the Status filter clears the selection - even for a selected event that is
    still shown afterwards - so a delete can't hit events that were filtered out."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        active, inactive = f"{prefix} active", f"{prefix} inactive"
        try:
            create_event(page, active, days_ahead=1)
            create_event(page, inactive, days_ahead=2, active=False)
            open_events(page, search=prefix)
            select_all_box(page).check()
            expect_selected(page, 2)

            page.locator("#status").select_option("inactive")
            page.wait_for_url("**status=inactive**")
            settle(page)
            assert card_titles(page) == [inactive], card_titles(page)
            expect(dock(page)).to_be_hidden()
            expect(checked_cards(page)).to_have_count(0)
        finally:
            delete_events(page, prefix)

        browser.close()
