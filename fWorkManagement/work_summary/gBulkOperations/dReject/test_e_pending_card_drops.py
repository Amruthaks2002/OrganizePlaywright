from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, expect_toast, summary_card, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, run_bulk, pending_hours,
                                            rejected_msg, cleanup_prefixed)


def test_pending_card_drops():
    """WS-078: rejecting two 1-hour entries together takes 2 hours off the employee's Pending Comp Hours card."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2, hours=1)
            data = show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            before = pending_hours(page)
            assert before == data["totalPendingCompensatoryHours"], data

            tick(page, *[log["description"] for log in logs])
            run_bulk(page, "Reject")
            expect_toast(page, rejected_msg(2))
            expect(summary_card(page, "Pending Comp Hours")).to_be_visible()
            page.wait_for_timeout(500)
            assert pending_hours(page) == before - 2
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
