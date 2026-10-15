from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, expect_toast, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, open_bulk, confirm_bulk,
                                            expect_confirm, statuses, rejected_msg, cleanup_prefixed)


def test_reject_one_singular():
    """WS-075: with one entry ticked the Reject dialog asks 'Reject 1 compensatory request?' with a red Reject
    button, and the toast reads '1 comp-off request rejected.'"""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            show_entries(page, "Comp Hours", earliest([log]), employee=ADMIN_NAME)
            tick(page, log["description"])

            open_bulk(page, "Reject")
            expect_confirm(page, "Reject Compensatory Hours", "Reject 1 compensatory request?", "Reject", danger=True)
            assert confirm_bulk(page, "Reject") == [log["id"]]
            expect_toast(page, rejected_msg(1))
            assert statuses(page, prefix) == {log["description"]: "rejected"}
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
