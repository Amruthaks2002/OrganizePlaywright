from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, expect_toast, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, open_bulk,
                                            confirm_bulk, expect_confirm, find_prefixed, deleted_msg, cleanup_prefixed)


def test_delete_one_singular():
    """WS-069: with one log ticked the dialog says 'Delete Work Log' / 'Delete 1 time log? This cannot be
    undone.' and the toast '1 time log deleted.'"""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1, comp=False)
            show_entries(page, "Regular Hours", earliest([log]), employee=ADMIN_NAME)
            tick(page, log["description"])

            open_bulk(page, "Delete")
            expect_confirm(page, "Delete Work Log", "Delete 1 time log? This cannot be undone.", "Delete", danger=True)
            assert confirm_bulk(page, "Delete") == [log["id"]]
            expect_toast(page, deleted_msg(1))
            expect(entry_row(page, log["description"])).to_have_count(0)
            assert find_prefixed(page, prefix) == []
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
