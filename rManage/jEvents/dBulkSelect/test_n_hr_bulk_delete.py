from playwright.sync_api import sync_playwright
from utils.events_helper import (
    open_browser, open_browser_as, unique_prefix, create_events, delete_events, open_events, select_cards,
    confirm_delete, card_titles,
)


def test_hr_bulk_delete():
    """EB-014: HR gets the bulk select UI on Events and can bulk delete."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix)

            hr_browser, hr_page = open_browser_as(p, "hr")
            open_events(hr_page, search=prefix)
            select_cards(hr_page, *titles)
            confirm_delete(hr_page, 2)
            open_events(hr_page, search=prefix)
            assert card_titles(hr_page) == [], card_titles(hr_page)
            hr_browser.close()
        finally:
            delete_events(page, prefix)

        browser.close()
