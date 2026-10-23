from datetime import timedelta
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, expect_toast, row_cells, data_rows, today, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, row_checkbox,
                                            approved_row, run_bulk, expect_dock, find_prefixed, deleted_msg, cleanup_prefixed)


def test_delete_skips_approved():
    """WS-071: with a pending and an approved entry ticked, Delete (1) only sends the pending one; the approved
    entry stays. (The approved entry was approved earlier and is never sent.)"""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            show_entries(page, "Comp Hours", min(earliest([log]), today() - timedelta(days=30)), employee=ADMIN_NAME)
            approved = approved_row(page)
            approved_cells = row_cells(approved)
            tick(page, log["description"])
            row_checkbox(approved).check()
            expect_dock(page, 2, delete=1)

            assert run_bulk(page, "Delete") == [log["id"]]
            expect_toast(page, deleted_msg(1))
            expect(entry_row(page, log["description"])).to_have_count(0)
            assert find_prefixed(page, prefix) == []
            assert approved_cells in [row_cells(tr) for tr in data_rows(page)], approved_cells
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
