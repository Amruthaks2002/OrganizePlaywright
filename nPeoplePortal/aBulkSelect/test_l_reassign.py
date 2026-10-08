from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_row, row_assignee,
    select_all, bulk_assign, ASSIGNEE, SECOND_ASSIGNEE,
)


def test_reassign():
    """PB-012: bulk assigning queries that already have an assignee moves them to the new one."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_all(page, 2)
            bulk_assign(page, ASSIGNEE)

            open_portal(page, search=prefix)
            select_all(page, 2)
            bulk_assign(page, SECOND_ASSIGNEE)

            open_portal(page, search=prefix)
            for subject in subjects:
                expect(row_assignee(query_row(page, subject))).to_have_text(SECOND_ASSIGNEE)
        finally:
            delete_queries(page, prefix)

        browser.close()
