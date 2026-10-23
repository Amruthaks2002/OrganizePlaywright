from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, data_rows, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, header_checkbox, row_checkbox,
                                            cleanup_prefixed)


def test_header_follows_rows():
    """WS-056: ticking every row one by one ticks the header checkbox too; unticking any one row unticks it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            trs = data_rows(page)
            for i, tr in enumerate(trs):
                expect(header_checkbox(page)).not_to_be_checked()
                row_checkbox(tr).check()
            expect(header_checkbox(page)).to_be_checked()

            row_checkbox(trs[-1]).uncheck()
            expect(header_checkbox(page)).not_to_be_checked()
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
