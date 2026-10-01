from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_with_employees, select_policy,
    employees_count, employee_names, employees_section,
)


def test_employee_preview_limit():
    """LP-007: a policy with more than 12 employees previews 12 names and '+N more'."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        name = policy_with_employees(page, minimum=13)
        select_policy(page, name)
        total = employees_count(page)

        assert len(employee_names(page)) == 12
        expect(employees_section(page).get_by_text(f"+{total - 12} more")).to_be_visible()

        browser.close()
