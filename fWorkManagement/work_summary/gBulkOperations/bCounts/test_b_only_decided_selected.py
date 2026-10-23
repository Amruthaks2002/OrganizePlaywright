from datetime import timedelta
from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, today, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, row_checkbox, approved_row,
                                            bulk_api, expect_dock, cleanup_prefixed)


def test_only_decided_selected():
    """WS-065: with only an approved and a rejected entry ticked, Approve (0), Reject (0) and Delete (0) are
    all disabled."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            assert bulk_api(page, "reject", [log["id"]], json_errors=False)[0] == 302
            show_entries(page, "Comp Hours", min(earliest([log]), today() - timedelta(days=30)), employee=ADMIN_NAME)

            tick(page, log["description"])
            row_checkbox(approved_row(page)).check()
            expect_dock(page, 2, approve=0, reject=0, delete=0)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
