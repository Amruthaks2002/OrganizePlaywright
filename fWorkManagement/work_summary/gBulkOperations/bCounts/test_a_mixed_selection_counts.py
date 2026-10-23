from datetime import timedelta
from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, today, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, row_checkbox, approved_row,
                                            bulk_api, expect_dock, cleanup_prefixed)


def test_mixed_selection_counts():
    """WS-064: with 2 pending, 1 rejected and 1 approved entry ticked, the dock counts 4 selected but only offers
    Approve (2) / Reject (2) / Delete (2) - decided entries are left out of every action. The approved entry
    was approved earlier; it's only ticked."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 3)
            assert bulk_api(page, "reject", [logs[2]["id"]], json_errors=False)[0] == 302
            show_entries(page, "Comp Hours", min(earliest(logs), today() - timedelta(days=30)), employee=ADMIN_NAME)

            tick(page, *[log["description"] for log in logs])
            row_checkbox(approved_row(page)).check()
            expect_dock(page, 4, approve=2, reject=2, delete=2)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
