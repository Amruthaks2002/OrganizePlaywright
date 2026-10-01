from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_with_employees, select_policy,
    employee_names, employees_section, profile_card, main_content,
)


def test_view_full_profile():
    """LP-014: 'View full profile' opens the employee's profile page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        select_policy(page, policy_with_employees(page))
        employee = employee_names(page)[0]
        employees_section(page).get_by_role("button", name=f"View {employee}'s profile").click()
        profile_card(page, employee).get_by_role("button", name="View full profile").click()

        page.wait_for_url("**/users/*/profile")
        expect(main_content(page).get_by_text(employee, exact=True).first).to_be_visible()

        browser.close()
