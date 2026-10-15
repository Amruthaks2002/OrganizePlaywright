from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, BADGES, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, open_bulk,
                                            cancel_bulk, expect_dock, watch_bulk, statuses, cleanup_prefixed)


def test_reject_cancel():
    """WS-076: cancelling the Reject dialog sends nothing; the entries stay pending and ticked."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            descs = [log["description"] for log in logs]
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            sent = watch_bulk(page)
            tick(page, *descs)

            open_bulk(page, "Reject")
            cancel_bulk(page)
            page.wait_for_timeout(500)
            assert sent == []
            expect_dock(page, 2, approve=2, reject=2, delete=2)
            for desc in descs:
                expect(entry_row(page, desc).locator("span.rounded-full").last).to_have_text(BADGES["pending"])
            assert statuses(page, prefix) == {desc: "pending" for desc in descs}
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
