from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, open_bulk, cancel_bulk,
                                            expect_confirm, watch_bulk, statuses, cleanup_prefixed)


def test_approve_one_singular_cancel():
    """WS-080: with one entry ticked the dialog asks 'Approve 1 compensatory request?'. Cancelled only."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            show_entries(page, "Comp Hours", earliest([log]), employee=ADMIN_NAME)
            sent = watch_bulk(page)
            tick(page, log["description"])

            open_bulk(page, "Approve")
            expect_confirm(page, "Approve Compensatory Hours", "Approve 1 compensatory request?", "Approve", danger=False)
            cancel_bulk(page)
            page.wait_for_timeout(500)
            assert sent == []
            assert statuses(page, prefix) == {log["description"]: "pending"}
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
