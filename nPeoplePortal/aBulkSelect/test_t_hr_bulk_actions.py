from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, open_browser_as, unique_prefix, create_queries, delete_queries, open_portal, query_rows,
    query_row, row_assignee, select_all, bulk_assign, confirm_delete, ASSIGNEE,
)


def test_hr_bulk_actions():
    """PB-020: HR can bulk assign and bulk delete queries."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)

            hr_browser, hr_page = open_browser_as(p, "hr")
            open_portal(hr_page, search=prefix)
            select_all(hr_page, 2)
            bulk_assign(hr_page, ASSIGNEE)
            open_portal(hr_page, search=prefix)
            for subject in subjects:
                expect(row_assignee(query_row(hr_page, subject))).to_have_text(ASSIGNEE)

            select_all(hr_page, 2)
            confirm_delete(hr_page, 2)
            open_portal(hr_page, search=prefix)
            expect(query_rows(hr_page)).to_have_count(0)
            hr_browser.close()
        finally:
            delete_queries(page, prefix)

        browser.close()
