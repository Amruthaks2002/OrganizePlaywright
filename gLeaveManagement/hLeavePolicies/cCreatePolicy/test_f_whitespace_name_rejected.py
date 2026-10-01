from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, open_create_form, name_input, expect_toast, policy_names,
)


def test_whitespace_name_rejected():
    """LP-020: a name made only of spaces is rejected."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        form = open_create_form(page)
        name_input(form).fill("   ")
        form.get_by_role("button", name="Create Policy").click()

        expect_toast(page, "The name field is required.")
        expect(form).to_be_visible()
        assert all(policy_names(page))

        browser.close()
