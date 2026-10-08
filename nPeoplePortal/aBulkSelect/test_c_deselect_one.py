from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_row, row_box, checked_rows,
    select_all, select_all_box, dock_delete, expect_selected,
)


def test_deselect_one():
    """PB-003: unticking one row after Select All lowers the count (and Delete's) and unticks the header."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix, 3)
            open_portal(page, search=prefix)
            select_all(page, 3)

            row_box(query_row(page, subjects[0])).uncheck()
            expect(checked_rows(page)).to_have_count(2)
            expect(select_all_box(page)).not_to_be_checked()
            expect_selected(page, 2)
            expect(dock_delete(page, 2)).to_be_visible()
        finally:
            delete_queries(page, prefix)

        browser.close()
