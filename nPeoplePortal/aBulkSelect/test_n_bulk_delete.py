from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_rows, query_row,
    select_rows, confirm_delete, dock,
)


def test_bulk_delete():
    """PB-014: deleting two of three selected queries shows "2 queries deleted.", removes exactly
    those two and hides the dock."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix, 3)
            open_portal(page, search=prefix)
            select_rows(page, subjects[0], subjects[1])

            confirm_delete(page, 2)
            expect(dock(page)).to_be_hidden()

            open_portal(page, search=prefix)
            expect(query_rows(page)).to_have_count(1)
            expect(query_row(page, subjects[2])).to_have_count(1)
        finally:
            delete_queries(page, prefix)

        browser.close()
