from datetime import timedelta
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, wait_for_logs, data_rows, pager_button, today, PER_PAGE
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, header_checkbox, row_checkbox,
                                            expect_dock, dock, cleanup_prefixed)


def test_page_change_clears():
    """WS-062: a selection only lives on its page - going to page 2 drops it, 'select all' there only ticks
    page 2's rows, and coming back to page 1 finds nothing ticked. Logs extra entries if there aren't enough
    for two pages."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        start = today() - timedelta(days=60)
        try:
            data = show_entries(page, "Comp Hours", start)
            missing = PER_PAGE + 1 - data["timeLogs"]["total"]
            if missing > 0:
                create_logs(page, prefix, missing)
                data = show_entries(page, "Comp Hours", start)
            total = data["timeLogs"]["total"]

            row_checkbox(data_rows(page)[0]).check()
            expect_dock(page, 1)
            page2 = wait_for_logs(page, lambda: pager_button(page, "Next »").click())
            assert page2["timeLogs"]["current_page"] == 2
            expect(dock(page)).to_have_count(0)

            header_checkbox(page).check()
            expect_dock(page, min(total - PER_PAGE, PER_PAGE))

            wait_for_logs(page, lambda: pager_button(page, "1").click())
            expect(dock(page)).to_have_count(0)
            expect(header_checkbox(page)).not_to_be_checked()
            for tr in data_rows(page):
                expect(row_checkbox(tr)).not_to_be_checked()
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
