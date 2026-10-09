import re
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_marketplace, search_box, card_names,
    result_count, main_content, NO_MATCH,
)


def test_search():
    """MP-002: typing in the search box narrows the list to the matching app (search is in the
    URL), and a search with no match shows 0 results and the empty state."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_live_app(page, name)
            open_marketplace(page)

            search_box(page).fill(name)
            page.wait_for_url(re.compile(rf"search={re.escape(quote(name))}"))
            expect(result_count(page)).to_have_text("1 result")
            assert card_names(page) == [name], card_names(page)

            search_box(page).fill(f"{name} no-such-app")
            expect(result_count(page)).to_have_text("0 results")
            expect(main_content(page).get_by_text(NO_MATCH)).to_be_visible()
            assert card_names(page) == [], card_names(page)
        finally:
            delete_apps(page, name)

        browser.close()
