from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_row, row_assignee,
    row_status, select_all, bulk_assign, dock, ASSIGNEE,
)


def test_assign_one_assignee():
    """PB-010: distributing the selected queries to one assignee gives them all, keeps their status
    and clears the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_all(page, 2)

            bulk_assign(page, ASSIGNEE)
            expect(dock(page)).to_be_hidden()

            open_portal(page, search=prefix)
            for subject in subjects:
                row = query_row(page, subject)
                expect(row_assignee(row)).to_have_text(ASSIGNEE)
                expect(row_status(row)).to_have_text("Open")
        finally:
            delete_queries(page, prefix)

        browser.close()
