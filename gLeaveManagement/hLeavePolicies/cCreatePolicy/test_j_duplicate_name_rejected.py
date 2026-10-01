from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy, open_create_form,
    name_input, expect_toast, policy_card,
)


def test_duplicate_name_rejected():
    """LP-024: creating a policy with an existing name is rejected."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            form = open_create_form(page)
            name_input(form).fill(name)
            form.get_by_role("button", name="Create Policy").click()

            expect_toast(page, "The name has already been taken.")
            expect(form).to_be_visible()
            expect(policy_card(page, name)).to_have_count(1)
        finally:
            delete_policy(page, name)

        browser.close()
