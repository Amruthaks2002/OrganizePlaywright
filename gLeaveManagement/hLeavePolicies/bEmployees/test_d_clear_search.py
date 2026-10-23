from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_with_employees, select_policy, employees_count,
    employees_section, employees_dialog, employees_dialog_rows,
)


def test_clear_search():
    """LP-011: clearing the search brings back the full employee list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        select_policy(page, policy_with_employees(page))
        total = employees_count(page)
        employees_section(page).get_by_role("button", name="View all").click()
        dialog = employees_dialog(page)
        search = dialog.get_by_placeholder("Search employees...")

        search.fill("zzqx no such employee")
        expect(dialog.get_by_text("No matching employees found.")).to_be_visible()
        search.fill("")
        expect(employees_dialog_rows(page)).to_have_count(total)
        expect(dialog.get_by_text("No matching employees found.")).to_be_hidden()

        browser.close()
