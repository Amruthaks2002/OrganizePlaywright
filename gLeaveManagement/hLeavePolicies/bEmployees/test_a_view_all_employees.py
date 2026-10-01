from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_with_employees, select_policy, employees_count,
    employees_section, employees_dialog, employees_dialog_rows,
)


def test_view_all_employees():
    """LP-008: 'View all' lists every employee of the policy with name and email."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        name = policy_with_employees(page, minimum=13)
        select_policy(page, name)
        total = employees_count(page)

        employees_section(page).get_by_role("button", name="View all").click()
        dialog = employees_dialog(page)
        expect(dialog.locator("h3")).to_have_text(f"Employees — {name}")
        expect(employees_dialog_rows(page)).to_have_count(total)
        for row in employees_dialog_rows(page).all()[:5]:
            expect(row.locator("p.truncate")).not_to_be_empty()
            expect(row.locator("p").last).to_contain_text("@")

        browser.close()
