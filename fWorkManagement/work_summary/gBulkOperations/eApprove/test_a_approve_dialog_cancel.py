from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, open_bulk, cancel_bulk,
                                            expect_confirm, expect_dock, watch_bulk, statuses, cleanup_prefixed)


def test_approve_dialog_cancel():
    """WS-079: Approve with two entries ticked asks 'Approve 2 compensatory requests?' (indigo Approve button);
    cancelling sends nothing and both stay pending. Never confirmed: an approval can't be undone."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            descs = [log["description"] for log in logs]
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            sent = watch_bulk(page)
            tick(page, *descs)

            open_bulk(page, "Approve")
            expect_confirm(page, "Approve Compensatory Hours", "Approve 2 compensatory requests?", "Approve", danger=False)
            cancel_bulk(page)
            page.wait_for_timeout(500)
            assert sent == []
            expect_dock(page, 2, approve=2, reject=2, delete=2)
            assert statuses(page, prefix) == {desc: "pending" for desc in descs}
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
