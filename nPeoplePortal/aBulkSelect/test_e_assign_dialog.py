from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, select_all, open_assign,
    assignee_chips, selected_count, distribute_button, assignee_search,
)


def test_assign_dialog():
    """PB-005: Assign opens "Bulk Assign Queries" naming how many queries are selected, lists the
    eligible assignees with none picked, and keeps Distribute Queries disabled until one is."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_all(page, 2)

            dialog = open_assign(page)
            expect(dialog).to_contain_text("You have selected 2 queries. Select the assignees you wish to "
                                           "distribute these queries among:")
            picked, eligible = selected_count(dialog)
            assert picked == 0 and eligible > 1, (picked, eligible)
            expect(assignee_chips(dialog)).to_have_count(eligible)
            expect(assignee_search(dialog)).to_be_visible()
            expect(distribute_button(dialog)).to_be_disabled()
        finally:
            delete_queries(page, prefix)

        browser.close()
