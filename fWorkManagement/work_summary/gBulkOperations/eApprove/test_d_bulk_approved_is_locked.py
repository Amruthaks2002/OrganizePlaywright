from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, edit_button
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, tick, bulk_api,
                                            expect_dock, me, statuses, approved_msg, NONE_DELETED, comp_user_or_skip, open_comp_user,
                                            cleanup_prefixed)


def test_bulk_approved_is_locked():
    """WS-082: an entry approved in bulk is locked like a single approval: no Edit, ticking it offers
    Approve (0) / Reject (0) / Delete (0), and a bulk delete of it is refused.

    Throwaway comp user only (WS_COMP_USER_EMAIL / WS_COMP_USER_PASSWORD); skips when unset."""
    credentials = comp_user_or_skip()  # before Playwright starts
    with sync_playwright() as p:
        user_browser, user = open_comp_user(p, credentials)
        admin_browser, admin = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(user, prefix, 1)
            name = me(user)["name"]
            assert bulk_api(admin, "approve", [log["id"]], json_errors=False) == (302, {"success": approved_msg(1)})

            show_entries(admin, "Comp Hours", earliest([log]), employee=name)
            r = entry_row(admin, log["description"])
            expect(edit_button(r)).to_have_count(0)
            tick(admin, log["description"])
            expect_dock(admin, 1, approve=0, reject=0, delete=0)

            assert bulk_api(admin, "delete", [log["id"]], json_errors=False) == (302, {"error": NONE_DELETED})
            assert statuses(admin, prefix, employee_id=log["user_id"]) == {log["description"]: "approved"}
        finally:
            cleanup_prefixed(admin, prefix)
            admin_browser.close()
            user_browser.close()
