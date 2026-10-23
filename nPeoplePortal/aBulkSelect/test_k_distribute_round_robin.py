from collections import Counter

from playwright.sync_api import sync_playwright
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_row, row_assignee,
    select_all, bulk_assign, ASSIGNEE, SECOND_ASSIGNEE,
)


def test_distribute_round_robin():
    """PB-011: three queries distributed among two assignees are shared out 2 + 1 - nobody gets them
    all and nobody is left out."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix, 3)
            open_portal(page, search=prefix)
            select_all(page, 3)

            bulk_assign(page, ASSIGNEE, SECOND_ASSIGNEE)

            open_portal(page, search=prefix)
            counts = Counter(row_assignee(query_row(page, s)).inner_text().strip() for s in subjects)
            assert sorted(counts.values()) == [1, 2] and set(counts) == {ASSIGNEE, SECOND_ASSIGNEE}, counts
        finally:
            delete_queries(page, prefix)

        browser.close()
