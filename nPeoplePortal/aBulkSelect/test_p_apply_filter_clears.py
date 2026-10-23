from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, checked_rows, select_all, dock,
    main_content, settle,
)


def test_apply_filter_clears():
    """PB-016: applying the filters reloads the list and clears the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_all(page, 2)

            main_content(page).get_by_role("button", name="Apply").click()
            settle(page)
            expect(dock(page)).to_be_hidden()
            expect(checked_rows(page)).to_have_count(0)
        finally:
            delete_queries(page, prefix)

        browser.close()
