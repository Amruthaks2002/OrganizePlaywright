from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_rows, query_row, row_box,
    checked_rows, select_all, select_all_box, dock, dock_clear,
)


def test_clear_and_deselect():
    """PB-004: Clear unticks everything and hides the dock; unticking the last row hides it too."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)
            open_portal(page, search=prefix)

            select_all(page, 2)
            dock_clear(page).click()
            expect(checked_rows(page)).to_have_count(0)
            expect(select_all_box(page)).not_to_be_checked()
            expect(dock(page)).to_be_hidden()
            expect(query_rows(page)).to_have_count(2)

            row_box(query_row(page, subjects[0])).check()
            row_box(query_row(page, subjects[0])).uncheck()
            expect(dock(page)).to_be_hidden()
        finally:
            delete_queries(page, prefix)

        browser.close()
