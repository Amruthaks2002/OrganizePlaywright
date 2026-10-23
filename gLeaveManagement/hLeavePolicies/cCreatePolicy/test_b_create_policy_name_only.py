from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy, policy_card,
    card_status, card_employee_count, select_policy, detail_badges, detail_description,
    employees_count, employees_section,
)


def test_create_policy_name_only():
    """LP-016: a policy can be created with just a name and shows as Active with no employees."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            card = policy_card(page, name)
            expect(card_status(card)).to_have_text("Active")
            assert card_employee_count(card) == 0

            select_policy(page, name)
            expect(detail_badges(page)).to_have_text(["Active"])
            expect(detail_description(page)).to_have_text("No description provided.")
            assert employees_count(page) == 0
            expect(employees_section(page).get_by_text("No employees assigned yet.")).to_be_visible()
        finally:
            delete_policy(page, name)

        browser.close()
