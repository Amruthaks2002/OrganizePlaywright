from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, expect_toast, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, open_bulk,
                                            confirm_bulk, expect_confirm, expect_dock, dock, find_prefixed, deleted_msg,
                                            cleanup_prefixed)


def test_delete_regular_logs():
    """WS-067: an admin ticks two of their regular logs and deletes them together: 'Delete Work Logs' /
    'Delete 2 time logs? This cannot be undone.', then both are gone from the table and the server."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2, comp=False)
            descs = [log["description"] for log in logs]
            show_entries(page, "Regular Hours", earliest(logs), employee=ADMIN_NAME)
            tick(page, *descs)
            expect_dock(page, 2, delete=2)

            open_bulk(page, "Delete")
            expect_confirm(page, "Delete Work Logs", "Delete 2 time logs? This cannot be undone.", "Delete", danger=True)
            sent = confirm_bulk(page, "Delete")
            assert sorted(sent) == sorted(log["id"] for log in logs), sent

            expect_toast(page, deleted_msg(2))
            expect(dock(page)).to_have_count(0)
            for desc in descs:
                expect(entry_row(page, desc)).to_have_count(0)
            assert find_prefixed(page, prefix) == []
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
