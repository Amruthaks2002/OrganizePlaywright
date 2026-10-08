from playwright.sync_api import sync_playwright
from utils.people_portal_helper import (
    open_browser, unique_prefix, create_queries, delete_queries, open_portal, query_rows, row_id, bulk_post,
    BULK_ASSIGN, BULK_DELETE, FASNA_ID,
)

# far beyond any real query id
MISSING_ID = 99999999


def test_endpoint_validation():
    """PB-019: the bulk endpoints refuse an empty selection, no assignees, and a query that doesn't exist."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_queries(p, prefix, 1)
            open_portal(page, search=prefix)
            query_id = row_id(query_rows(page).first)

            cases = [
                (BULK_ASSIGN, {"query_ids": [], "user_ids": [str(FASNA_ID)]}, "query_ids", "The query ids field is required."),
                (BULK_ASSIGN, {"query_ids": [query_id], "user_ids": []}, "user_ids", "The user ids field is required."),
                (BULK_ASSIGN, {"query_ids": [MISSING_ID], "user_ids": [str(FASNA_ID)]}, "query_ids.0",
                 "The selected query_ids.0 is invalid."),
                (BULK_DELETE, {"query_ids": []}, "query_ids", "Please select at least one query."),
                (BULK_DELETE, {"query_ids": [MISSING_ID]}, "query_ids.0", "One of the selected queries no longer exists."),
            ]
            for path, data, field, message in cases:
                status, body = bulk_post(page, path, data)
                assert status == 422, f"{path} {data}: expected 422, got {status} {body}"
                assert body["errors"][field] == [message], body
        finally:
            delete_queries(page, prefix)

        browser.close()
