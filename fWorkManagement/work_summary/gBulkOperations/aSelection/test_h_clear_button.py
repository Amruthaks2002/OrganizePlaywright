from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, row_checkbox, tick,
                                            expect_dock, dock, dock_clear, header_checkbox, watch_bulk, statuses,
                                            cleanup_prefixed)


def test_clear_button():
    """WS-058: the dock's Clear unticks everything and hides the dock, without touching the entries."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            descs = [log["description"] for log in logs]
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            sent = watch_bulk(page)
            tick(page, *descs)
            expect_dock(page, 2)

            dock_clear(page).click()
            expect(dock(page)).to_have_count(0)
            expect(header_checkbox(page)).not_to_be_checked()
            for desc in descs:
                expect(entry_row(page, desc)).to_have_count(1)
                expect(row_checkbox(entry_row(page, desc))).not_to_be_checked()
            assert sent == []
            assert statuses(page, prefix) == {desc: "pending" for desc in descs}
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
