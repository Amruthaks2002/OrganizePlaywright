from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, expect_toast, BADGES, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk,
                                            bulk_api, statuses, rejected_msg, NONE_REJECTED, cleanup_prefixed)


def test_stale_selection():
    """WS-089: admin A ticks a pending entry, admin B rejects it in another session, then A clicks Reject: the
    server says nothing could be rejected, A's table refreshes to show it Rejected, and nothing breaks."""
    with sync_playwright() as p:
        browser_a, a = open_browser(p)
        browser_b, b = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(a, prefix, 1)
            show_entries(a, "Comp Hours", earliest([log]), employee=ADMIN_NAME)
            tick(a, log["description"])

            assert bulk_api(b, "reject", [log["id"]], json_errors=False) == (302, {"success": rejected_msg(1)})

            assert run_bulk(a, "Reject") == [log["id"]]
            expect_toast(a, NONE_REJECTED)
            expect(entry_row(a, log["description"]).locator("span.rounded-full").last).to_have_text(BADGES["rejected"])
            assert statuses(a, prefix) == {log["description"]: "rejected"}
        finally:
            cleanup_prefixed(a, prefix)
            browser_b.close()
            browser_a.close()
