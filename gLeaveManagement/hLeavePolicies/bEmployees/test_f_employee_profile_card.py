from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_with_employees, select_policy,
    employee_names, employees_section, profile_card,
)


def test_employee_profile_card():
    """LP-013: clicking an employee opens their profile card, which closes with X."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        select_policy(page, policy_with_employees(page))
        employee = employee_names(page)[0]
        employees_section(page).get_by_role("button", name=f"View {employee}'s profile").click()

        card = profile_card(page, employee)
        expect(card).to_be_visible()
        expect(card.get_by_text(employee, exact=True)).to_be_visible()
        expect(card.get_by_text("Joined")).to_be_visible()
        expect(card.get_by_role("button", name="View full profile")).to_be_visible()

        card.get_by_role("button", name="Close").click()
        expect(card).to_be_hidden()

        browser.close()
