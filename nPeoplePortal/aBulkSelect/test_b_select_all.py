import re

from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_rows, checked_rows,
    select_all_box, dock, dock_delete, expect_selected,
)


def test_select_all():
    """PB-002: the header checkbox ticks every query on the page; the dock reads "3 queries selected"
    with Delete (3)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_queries(p, prefix, 3)
            open_portal(page, search=prefix)
            expect(query_rows(page)).to_have_count(3)

            select_all_box(page).check()
            expect(checked_rows(page)).to_have_count(3)
            expect_selected(page, 3)
            expect(dock(page)).to_contain_text(re.compile(r"^\s*3\s*queries selected"))
            expect(dock_delete(page, 3)).to_be_enabled()
        finally:
            delete_queries(page, prefix)

        browser.close()
