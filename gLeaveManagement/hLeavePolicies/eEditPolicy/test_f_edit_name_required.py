from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    open_edit_form, name_input, policy_card, goto, POLICIES_URL,
)


def test_edit_name_required():
    """LP-037: the policy can't be updated with an empty name, and the old name is kept."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            form = open_edit_form(page, name)
            name_input(form).fill("")
            form.get_by_role("button", name="Update Policy").click()
            assert name_input(form).evaluate("e => e.validationMessage") != ""
            expect(form).to_be_visible()
            form.get_by_role("button", name="Cancel").click()
            expect(form).to_be_hidden()

            goto(page, POLICIES_URL)
            expect(policy_card(page, name)).to_have_count(1)
        finally:
            delete_policy(page, name)

        browser.close()
