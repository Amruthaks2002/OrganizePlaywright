from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_rows, checked_rows,
    select_all, open_delete, expect_selected,
)


def test_delete_dialog_and_cancel():
    """PB-013: Delete asks "Delete 2 queries? This action cannot be undone."; Cancel deletes nothing
    and keeps the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_all(page, 2)

            dialog = open_delete(page, 2)
            expect(dialog).to_contain_text("Delete Queries")
            expect(dialog).to_contain_text("Delete 2 queries? This action cannot be undone.")
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()
            expect(checked_rows(page)).to_have_count(2)
            expect_selected(page, 2)

            open_portal(page, search=prefix)
            expect(query_rows(page)).to_have_count(2)
        finally:
            delete_queries(page, prefix)

        browser.close()
