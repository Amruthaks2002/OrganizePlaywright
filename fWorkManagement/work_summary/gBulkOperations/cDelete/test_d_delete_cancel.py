from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, row_checkbox, tick,
                                            open_bulk, cancel_bulk, expect_dock, watch_bulk, find_prefixed, cleanup_prefixed)


def test_delete_cancel():
    """WS-070: cancelling the Delete dialog sends nothing, keeps the logs and keeps them ticked."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2, comp=False)
            descs = [log["description"] for log in logs]
            show_entries(page, "Regular Hours", earliest(logs), employee=ADMIN_NAME)
            sent = watch_bulk(page)
            tick(page, *descs)

            open_bulk(page, "Delete")
            cancel_bulk(page)
            page.wait_for_timeout(500)
            assert sent == []
            expect_dock(page, 2, delete=2)
            for desc in descs:
                expect(row_checkbox(entry_row(page, desc))).to_be_checked()
            assert len(find_prefixed(page, prefix)) == 2
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
