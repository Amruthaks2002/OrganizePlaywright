from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, expect_toast, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, open_bulk, dock_button,
                                            confirm_dialog, watch_bulk, statuses, rejected_msg, BULK_URL, cleanup_prefixed)


def test_no_double_submit():
    """WS-090: while a bulk Reject is in flight every dock action is disabled, so the request goes out once.
    The request is held back until the buttons have been checked."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            show_entries(page, "Comp Hours", earliest(logs), employee=ADMIN_NAME)
            tick(page, *[log["description"] for log in logs])
            sent = watch_bulk(page)
            held = []
            page.route(f"{BULK_URL}reject", lambda route: held.append(route))

            open_bulk(page, "Reject")
            confirm_dialog(page).get_by_test_id("confirm-dialog-confirm").click()
            expect(page.get_by_test_id("confirm-dialog")).to_have_count(0)
            for action in ("Approve", "Reject", "Delete"):
                expect(dock_button(page, action)).to_be_disabled()
            page.wait_for_timeout(500)
            assert len(sent) == 1 and len(held) == 1, sent

            held[0].continue_()
            page.unroute(f"{BULK_URL}reject")
            expect_toast(page, rejected_msg(2))
            assert len(sent) == 1, sent
            assert set(statuses(page, prefix).values()) == {"rejected"}
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
