from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_tab, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, row_checkbox, tick,
                                            expect_dock, dock, cleanup_prefixed)


def test_tab_change_clears():
    """WS-060: switching between Comp Hours and Regular Hours drops the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [comp] = create_logs(page, prefix, 1)
            [regular] = create_logs(page, prefix, 1, comp=False, start_index=2)
            start = min(earliest([comp]), earliest([regular]))
            show_entries(page, "Comp Hours", start, employee=ADMIN_NAME)
            tick(page, comp["description"])
            expect_dock(page, 1)

            open_tab(page, "Regular Hours")
            expect(dock(page)).to_have_count(0)
            tick(page, regular["description"])
            expect_dock(page, 1)

            open_tab(page, "Comp Hours")
            expect(dock(page)).to_have_count(0)
            expect(row_checkbox(entry_row(page, comp["description"]))).not_to_be_checked()
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
