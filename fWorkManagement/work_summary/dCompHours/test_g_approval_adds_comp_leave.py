import pytest
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_browser_with_login, comp_user_credentials, open_hours, open_tab,
                                       page_props, pick_employee, wait_for_logs, from_date, summary_card, card_number,
                                       comp_balance, expected_after_approval, log_comp_hours, approve_in_ui,
                                       find_logs, cleanup_unapproved, unique_desc, COMP_USER_ENV, COMP_SEARCH_DAYS,
                                       ADMIN_ID, EMPLOYEE_ID)

# (approved hours, comp-off days they must add when nothing is left over from before)
CASES = [(4, 0.5), (8, 1.0)]
CARRY_OVER_HOURS = 3


def test_approval_adds_comp_leave():
    """WS-049: approving compensatory hours adds comp-off leave to the employee - 4 approved hours add half
    a day and 8 add a full day, leaving any earlier unconverted hours as they were. Hours that don't make a
    full half day (3h) carry over: they're added to the unconverted hours, and each 4 of those become half
    a day.

    Approving can't be undone, so this runs as a dedicated throwaway user (WS_COMP_USER_EMAIL /
    WS_COMP_USER_PASSWORD) whose balance grows by 1.5 days + 3 hours on every run; the test only compares
    before and after."""
    credentials = comp_user_credentials()
    if not credentials:
        pytest.skip(f"set {' / '.join(COMP_USER_ENV)} to a throwaway user who can log hours - "
                    "approving comp hours permanently changes their leave balance")

    with sync_playwright() as p:
        user_browser, user = open_browser_with_login(p, *credentials)
        admin_browser, admin = open_browser(p)
        desc = unique_desc("comp leave")
        open_hours(user)
        me = page_props(user)["auth"]["user"]
        # never the shared admin / quick-login employee: their balances are used elsewhere
        assert me["id"] not in (ADMIN_ID, EMPLOYEE_ID), f"{me['name']} isn't a throwaway user"
        weekends = page_props(user)["weekends"]
        project = page_props(user)["assignableProjects"][0]["name"]
        try:
            for hours, days_added in CASES + [(CARRY_OVER_HOURS, None)]:
                tag = f"{desc} {hours}h"
                balance, leftover = comp_balance(admin, me["id"])
                day = log_comp_hours(user, tag, hours, project, weekends)
                [log] = find_logs(admin, tag, days=COMP_SEARCH_DAYS, employee_id=me["id"])
                assert log["comp_off_status"] == "pending", log

                approve_in_ui(admin, tag, day, me["name"])
                [log] = find_logs(admin, tag, days=COMP_SEARCH_DAYS, employee_id=me["id"])
                assert log["comp_off_status"] == "approved" and log["approved_by"]["id"] == ADMIN_ID, log

                after = comp_balance(admin, me["id"])
                # the summary figures are the employee's stored balance, not a recount
                [log] = find_logs(admin, tag, days=COMP_SEARCH_DAYS, employee_id=me["id"])
                assert (float(log["user"]["comp_off_balance"]), float(log["user"]["comp_off_hours"])) == after, log["user"]
                assert after == expected_after_approval(balance, leftover, hours), \
                    f"{hours}h approved: balance {balance} days + {leftover}h left over -> {after}"
                if days_added is not None:
                    assert (after[0] - balance, after[1]) == (days_added, leftover), \
                        f"{hours}h approved should add {days_added} day(s): {balance} -> {after[0]} days, " \
                        f"left over {leftover}h -> {after[1]}h"

            # the summary cards show the new balance too
            open_hours(admin)
            open_tab(admin, "Comp Hours")
            wait_for_logs(admin, lambda: pick_employee(admin, me["name"]))
            balance, leftover = comp_balance(admin, me["id"])
            assert card_number(summary_card(admin, "Leave Balance")) == balance
            assert card_number(summary_card(admin, "Convertible Balance")) == leftover
        finally:
            for hours, _ in CASES + [(CARRY_OVER_HOURS, None)]:
                cleanup_unapproved(admin, f"{desc} {hours}h", me["id"])
            admin_browser.close()
            user_browser.close()
