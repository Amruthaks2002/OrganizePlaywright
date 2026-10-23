from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_row, row_assignee,
    select_all, open_assign, assignee_chip, ASSIGNEE,
)


def test_cancel_assign():
    """PB-009: Cancel (and the ✕) close the Assign dialog without assigning anything."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_all(page, 2)

            dialog = open_assign(page)
            assignee_chip(dialog, ASSIGNEE).click()
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()

            dialog = open_assign(page)
            dialog.get_by_role("button", name="✕").click()
            expect(dialog).to_be_hidden()

            open_portal(page, search=prefix)
            for subject in subjects:
                expect(row_assignee(query_row(page, subject))).to_have_text("Unassigned")
        finally:
            delete_queries(page, prefix)

        browser.close()
