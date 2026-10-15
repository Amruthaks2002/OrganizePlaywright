from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, untick, bulk_api,
                                            expect_dock, cleanup_prefixed)


def test_counts_follow_selection():
    """WS-066: the action counts update live as rows are ticked and unticked."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 3)
            pending1, pending2, rejected = [log["description"] for log in logs]
            assert bulk_api(page, "reject", [logs[2]["id"]], json_errors=False)[0] == 302
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)

            tick(page, pending1)
            expect_dock(page, 1, approve=1, reject=1, delete=1)
            tick(page, rejected)
            expect_dock(page, 2, approve=1, reject=1, delete=1)
            tick(page, pending2)
            expect_dock(page, 3, approve=2, reject=2, delete=2)
            untick(page, pending1)
            expect_dock(page, 2, approve=1, reject=1, delete=1)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
