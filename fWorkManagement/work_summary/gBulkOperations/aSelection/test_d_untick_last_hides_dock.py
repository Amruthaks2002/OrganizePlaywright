from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, untick, expect_dock,
                                            dock, cleanup_prefixed)


def test_untick_last_hides_dock():
    """WS-054: unticking rows counts the dock down, and unticking the last one hides it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            first, second = [log["description"] for log in logs]
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            tick(page, first, second)
            expect_dock(page, 2)

            untick(page, first)
            expect_dock(page, 1, approve=1, reject=1, delete=1)
            untick(page, second)
            expect(dock(page)).to_have_count(0)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
