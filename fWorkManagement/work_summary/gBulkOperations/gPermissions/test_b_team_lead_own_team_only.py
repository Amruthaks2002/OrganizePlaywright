from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_browser_as, expect_toast
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, tick, run_bulk, bulk_api, me,
                                            expect_dock, statuses, rejected_msg, NONE_DELETED, NONE_REJECTED,
                                            cleanup_prefixed)


def test_team_lead_own_team_only():
    """WS-092: the team lead can reject their team member's (the employee quick login's) entries but not delete
    them, and can't reject the admin's entry - who isn't in their team - even by sending the request directly."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        employee_browser, employee = open_browser_as(p, "employee")
        browser, lead = open_browser_as(p, "team-lead")
        prefix = bulk_prefix()
        try:
            [admin_log] = create_logs(admin, prefix, 1)
            [team_log] = create_logs(employee, prefix, 1, start_index=2)

            assert bulk_api(lead, "reject", [admin_log["id"]], json_errors=False) == (302, {"error": NONE_REJECTED})
            assert bulk_api(lead, "delete", [team_log["id"]], json_errors=False) == (302, {"error": NONE_DELETED})
            assert statuses(admin, prefix) == {admin_log["description"]: "pending", team_log["description"]: "pending"}

            show_entries(lead, "Comp Hours", earliest([team_log]), employee=me(employee)["name"])
            tick(lead, team_log["description"])
            expect_dock(lead, 1, approve=1, reject=1, delete=0)
            assert run_bulk(lead, "Reject") == [team_log["id"]]
            expect_toast(lead, rejected_msg(1))
            assert statuses(admin, prefix) == {admin_log["description"]: "pending", team_log["description"]: "rejected"}
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            employee_browser.close()
            admin_browser.close()
