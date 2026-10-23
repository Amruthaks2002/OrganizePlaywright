from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_with_employees, select_policy,
    employees_section, employees_dialog, employees_dialog_names,
)


def test_search_no_match():
    """LP-010: a search with no match shows the empty message."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        select_policy(page, policy_with_employees(page))
        employees_section(page).get_by_role("button", name="View all").click()
        dialog = employees_dialog(page)
        dialog.get_by_placeholder("Search employees...").fill("zzqx no such employee")

        expect(dialog.get_by_text("No matching employees found.")).to_be_visible()
        assert employees_dialog_names(page) == []

        browser.close()
