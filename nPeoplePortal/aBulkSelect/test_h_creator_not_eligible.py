from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_row, row_assignee,
    select_all, open_assign, assignee_chip, bulk_post, row_id, CREATOR, CREATOR_ID, BULK_ASSIGN,
)


def test_creator_not_eligible():
    """PB-008: the employee who raised the queries isn't offered as their assignee, and assigning
    them through the endpoint anyway leaves the queries unassigned."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)
            open_portal(page, search=prefix)
            ids = [row_id(query_row(page, s)) for s in subjects]
            select_all(page, 2)

            dialog = open_assign(page)
            expect(assignee_chip(dialog, CREATOR)).to_have_count(0)
            dialog.get_by_role("button", name="Cancel").click()

            bulk_post(page, BULK_ASSIGN, {"query_ids": ids, "user_ids": [str(CREATOR_ID)]})
            open_portal(page, search=prefix)
            for subject in subjects:
                expect(row_assignee(query_row(page, subject))).to_have_text("Unassigned")
        finally:
            delete_queries(page, prefix)

        browser.close()
