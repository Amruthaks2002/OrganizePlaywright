import re

from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, select_all, open_assign,
    assignee_search, selected_count,
)


def test_assignee_search():
    """PB-007: the assignee search lists only matching eligible assignees (ticking one picks it), and
    an unmatched search says "No eligible assignees found."."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_queries(p, prefix)
            open_portal(page, search=prefix)
            select_all(page, 2)
            dialog = open_assign(page)
            _, eligible = selected_count(dialog)

            assignee_search(dialog).fill("Fas")
            results = dialog.locator("label:visible").filter(has=page.locator("input[type=checkbox]"))
            expect(results).to_have_count(2)
            assert sorted(t.strip() for t in results.all_inner_texts()) == ["Fasil KK", "Fasna KK"]

            results.filter(has_text="Fasna KK").click()
            assert selected_count(dialog) == (1, eligible), selected_count(dialog)

            assignee_search(dialog).fill("zzz-nobody")
            expect(dialog.get_by_text("No eligible assignees found.")).to_be_visible()
            expect(results).to_have_count(0)
        finally:
            delete_queries(page, prefix)

        browser.close()
