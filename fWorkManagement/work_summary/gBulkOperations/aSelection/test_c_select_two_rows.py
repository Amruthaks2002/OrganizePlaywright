from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, expect_dock,
                                            cleanup_prefixed)


def test_select_two_rows():
    """WS-053: with two rows ticked the dock reads '2 time logs selected' (plural) and its toolbar is labelled
    'Actions for 2 selected time logs'."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            tick(page, *[log["description"] for log in logs])
            expect_dock(page, 2, approve=2, reject=2, delete=2)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
