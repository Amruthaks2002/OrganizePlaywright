from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, expect_toast, approve_button, reject_button, comp_balance,
                                       expected_after_approval, BADGES)
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, run_bulk,
                                            expect_dock, dock, me, statuses, approved_msg, comp_user_or_skip, open_comp_user,
                                            cleanup_prefixed)


def test_bulk_approve():
    """WS-081: an admin approves two of the throwaway comp user's 2-hour entries together: both turn Approved
    and the 4 hours go into the user's comp-off balance like single approvals do (4h -> +0.5 day).

    Approving can't be undone, so this only runs as the dedicated throwaway user (WS_COMP_USER_EMAIL /
    WS_COMP_USER_PASSWORD) and skips when they're unset."""
    credentials = comp_user_or_skip()  # before Playwright starts
    with sync_playwright() as p:
        user_browser, user = open_comp_user(p, credentials)
        admin_browser, admin = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(user, prefix, 2, hours=2)
            name, user_id = me(user)["name"], me(user)["id"]
            balance, leftover = comp_balance(admin, user_id)

            show_entries(admin, "Comp Hours", earliest(logs), employee=name)
            descs = [log["description"] for log in logs]
            tick(admin, *descs)
            expect_dock(admin, 2, approve=2, reject=2, delete=2)
            sent = run_bulk(admin, "Approve")
            assert sorted(sent) == sorted(log["id"] for log in logs), sent

            expect_toast(admin, approved_msg(2))
            expect(dock(admin)).to_have_count(0)
            for desc in descs:
                r = entry_row(admin, desc)
                expect(r.locator("span.rounded-full").last).to_have_text(BADGES["approved"])
                expect(approve_button(r)).to_have_count(0)
                expect(reject_button(r)).to_have_count(0)
            assert statuses(admin, prefix, employee_id=user_id) == {desc: "approved" for desc in descs}
            assert comp_balance(admin, user_id) == expected_after_approval(balance, leftover, 4)
        finally:
            cleanup_prefixed(admin, prefix)
            admin_browser.close()
            user_browser.close()
