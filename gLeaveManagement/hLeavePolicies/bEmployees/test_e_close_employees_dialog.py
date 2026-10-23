from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_with_employees, select_policy,
    employees_section, employees_dialog, close_x,
)


def test_close_employees_dialog():
    """LP-012: the Employees dialog closes with the X button and with Escape."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        select_policy(page, policy_with_employees(page))
        view_all = employees_section(page).get_by_role("button", name="View all")

        view_all.click()
        expect(employees_dialog(page)).to_be_visible()
        close_x(employees_dialog(page)).click()
        expect(employees_dialog(page)).to_be_hidden()

        view_all.click()
        expect(employees_dialog(page)).to_be_visible()
        page.keyboard.press("Escape")
        expect(employees_dialog(page)).to_be_hidden()

        browser.close()
