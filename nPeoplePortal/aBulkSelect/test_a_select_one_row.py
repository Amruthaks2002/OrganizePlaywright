import re

from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_row, row_box, dock,
    dock_assign, dock_delete, dock_clear,
)


def test_select_one_row():
    """PB-001: ticking one query shows the dock with "1 query selected", Assign, Delete (1) and Clear.

    Known bug: the dock reads "1 querie selected" (the plural with the s chopped off). This test
    fails until the label is fixed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)
            open_portal(page, search=prefix)
            expect(dock(page)).to_be_hidden()

            row_box(query_row(page, subjects[0])).check()
            expect(dock_assign(page)).to_be_enabled()
            expect(dock_delete(page, 1)).to_be_enabled()
            expect(dock_clear(page)).to_be_visible()
            expect(dock(page)).to_contain_text(re.compile(r"^\s*1\s*query selected"))
        finally:
            delete_queries(page, prefix)

        browser.close()
