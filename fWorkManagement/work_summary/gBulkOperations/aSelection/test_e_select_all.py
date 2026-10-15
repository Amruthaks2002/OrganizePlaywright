from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, data_rows, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, header_checkbox, row_checkbox,
                                            expect_dock, dock, cleanup_prefixed)


def test_select_all():
    """WS-055: the header checkbox ticks every row on the page (the dock counts them all) and clicking it
    again unticks them all and hides the dock. Only ticks rows - nothing is acted on."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            trs = data_rows(page)

            header_checkbox(page).check()
            expect_dock(page, len(trs))
            for tr in trs:
                expect(row_checkbox(tr)).to_be_checked()

            header_checkbox(page).uncheck()
            expect(dock(page)).to_have_count(0)
            for tr in trs:
                expect(row_checkbox(tr)).not_to_be_checked()
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
