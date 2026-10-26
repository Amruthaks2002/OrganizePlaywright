from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, expect_toast, edit_button, comp_balance, expected_after_approval,
                                       BADGES)
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk, me,
                                            expect_dock, approved_msg, comp_user_or_skip, open_comp_user, cleanup_prefixed)


def test_admin_approve_seen_by_employee():
    """WS-106: when an admin bulk-approves two of an employee's 2-hour entries, the employee sees them Approved
    and locked (no Edit; ticking them gives Delete (0)), and their comp-off balance grows by 4 hours' worth.

    Approving can't be undone, so the employee is the throwaway comp user (WS_COMP_USER_EMAIL /
    WS_COMP_USER_PASSWORD); skips when unset."""
    credentials = comp_user_or_skip()  # before Playwright starts
    with sync_playwright() as p:
        browser, page = open_comp_user(p, credentials)
        admin_browser, admin = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2, hours=2)
            descs = [log["description"] for log in logs]
            user = me(page)
            balance, leftover = comp_balance(admin, user["id"])

            show_entries(admin, "Comp Hours", earliest(logs), employee=user["name"])
            tick(admin, *descs)
            run_bulk(admin, "Approve")
            expect_toast(admin, approved_msg(2))

            show_entries(page, "Comp Hours", earliest(logs))
            for desc in descs:
                r = entry_row(page, desc)
                expect(r.locator("span.rounded-full").last).to_have_text(BADGES["approved"])
                expect(edit_button(r)).to_have_count(0)
            tick(page, *descs)
            expect_dock(page, 2, approve=None, reject=None, delete=0)
            assert comp_balance(admin, user["id"]) == expected_after_approval(balance, leftover, 4)
        finally:
            cleanup_prefixed(admin, prefix)
            admin_browser.close()
            browser.close()
