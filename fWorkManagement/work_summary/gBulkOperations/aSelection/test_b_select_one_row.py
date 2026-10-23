import re
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, row_checkbox, tick,
                                            expect_dock, cleanup_prefixed)


def test_select_one_row():
    """WS-052: ticking one pending comp entry highlights its row and brings up the dock with '1 time log
    selected' and Approve (1) / Reject (1) / Delete (1)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            show_entries(page, "Comp Hours", earliest([log]), employee=ADMIN_NAME)
            r = entry_row(page, log["description"])
            expect(r).not_to_have_class(re.compile(r"bg-indigo-50"))

            tick(page, log["description"])
            expect(row_checkbox(r)).to_be_checked()
            expect(r).to_have_class(re.compile(r"bg-indigo-50"))
            expect_dock(page, 1, approve=1, reject=1, delete=1)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
