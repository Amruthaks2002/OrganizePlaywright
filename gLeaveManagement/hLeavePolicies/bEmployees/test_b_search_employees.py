from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_with_employees, select_policy, employees_count,
    employee_names, employees_section, employees_dialog, employees_dialog_rows, employees_dialog_names,
)


def test_search_employees():
    """LP-009: searching by part of a name narrows the employee list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        name = policy_with_employees(page, minimum=13)
        select_policy(page, name)
        total = employees_count(page)
        employee = employee_names(page)[0]
        term = employee.split()[0]

        employees_section(page).get_by_role("button", name="View all").click()
        employees_dialog(page).get_by_placeholder("Search employees...").fill(term)

        expect(employees_dialog_rows(page).filter(has_text=employee).first).to_be_visible()
        names = employees_dialog_names(page)
        assert 0 < len(names) < total
        assert all(term.lower() in n.lower() for n in names), names

        browser.close()
