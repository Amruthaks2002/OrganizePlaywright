from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    open_edit_form, delete_dialog, expect_toast, policy_card,
)


def test_delete_from_edit_form():
    """LP-040: 'Delete Policy' in the Edit form asks for confirmation and deletes the policy.

    Known bug: the button just closes the Edit form; no confirmation appears and
    the policy is not deleted. This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            form = open_edit_form(page, name)
            form.get_by_role("button", name="Delete Policy").click()
            confirm = delete_dialog(page)
            expect(confirm, "Delete Policy in the Edit form should ask for confirmation").to_be_visible()
            confirm.get_by_role("button", name="Delete", exact=True).click()
            expect_toast(page, "Leave policy deleted successfully.")
            expect(policy_card(page, name)).to_have_count(0)
        finally:
            delete_policy(page, name)

        browser.close()
