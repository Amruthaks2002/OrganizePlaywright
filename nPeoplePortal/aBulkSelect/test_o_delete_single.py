from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_rows, query_row,
    select_rows, open_delete, confirm_delete,
)


def test_delete_single():
    """PB-015: deleting one query asks "Delete 1 query?" and shows "1 query deleted."."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_rows(page, subjects[0])

            dialog = open_delete(page, 1)
            expect(dialog).to_contain_text("Delete 1 query? This action cannot be undone.")
            dialog.get_by_role("button", name="Cancel").click()
            confirm_delete(page, 1)

            open_portal(page, search=prefix)
            expect(query_rows(page)).to_have_count(1)
            expect(query_row(page, subjects[1])).to_have_count(1)
        finally:
            delete_queries(page, prefix)

        browser.close()
