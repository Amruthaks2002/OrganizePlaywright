from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_browser_as, approve_button, reject_button, BADGES
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, entry_row, bulk_api, me,
                                            NONE_REJECTED, NONE_APPROVED, comp_user_or_skip, open_comp_user, cleanup_prefixed)


def check_admin_sees_pending(admin, log, name):
    show_entries(admin, "Comp Hours", earliest([log]), employee=name)
    r = entry_row(admin, log["description"])
    expect(r.locator("span.rounded-full").last).to_have_text(BADGES["pending"])
    expect(approve_button(r)).to_be_visible()
    expect(reject_button(r)).to_be_visible()


def test_employee_reject_refused_admin_view():
    """WS-111: after an employee's direct bulk reject of their own entry is refused, the admin still sees it
    Pending with its Approve / Reject buttons."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            assert bulk_api(page, "reject", [log["id"]], json_errors=False) == (302, {"error": NONE_REJECTED})
            check_admin_sees_pending(admin, log, me(page)["name"])
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()


def test_employee_approve_refused_admin_view():
    """WS-111: after an employee's direct bulk approve of their own entry is refused, the admin still sees it
    Pending. Runs as the throwaway comp user (WS_COMP_USER_EMAIL / WS_COMP_USER_PASSWORD) in case the server
    approves it anyway; skips when unset."""
    credentials = comp_user_or_skip()  # before Playwright starts
    with sync_playwright() as p:
        browser, page = open_comp_user(p, credentials)
        admin_browser, admin = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            assert bulk_api(page, "approve", [log["id"]], json_errors=False) == (302, {"error": NONE_APPROVED})
            check_admin_sees_pending(admin, log, me(page)["name"])
        finally:
            cleanup_prefixed(admin, prefix)
            admin_browser.close()
            browser.close()
