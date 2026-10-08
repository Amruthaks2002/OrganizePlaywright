from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, unique_prefix, open_events, main_content, dock, EMPTY_LIST,
)


def test_no_events_no_select_all():
    """EB-013: when nothing matches, the empty state shows without a Select All bar or dock."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        open_events(page, search=f"{unique_prefix()} nothing")
        expect(main_content(page).get_by_text(EMPTY_LIST)).to_be_visible()
        expect(main_content(page).get_by_text("Select All", exact=True)).to_have_count(0)
        expect(dock(page)).to_be_hidden()

        browser.close()
