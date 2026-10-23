from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, expect_toast, approve_button, reject_button, BADGES, ADMIN_NAME, ADMIN_ID
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, open_bulk, confirm_bulk,
                                            expect_dock, expect_confirm, dock, statuses, find_prefixed, cleanup_prefixed,
                                            rejected_msg)


def test_bulk_reject():
    """WS-074: an admin ticks two pending comp entries and rejects them together: the dialog asks 'Reject 2
    compensatory requests?', both rows turn Rejected without their Approve/Reject icons, the server records who
    rejected them, and the dock goes away."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            descs = [log["description"] for log in logs]
            tick(page, *descs)
            expect_dock(page, 2, approve=2, reject=2, delete=2)

            open_bulk(page, "Reject")
            expect_confirm(page, "Reject Compensatory Hours", "Reject 2 compensatory requests?", "Reject")
            sent = confirm_bulk(page, "Reject")
            assert sorted(sent) == sorted(log["id"] for log in logs), sent

            expect_toast(page, rejected_msg(2))
            expect(dock(page)).to_have_count(0)
            for desc in descs:
                r = entry_row(page, desc)
                expect(r.locator("span.rounded-full").last).to_have_text(BADGES["rejected"])
                expect(approve_button(r)).to_have_count(0)
                expect(reject_button(r)).to_have_count(0)
            assert statuses(page, prefix) == {desc: "rejected" for desc in descs}
            for log in find_prefixed(page, prefix):  # the decider is kept in approved_by, rejected or not
                assert log["approved_by"]["id"] == ADMIN_ID and log["approved_at"], log["approved_by"]
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
