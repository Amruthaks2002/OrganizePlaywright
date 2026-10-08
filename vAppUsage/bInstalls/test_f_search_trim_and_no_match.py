from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, open_app_usage, main_content, install_rows, installs_count,
                                    search_installs, query_params, INSTALLS_EMPTY)


def test_search_trim_and_no_match():
    """AI-006: spaces around a search term are ignored; a search with no match shows the empty message."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        term = install_rows(page)[0]["name"].split()[0].lower()

        search_installs(page, term)
        expected = install_rows(page)
        search_installs(page, f"   {term}   ")
        assert query_params(page).get("search") == term, page.url
        assert install_rows(page) == expected

        search_installs(page, "zzqx-no-such-install")
        expect(main_content(page).get_by_text(INSTALLS_EMPTY)).to_be_visible()
        assert install_rows(page) == []
        assert installs_count(page) == 0

        browser.close()
